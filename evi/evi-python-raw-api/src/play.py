# parse_and_merge_audio_outputs.py
import base64
import io
import re
import wave
from pathlib import Path
from collections import defaultdict

LOG_FILE = "data.txt"
SAVE_EACH_CHUNK = False  # flip to True to save chunk_XXXX.wav files too

# Regexes that work for both JSON and Python-dict-looking logs
RE_AUDIO_OUTPUT = re.compile(r'audio_output')
RE_ID    = re.compile(r"""['"]id['"]\s*:\s*['"]([^'"]+)['"]""")
RE_INDEX = re.compile(r"""['"]index['"]\s*:\s*(\d+)""")
RE_DATA  = re.compile(r"""['"]data['"]\s*:\s*['"]([A-Za-z0-9+/=]+)['"]""")

def is_wav(header: bytes) -> bool:
    return header.startswith(b"RIFF") and b"WAVE" in header[:16]

def wav_params_and_frames(blob: bytes):
    with wave.open(io.BytesIO(blob), "rb") as r:
        nch, sw, sr = r.getnchannels(), r.getsampwidth(), r.getframerate()
        frames = r.readframes(r.getnframes())
    return (nch, sw, sr), frames

def main():
    text = Path(LOG_FILE).read_text(errors="ignore")
    chunks_by_id = defaultdict(list)

    for line in text.splitlines():
        if not RE_AUDIO_OUTPUT.search(line):
            continue
        m_id = RE_ID.search(line)
        m_idx = RE_INDEX.search(line)
        m_dat = RE_DATA.search(line)
        if not (m_id and m_dat):
            continue

        stream_id = m_id.group(1)
        index = int(m_idx.group(1)) if m_idx else 0
        b64 = m_dat.group(1)

        try:
            raw = base64.b64decode(b64)
        except Exception:
            continue

        chunks_by_id[stream_id].append((index, raw))

    if not chunks_by_id:
        print("No audio_output data found.")
        return

    for stream_id, chunks in chunks_by_id.items():
        chunks.sort(key=lambda t: t[0])

        params = None  # (nch, sampwidth_bytes, samplerate)
        pcm = bytearray()

        for idx, blob in chunks:
            if is_wav(blob[:12]):
                p, frames = wav_params_and_frames(blob)
                if params is None:
                    params = p
                else:
                    if p != params:
                        raise RuntimeError(f"Format mismatch in stream {stream_id}: {p} vs {params}")
                pcm.extend(frames)

                if SAVE_EACH_CHUNK:
                    with wave.open(f"chunk_{stream_id}_{idx:04d}.wav", "wb") as w:
                        w.setnchannels(p[0]); w.setsampwidth(p[1]); w.setframerate(p[2])
                        w.writeframes(frames)
            else:
                # Fallback: treat as raw PCM16 mono @ 48k if a non-WAV sneaks in
                if params is None:
                    params = (1, 2, 48000)
                pcm.extend(blob)

        if params is None:
            print(f"No decodable audio for stream {stream_id}")
            continue

        nch, sw, sr = params
        out_path = f"combined_{stream_id}.wav"
        with wave.open(out_path, "wb") as w:
            w.setnchannels(nch); w.setsampwidth(sw); w.setframerate(sr)
            w.writeframes(pcm)

        dur = len(pcm) / (nch * sw * sr)
        print(f"Wrote {out_path} — {nch} ch, {sw*8}-bit, {sr} Hz, {dur:.2f}s "
              f"from {len(chunks)} chunk(s).")

if __name__ == "__main__":
    main()
