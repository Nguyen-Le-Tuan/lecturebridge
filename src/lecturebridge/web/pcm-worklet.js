/* Streaming box-filter resampler: bounded memory at every input sample rate. */
class PCMRecorder extends AudioWorkletProcessor {
  constructor() {
    super();
    this.ratio = sampleRate / 16000;
    this.weight = 0;
    this.sum = 0;
    this.count = 0;
    this.energy = 0;
    this.buffer = new Int16Array(4000);
    this.stopped = false;
    this.port.onmessage = ({ data }) => {
      if (data === "stop") {
        this.stopped = true;
        this.flush();
        this.port.postMessage({ type: "flushed" });
      }
    };
  }
  flush() {
    if (!this.count) return;
    const pcm = this.buffer.slice(0, this.count);
    this.port.postMessage(
      {
        type: "pcm",
        buffer: pcm.buffer,
        level: Math.min(1, Math.sqrt(this.energy / this.count) * 4),
      },
      [pcm.buffer],
    );
    this.count = 0;
    this.energy = 0;
  }
  process(inputs) {
    if (this.stopped) return false;
    const channels = inputs[0];
    if (!channels?.[0]) return true;
    for (let i = 0; i < channels[0].length; i++) {
      let value = 0;
      for (const channel of channels) value += channel[i] / channels.length;
      let remaining = 1;
      while (remaining > 1e-8) {
        const used = Math.min(remaining, this.ratio - this.weight);
        this.sum += value * used;
        this.weight += used;
        remaining -= used;
        if (this.weight >= this.ratio - 1e-8) {
          const sample = Math.max(-1, Math.min(1, this.sum / this.ratio));
          this.buffer[this.count++] = Math.round(
            sample * (sample < 0 ? 32768 : 32767),
          );
          this.energy += sample * sample;
          this.weight = 0;
          this.sum = 0;
          if (this.count === this.buffer.length) this.flush();
        }
      }
    }
    return true;
  }
}
registerProcessor("lecturebridge-pcm", PCMRecorder);
