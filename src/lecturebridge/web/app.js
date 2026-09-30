const $ = (id) => document.getElementById(id);
const preferences = {
  get(key, fallback) {
    try {
      return localStorage.getItem(`lb-${key}`) || fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    try {
      localStorage.setItem(`lb-${key}`, value);
    } catch {
      /* private browsing */
    }
  },
};
let mode = "en",
  segments = [],
  phase = "idle",
  socket,
  stream,
  context,
  worklet,
  source,
  silent;
let secondsElapsed = 0,
  startedAt = 0,
  timer,
  stopTimer,
  flushResolve,
  wakeLock;
let follow = true,
  currentRecording = null,
  savedId = null,
  translationState = "idle",
  toastTimer;
let capabilities = {},
  selectedInput = "",
  finishReceived = false,
  downloadedPrompt = false;
let fontSize = Math.max(
  18,
  Math.min(32, Number(preferences.get("font", "22")) || 22),
);
const mediaTheme = matchMedia("(prefers-color-scheme: dark)");
function applyTheme() {
  const theme = $("themeSelect").value;
  document.documentElement.dataset.theme =
    theme === "system" ? (mediaTheme.matches ? "dark" : "light") : theme;
  preferences.set("theme", theme);
}
$("themeSelect").value = preferences.get("theme", "system");
applyTheme();
mediaTheme.addEventListener("change", applyTheme);
$("themeSelect").addEventListener("change", applyTheme);
function setFont(value) {
  fontSize = Math.max(18, Math.min(32, value));
  document.documentElement.style.setProperty("--reading", `${fontSize}px`);
  preferences.set("font", fontSize);
}
setFont(fontSize);
$("smallerText").onclick = () => setFont(fontSize - 2);
$("largerText").onclick = () => setFont(fontSize + 2);
$("today").textContent = new Intl.DateTimeFormat("vi-VN", {
  weekday: "short",
  day: "numeric",
  month: "long",
}).format(new Date());
const clock = (seconds) =>
  `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
const sizeLabel = (bytes) => `${(bytes / 1024 / 1024).toFixed(1)} MB`;
function toast(text) {
  clearTimeout(toastTimer);
  $("toast").textContent = text;
  $("toast").hidden = false;
  toastTimer = setTimeout(() => {
    $("toast").hidden = true;
  }, 5000);
}
function message(text) {
  $("sessionMessage").textContent = text;
  $("sessionMessage").hidden = !text;
}
async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok)
    throw new Error(`Không thể thực hiện yêu cầu (${response.status}).`);
  return response.json();
}
function showView(view) {
  const live = view === "live";
  $("liveView").hidden = !live;
  $("libraryView").hidden = live;
  $("liveNav").classList.toggle("selected", live);
  $("libraryNav").classList.toggle("selected", !live);
  $("liveNav").toggleAttribute("aria-current", live);
  $("libraryNav").toggleAttribute("aria-current", !live);
  $("pageCrumb").textContent = live ? "Trực tiếp" : "Thư viện";
  if (!live) refreshLibrary();
}
$("liveNav").onclick = () => showView("live");
$("libraryNav").onclick = () => showView("library");
$("newSession").onclick = () => showView("live");
$("refreshLibrary").onclick = () => refreshLibrary();
function openSettings() {
  $("settingsDialog").showModal();
  refreshDevices();
}
$("settingsButton").onclick = openSettings;
$("mobileSettings").onclick = openSettings;
$("closeSettings").onclick = () => $("settingsDialog").close();
$("microphoneSelect").onchange = () => {
  selectedInput = $("microphoneSelect").value;
};
async function refreshDevices() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const list = $("microphoneSelect");
    list.replaceChildren(new Option("Mặc định của thiết bị", ""));
    for (const device of devices.filter(
      (d) => d.kind === "audioinput" && d.label,
    ))
      list.add(new Option(device.label, device.deviceId));
    list.value = selectedInput;
  } catch {
    /* Permission has not been granted yet. */
  }
}
$("saveRecording").onchange = () => {
  $("consentNote").hidden = !$("saveRecording").checked;
};
function setPhase(value, text) {
  phase = value;
  $("sessionStatus").textContent = text;
  const active = value === "listening";
  $("statusDot").classList.toggle("active", active);
  $("startStop").classList.toggle("recording", active);
  $("startStop").textContent = active
    ? "■  Dừng phiên"
    : value === "starting"
      ? "Đang chuẩn bị…"
      : value === "stopping"
        ? "Đang hoàn tất…"
        : "●  Bắt đầu nghe";
  $("startStop").disabled = ["starting", "stopping"].includes(value);
  for (const id of ["saveRecording", "sessionTitle", "microphoneSelect"])
    $(id).disabled = value !== "idle";
}
function updateTranslationNotice() {
  const texts = {
    idle: "Bản dịch sẽ bắt đầu với phần nói mới khi bạn bắt đầu phiên.",
    loading:
      "Đang chuẩn bị bộ dịch trên CPU. Transcript tiếng Anh vẫn tiếp tục.",
    downloading: "Đang tải bộ dịch. Bạn vẫn có thể đọc transcript tiếng Anh.",
    missing: `Cần tải bộ dịch local (~${((capabilities.translation?.download_bytes || 2500000000) / 1e9).toFixed(1)} GB). NLLB chỉ dành cho mục đích phi thương mại.`,
    ready:
      "Dịch phần nói mới · CPU local. Các đoạn trước khi bật dịch được giữ bằng tiếng Anh.",
    error:
      "Bộ dịch chưa hoạt động. Transcript tiếng Anh vẫn tiếp tục; thử lại bằng nút chế độ đọc.",
    off: "Bộ dịch đang tắt.",
  };
  $("translationNotice").hidden = mode === "en";
  $("translationText").textContent = texts[translationState] || texts.idle;
  $("downloadTranslation").hidden = !["missing", "error"].includes(
    translationState,
  );
  $("downloadTranslation").textContent =
    translationState === "error" ? "Chuẩn bị lại bộ dịch" : "Tải bộ dịch";
}
for (const button of document.querySelectorAll("[data-mode]"))
  button.onclick = () => {
    const wasEnabled = mode !== "en";
    mode = button.dataset.mode;
    for (const item of document.querySelectorAll("[data-mode]"))
      item.setAttribute("aria-pressed", String(item === button));
    if (
      phase === "listening" &&
      (wasEnabled !== (mode !== "en") || translationState === "error")
    ) {
      socket.send(
        JSON.stringify({ type: "translation", enabled: mode !== "en" }),
      );
      translationState = mode === "en" ? "off" : "loading";
    }
    updateTranslationNotice();
    renderTranscript();
  };
$("downloadTranslation").onclick = async () => {
  try {
    await api("/api/translation/prepare", {
      method: "POST",
      body: JSON.stringify({ download: true }),
    });
    translationState = "downloading";
    downloadedPrompt = true;
    updateTranslationNotice();
  } catch (error) {
    toast(error.message);
  }
};
function lineNode(segment, playback = false) {
  const line = document.createElement("div");
  line.className = "transcript-line";
  line.dataset.id = segment.id;
  const timestamp = document.createElement(playback ? "button" : "span");
  timestamp.className = "transcript-time";
  timestamp.textContent = clock(segment.start);
  if (playback) {
    timestamp.title = `Nghe từ ${clock(segment.start)}`;
    timestamp.onclick = () => {
      $("audioPlayer").currentTime = segment.start;
      $("audioPlayer")
        .play()
        .catch(() => toast("Bấm phát trên thanh audio để nghe."));
    };
  }
  const copy = document.createElement("div");
  copy.className = "transcript-copy";
  const add = (text, className = "") => {
    const p = document.createElement("p");
    p.textContent = text;
    p.className = className;
    copy.append(p);
  };
  if (playback || mode !== "vi" || !segment.translation) add(segment.text);
  if ((playback || mode !== "en") && segment.translation)
    add(segment.translation, "translation");
  else if (!playback && mode !== "en") {
    const labels = {
      pending: "Đang chờ bản dịch…",
      off: "Chưa dịch · đoạn trước khi bật dịch",
      skipped: "Chưa dịch · bộ dịch đang bận",
      error: "Chưa dịch · bộ dịch gặp lỗi",
      unavailable: "Chưa dịch · cần chuẩn bị bộ dịch",
    };
    add(labels[segment.translation_status] || "Chưa dịch", "untranslated");
  }
  line.append(timestamp, copy);
  return line;
}
function renderTranscript() {
  $("transcriptLines").replaceChildren(
    ...segments.map((segment) => lineNode(segment)),
  );
  $("emptyState").hidden =
    segments.length > 0 || !!$("partialText").textContent;
  $("exportLive").disabled = !segments.length;
  if (follow) $("readerScroll").scrollTop = $("readerScroll").scrollHeight;
}
$("readerScroll").addEventListener("scroll", () => {
  const el = $("readerScroll");
  follow = el.scrollHeight - el.scrollTop - el.clientHeight < 65;
  $("followLatest").hidden = follow || !segments.length;
});
$("followLatest").onclick = () => {
  follow = true;
  $("readerScroll").scrollTop = $("readerScroll").scrollHeight;
  $("followLatest").hidden = true;
};
function downloadBlob(content, type, name) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}
$("exportLive").onclick = () =>
  downloadBlob(
    segments
      .map(
        (s) =>
          `[${clock(s.start)}] ${s.text}${s.translation ? `\n${s.translation}` : ""}`,
      )
      .join("\n\n"),
    "text/plain;charset=utf-8",
    "lecturebridge-transcript.txt",
  );
async function releaseAudio(flush = false) {
  if (worklet && flush)
    await new Promise((resolve) => {
      flushResolve = resolve;
      worklet.port.postMessage("stop");
      setTimeout(resolve, 750);
    });
  worklet?.disconnect();
  source?.disconnect();
  silent?.disconnect();
  stream?.getTracks().forEach((track) => {
    track.onended = null;
    track.stop();
  });
  if (context && context.state !== "closed")
    await context.close().catch(() => {});
  stream = context = worklet = source = silent = null;
  flushResolve = null;
  if (wakeLock) await wakeLock.release().catch(() => {});
  wakeLock = null;
  $("micLevel").value = 0;
}
async function start() {
  if (
    segments.length &&
    !savedId &&
    !confirm(
      "Phiên trước chưa được lưu. Hãy tải transcript nếu cần trước khi bắt đầu phiên mới. Tiếp tục?",
    )
  )
    return;
  setPhase("starting", "Đang xin quyền microphone");
  message("");
  savedId = null;
  finishReceived = false;
  try {
    if (!navigator.mediaDevices?.getUserMedia)
      throw new Error("Microphone cần localhost hoặc URL Tailscale HTTPS.");
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        ...(selectedInput ? { deviceId: { exact: selectedInput } } : {}),
      },
      video: false,
    });
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    context = new AudioContextClass();
    await context.resume();
    await context.audioWorklet.addModule("/assets/pcm-worklet.js");
    source = context.createMediaStreamSource(stream);
    worklet = new AudioWorkletNode(context, "lecturebridge-pcm");
    silent = context.createGain();
    silent.gain.value = 0;
    // Connect only after the server acknowledges this session.
    worklet.port.onmessage = ({ data }) => {
      if (data.type === "flushed") {
        flushResolve?.();
        return;
      }
      if (data.type === "pcm" && socket?.readyState === WebSocket.OPEN) {
        if (socket.bufferedAmount > 128000) {
          fail("Kết nối quá chậm. Phiên đã dừng để tránh tích lũy audio.");
          return;
        }
        socket.send(data.buffer);
        $("micLevel").value = data.level;
      }
    };
    socket = new WebSocket(
      `${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/api/live`,
    );
    socket.binaryType = "arraybuffer";
    const connecting = setTimeout(
      () => fail("Không kết nối được máy chủ. Kiểm tra laptop và Tailscale."),
      15000,
    );
    socket.onopen = () =>
      socket.send(
        JSON.stringify({
          type: "start",
          save: $("saveRecording").checked,
          title: $("sessionTitle").value.trim() || "Bài giảng mới",
          translation: mode !== "en",
        }),
      );
    socket.onmessage = ({ data }) => {
      const event = JSON.parse(data);
      if (event.type === "config") {
        clearTimeout(connecting);
        segments = [];
        $("partialText").textContent = "";
        renderTranscript();
        savedId = event.recording_id;
        secondsElapsed = 0;
        startedAt = Date.now();
        $("timer").textContent = "00:00";
        source.connect(worklet);
        worklet.connect(silent);
        silent.connect(context.destination);
        stream.getAudioTracks().forEach((track) => {
          track.onended = () =>
            stop("Microphone đã ngắt. Đang lưu phần đã nhận.");
        });
        setPhase("listening", "Đang lắng nghe");
        $("recordingStatus").textContent = savedId
          ? "Đang lưu bản ghi trên laptop"
          : "Chỉ xử lý trực tiếp · Không lưu audio";
        timer = setInterval(() => {
          secondsElapsed = (Date.now() - startedAt) / 1000;
          $("timer").textContent = clock(secondsElapsed);
          if (secondsElapsed >= 7200)
            stop("Đã đạt giới hạn 2 giờ của một phiên.");
        }, 1000);
        navigator.wakeLock
          ?.request("screen")
          .then((lock) => {
            if (phase === "listening") wakeLock = lock;
            else lock.release();
          })
          .catch(() => {});
        refreshDevices();
      } else if (event.type === "transcript") {
        segments = event.segments;
        renderTranscript();
      } else if (event.type === "partial") {
        $("partialText").textContent = event.text;
        $("emptyState").hidden = segments.length > 0 || !!event.text;
        $("lagLabel").textContent =
          event.lag > 0
            ? `Độ trễ xử lý ~${event.lag.toFixed(1)} giây`
            : "Đang theo kịp âm thanh";
        if (follow)
          $("readerScroll").scrollTop = $("readerScroll").scrollHeight;
      } else if (event.type === "translation_state") {
        translationState = event.state;
        updateTranslationNotice();
      } else if (event.type === "recording_error") {
        message(event.message);
        $("recordingStatus").textContent = "Lưu bản ghi bị gián đoạn";
      } else if (event.type === "error") {
        clearTimeout(connecting);
        fail(event.message);
      } else if (event.type === "ready_to_stop") {
        clearTimeout(connecting);
        finishReceived = true;
        finish(event.recording_id, event.recording_interrupted);
      }
    };
    socket.onclose = () => {
      clearTimeout(connecting);
      if (!finishReceived && phase !== "idle")
        fail(
          "Kết nối đã ngắt. Phần audio đến được laptop được giữ nếu bạn bật lưu; mở Thư viện để kiểm tra.",
        );
    };
    socket.onerror = () => {
      clearTimeout(connecting);
      if (phase !== "idle")
        fail("Không kết nối được máy chủ. Kiểm tra laptop và Tailscale.");
    };
  } catch (error) {
    const text =
      error.name === "NotAllowedError"
        ? "Microphone chưa được cho phép. Cho phép trong cài đặt trình duyệt rồi thử lại."
        : error.name === "NotFoundError"
          ? "Không tìm thấy microphone."
          : error.message;
    await fail(text);
  }
}
async function stop(note = "") {
  if (phase !== "listening") return;
  setPhase("stopping", "Đang hoàn tất transcript");
  clearInterval(timer);
  if (note) message(note);
  await releaseAudio(true);
  if (socket?.readyState === WebSocket.OPEN)
    socket.send(JSON.stringify({ type: "stop" }));
  stopTimer = setTimeout(
    () =>
      fail(
        "Hoàn tất quá lâu. Bản ghi đã nhận được giữ trên laptop; kiểm tra Thư viện.",
      ),
    35000,
  );
}
async function finish(recordingId, interrupted = false) {
  clearInterval(timer);
  clearTimeout(stopTimer);
  await releaseAudio();
  savedId = recordingId;
  if (socket) {
    socket.onclose = socket.onerror = null;
    socket.close();
  }
  setPhase("idle", "Phiên học đã hoàn tất");
  $("partialText").textContent = "";
  $("recordingStatus").textContent = recordingId
    ? "Đã lưu trong Thư viện"
    : "Không lưu audio · Có thể tải transcript";
  $("saveRecording").checked = false;
  $("consentNote").hidden = true;
  if (recordingId)
    message(
      "Bản ghi đã có trong Thư viện. Bạn có thể nghe lại, tải xuống hoặc xóa.",
    );
  if (interrupted) {
    message(
      "Bản ghi chỉ lưu được một phần do lỗi lưu trữ. Kiểm tra Thư viện và dung lượng laptop.",
    );
    $("recordingStatus").textContent = "Bản ghi bị gián đoạn";
  }
  refreshLibrary(false);
}
async function fail(text) {
  if (phase === "idle") return;
  setPhase("stopping", "Đang dừng phiên");
  clearInterval(timer);
  clearTimeout(stopTimer);
  finishReceived = true;
  if (socket) {
    socket.onclose = socket.onerror = null;
    socket.close();
  }
  await releaseAudio();
  setPhase("idle", "Phiên đã gián đoạn");
  $("saveRecording").checked = false;
  $("consentNote").hidden = true;
  message(text);
  $("recordingStatus").textContent = "Microphone đang tắt";
}
$("startStop").onclick = () => (phase === "listening" ? stop() : start());
window.addEventListener("beforeunload", (event) => {
  if (phase !== "idle") {
    event.preventDefault();
    event.returnValue = "";
  }
});
async function refreshLibrary(showError = true) {
  try {
    const recordings = await api("/api/recordings");
    $("libraryCount").textContent = recordings.length;
    $("librarySummary").textContent =
      `${recordings.length} bản ghi · ${sizeLabel(recordings.reduce((n, r) => n + r.bytes, 0))}`;
    $("libraryEmpty").hidden = recordings.length > 0;
    $("recordingList").replaceChildren(
      ...recordings.map((recording) => {
        const card = document.createElement("button");
        card.className = "recording-card";
        const icon = document.createElement("span");
        icon.className = "record-icon";
        icon.textContent = "▷";
        icon.setAttribute("aria-hidden", "true");
        const info = document.createElement("span");
        const name = document.createElement("strong");
        name.textContent = recording.title;
        const date = document.createElement("small");
        date.textContent = new Date(recording.created).toLocaleString("vi-VN", {
          dateStyle: "medium",
          timeStyle: "short",
        });
        info.append(name, date);
        const meta = document.createElement("span");
        meta.className = "record-meta";
        const status = {
          complete: "Đã lưu",
          interrupted: "Gián đoạn",
          recording: "Đang ghi",
        }[recording.status];
        meta.textContent = `${clock(recording.duration)} · ${status}`;
        card.append(icon, info, meta);
        card.onclick = () =>
          recording.status === "recording"
            ? toast("Dừng phiên trước khi nghe lại.")
            : openRecording(recording.id);
        return card;
      }),
    );
  } catch (error) {
    if (showError) toast(error.message);
  }
}
async function openRecording(id) {
  try {
    currentRecording = await api(`/api/recordings/${id}`);
    $("recordingDetail").hidden = false;
    $("detailTitle").textContent = currentRecording.title;
    $("audioPlayer").src = `/api/recordings/${id}/audio`;
    $("downloadAudio").href = `/api/recordings/${id}/audio?download=true`;
    $("downloadTxt").href = `/api/recordings/${id}/export?format=txt`;
    $("downloadJson").href = `/api/recordings/${id}/export?format=json`;
    $("detailTranscript").replaceChildren(
      ...currentRecording.segments.map((segment) => lineNode(segment, true)),
    );
    if (!currentRecording.segments.length)
      $("detailTranscript").textContent =
        "Phiên này chưa có transcript đã chốt.";
    $("recordingDetail").scrollIntoView({ block: "start", behavior: "auto" });
  } catch (error) {
    toast(error.message);
  }
}
$("audioPlayer").onerror = () =>
  toast("Không phát được audio. Thử tải WAV hoặc kiểm tra file trên laptop.");
$("closeDetail").onclick = () => {
  $("audioPlayer").pause();
  $("recordingDetail").hidden = true;
};
$("renameRecording").onclick = () => {
  $("editTitle").value = currentRecording.title;
  $("editDialog").showModal();
};
$("cancelEdit").onclick = () => $("editDialog").close();
$("editForm").onsubmit = async (event) => {
  event.preventDefault();
  try {
    currentRecording = await api(`/api/recordings/${currentRecording.id}`, {
      method: "PATCH",
      body: JSON.stringify({ title: $("editTitle").value.trim() }),
    });
    $("detailTitle").textContent = currentRecording.title;
    $("editDialog").close();
    refreshLibrary();
  } catch (error) {
    toast(error.message);
  }
};
$("deleteRecording").onclick = () => $("deleteDialog").showModal();
$("cancelDelete").onclick = () => $("deleteDialog").close();
$("confirmDelete").onclick = async () => {
  try {
    await api(`/api/recordings/${currentRecording.id}`, { method: "DELETE" });
    $("audioPlayer").pause();
    $("audioPlayer").removeAttribute("src");
    $("audioPlayer").load();
    $("recordingDetail").hidden = true;
    $("deleteDialog").close();
    currentRecording = null;
    refreshLibrary();
    toast("Đã xóa bản ghi và transcript.");
  } catch (error) {
    toast(error.message);
  }
};
async function checkCapabilities() {
  try {
    capabilities = await api("/api/capabilities");
    $("modelInfo").textContent =
      `ASR: ${capabilities.model} · Dịch: CPU · Thư viện: laptop · Phiên tối đa 2 giờ`;
    if (
      downloadedPrompt &&
      !["loading", "downloading"].includes(capabilities.translation.state)
    ) {
      downloadedPrompt = false;
      translationState = capabilities.translation.state;
      updateTranslationNotice();
      if (
        translationState === "ready" &&
        phase === "listening" &&
        mode !== "en"
      )
        socket.send(JSON.stringify({ type: "translation", enabled: true }));
    }
  } catch {
    /* Live connection owns its own error UI. */
  }
}
checkCapabilities().then(() => {
  if (capabilities.translation_default)
    document.querySelector('[data-mode="both"]').click();
});
setInterval(() => {
  if (downloadedPrompt) checkCapabilities();
}, 2000);
refreshLibrary(false);
