#!/usr/bin/env python3
"""analyze.py — turunkan deskriptor gaya Suno dari AUDIO asli sebuah lagu.

Browser tidak bisa mendengar audio, jadi gaya hanya bisa ditebak dari teks.
Script ini menutup celah itu: unduh audio (yt-dlp) lalu ekstrak fitur sonik
(librosa) — tempo/BPM, key/nada, energy, kecerahan — dan memetakannya ke
deskriptor gaya Suno. Outputnya `style.json` yang bisa diimpor di web lewat
tombol "Impor analisa audio".

Ini SENGAJA dipisah dari MVP HTML (butuh Python + ffmpeg lokal), sesuai CLAUDE.md.

Pakai:
    pip install -r requirements.txt        # juga butuh ffmpeg di PATH
    python analyze.py "https://youtu.be/..."        # -> tulis style.json
    python analyze.py "URL" -o lagu.json            # nama output lain
    python analyze.py lagu.mp3                       # file lokal, lewati unduh
    python analyze.py --selftest                     # uji logika murni (tanpa deps)
"""
import argparse
import json
import os
import sys
import tempfile

# ---- profil Krumhansl-Schmuckler untuk estimasi key (12 pitch class) --------
PITCHES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def _pearson(a, b):
    """Korelasi Pearson, pure-python (biar bisa diuji tanpa numpy)."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    num = sum(x * y for x, y in zip(da, db))
    den = (sum(x * x for x in da) * sum(y * y for y in db)) ** 0.5
    return num / den if den else 0.0


def estimate_key(chroma12):
    """chroma12 = energi rata-rata per pitch class (panjang 12) -> 'A minor'.

    ponytail: heuristik korelasi profil, bukan deteksi key sempurna. Cukup untuk
    prompt; upgrade ke madmom/essentia kalau butuh presisi musikologis.
    """
    assert len(chroma12) == 12, "chroma harus 12 nilai"
    best = (-2.0, None)
    for i in range(12):
        rot_maj = [chroma12[(i + s) % 12] for s in range(12)]
        # korelasikan profil tetap dgn chroma yang dirotasi ke tonika i
        cmaj = _pearson(_MAJOR, rot_maj)
        cmin = _pearson(_MINOR, rot_maj)
        if cmaj > best[0]:
            best = (cmaj, f"{PITCHES[i]} major")
        if cmin > best[0]:
            best = (cmin, f"{PITCHES[i]} minor")
    return best[1]


def tempo_descriptors(bpm):
    bpm = int(round(bpm))
    bucket = "slow tempo" if bpm < 90 else "mid tempo" if bpm <= 120 else "upbeat tempo"
    return [f"{bpm} BPM", bucket]


def energy_descriptors(rms_norm):
    """rms_norm: 0..1 (RMS rata-rata dinormalisasi)."""
    if rms_norm < 0.04:
        return ["calm", "soft dynamics"]
    if rms_norm < 0.12:
        return ["mellow"]
    return ["energetic", "powerful dynamics"]


def brightness_descriptors(centroid_hz):
    if centroid_hz < 1500:
        return ["warm production"]
    if centroid_hz > 3000:
        return ["bright production"]
    return []


def build_style(bpm, key, rms_norm, centroid_hz):
    """Gabungkan fitur -> dict {dimensi: [deskriptor]} sesuai state web."""
    return {
        "tempo": tempo_descriptors(bpm),
        "custom": [f"key {key}"],
        "mood": energy_descriptors(rms_norm),
        "production": brightness_descriptors(centroid_hz),
    }


# ---- jalur audio (butuh librosa/yt-dlp/ffmpeg) ------------------------------
def download_audio(url, dest_dir):
    from yt_dlp import YoutubeDL
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(dest_dir, "%(id)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return os.path.join(dest_dir, info["id"] + ".wav"), info.get("title", "")


def analyze_file(path):
    import librosa
    import numpy as np
    # analisa potongan representatif: lewati 20s intro, ambil maks 120s
    y, sr = librosa.load(path, sr=22050, mono=True, offset=20.0, duration=120.0)
    if y.size == 0:  # lagu sangat pendek: muat dari awal
        y, sr = librosa.load(path, sr=22050, mono=True, duration=120.0)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    key = estimate_key([float(x) for x in chroma])
    rms_norm = float(np.clip(librosa.feature.rms(y=y).mean(), 0, 1))
    centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    return build_style(bpm, key, rms_norm, centroid), {
        "bpm": round(bpm, 1), "key": key,
        "rms": round(rms_norm, 4), "centroid_hz": round(centroid, 1),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Analisa audio -> deskriptor gaya Suno (style.json)")
    ap.add_argument("input", nargs="?", help="URL YouTube atau path file audio lokal")
    ap.add_argument("-o", "--out", default="style.json", help="file output (default style.json)")
    ap.add_argument("--selftest", action="store_true", help="uji logika murni lalu keluar")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.input:
        ap.error("beri URL YouTube atau path file audio (atau --selftest)")

    title = ""
    is_url = args.input.startswith("http") or "youtu" in args.input
    try:
        if is_url:
            with tempfile.TemporaryDirectory() as tmp:
                print("Mengunduh audio…", file=sys.stderr)
                path, title = download_audio(args.input, tmp)
                print("Menganalisa…", file=sys.stderr)
                style, feats = analyze_file(path)
        else:
            print("Menganalisa file lokal…", file=sys.stderr)
            style, feats = analyze_file(args.input)
    except ImportError as e:
        sys.exit(f"Dependency hilang: {e}. Jalankan: pip install -r requirements.txt (dan pasang ffmpeg).")

    out = {"title": title, "source": args.input, "features": feats, "style": style}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    flat = [d for arr in style.values() for d in arr]
    print(f"✓ {len(flat)} deskriptor -> {args.out}")
    print("  " + ", ".join(flat))
    print(f"  Impor file ini di web: tombol 'Impor analisa audio'.")


def selftest():
    # key: chroma dominan C harus -> 'C major'; profil minor A -> 'A minor'
    c_major = [1.0, 0, 0.3, 0, 0.6, 0.4, 0, 0.7, 0, 0.2, 0, 0.3]
    assert estimate_key(c_major) == "C major", estimate_key(c_major)
    a_minor = [_MINOR[(i - 9) % 12] for i in range(12)]  # profil minor ditonika ke A
    assert estimate_key(a_minor) == "A minor", estimate_key(a_minor)
    # tempo buckets
    assert tempo_descriptors(70) == ["70 BPM", "slow tempo"]
    assert tempo_descriptors(110)[1] == "mid tempo"
    assert tempo_descriptors(140)[1] == "upbeat tempo"
    # energy / brightness
    assert "calm" in energy_descriptors(0.01)
    assert "energetic" in energy_descriptors(0.5)
    assert brightness_descriptors(800) == ["warm production"]
    assert brightness_descriptors(4000) == ["bright production"]
    # bentuk output cocok dgn dimensi state web
    st = build_style(128, "G minor", 0.5, 3500)
    assert set(st) <= {"genre", "mood", "vocal", "instrument", "tempo", "era", "production", "custom"}
    assert "128 BPM" in st["tempo"] and "key G minor" in st["custom"]
    print("SELFTEST OK")


if __name__ == "__main__":
    main()
