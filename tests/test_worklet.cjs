const { test } = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const path = require("node:path");
const code = fs.readFileSync(
  path.join(__dirname, "../src/lecturebridge/web/pcm-worklet.js"),
  "utf8",
);

for (const rate of [16000, 44100, 48000]) {
  test(`PCM worklet preserves 1 second at ${rate} Hz and flushes its tail`, () => {
    const messages = [];
    let Recorder;
    const context = vm.createContext({
      sampleRate: rate,
      AudioWorkletProcessor: class {
        constructor() {
          this.port = { postMessage: (msg) => messages.push(msg) };
        }
      },
      registerProcessor: (_name, cls) => {
        Recorder = cls;
      },
    });
    vm.runInContext(code, context);
    const recorder = new Recorder();
    for (let offset = 0; offset < rate; offset += 128)
      recorder.process([
        [new Float32Array(Math.min(128, rate - offset)).fill(0.5)],
      ]);
    recorder.port.onmessage({ data: "stop" });
    const frames = messages
      .filter((msg) => msg.type === "pcm")
      .map((msg) => new Int16Array(msg.buffer));
    assert.equal(
      frames.reduce((n, frame) => n + frame.length, 0),
      16000,
    );
    assert.ok(
      frames.every((frame) =>
        [...frame].every((value) => Math.abs(value - 16384) <= 1),
      ),
    );
    assert.equal(messages.at(-1).type, "flushed");
    assert.equal(recorder.process([[new Float32Array(128)]]), false);
  });
}
