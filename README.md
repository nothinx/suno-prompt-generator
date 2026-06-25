# Suno Prompt Console

Ubah **satu link YouTube** + **satu puisi mentah** menjadi prompt **[Suno AI](https://suno.com)** siap pakai: deskriptor *Style of Music* + *Lyrics* bertag (`[Verse]`, `[Chorus]`, `[Bridge]`).

**▶ Live:** https://nothinx.github.io/suno-prompt-generator/

Satu file HTML, zero-install, 100% jalan di browser. Tidak ada server, tidak ada build step, tidak ada dependency.

## Cara pakai

1. **Source** — tempel link YouTube lagu referensi → tool menebak gaya (genre, mood, vokal, instrumen, era, produksi) dari metadata.
2. **Style** — edit deskriptor: hapus, tambah dari palet, atau ketik sendiri.
3. **Lyrics** — tempel puisi mentah (pisahkan bait dengan baris kosong) → auto-struktur jadi lirik bertag Suno. Bait berulang otomatis jadi `[Chorus]`.
4. **Prompt** — salin *Style of Music* + *Lyrics* langsung ke Suno.

### Mode komprehensif (opsional)

Tanpa key, tool hanya membaca judul + channel (cukup untuk tebakan dasar). Tambahkan [YouTube Data API v3 key](https://console.cloud.google.com/apis/library/youtube.googleapis.com) gratis untuk membaca deskripsi & tags → ekstraksi gaya jauh lebih kaya. Key disimpan lokal di browser saja.

## Jalankan lokal

Cukup buka `index.html` di browser. Tidak ada langkah lain.

## Analisis audio (opsional)

Browser tidak bisa mendengar audio, jadi gaya web ditebak dari **teks**. Untuk detail dari **suara asli** (tempo/BPM, key/nada, energy, kecerahan), ada `analyze.py` — jalan lokal, terpisah dari situs.

```bash
pip install -r requirements.txt     # juga butuh ffmpeg di PATH
python analyze.py "https://youtu.be/..."     # -> style.json
python analyze.py lagu.mp3                    # file lokal
python analyze.py --selftest                  # uji logika murni (tanpa deps)
```

Lalu di web buka **01 Source → Impor analisa audio**, pilih `style.json` → deskriptor (mis. `122 BPM`, `upbeat tempo`, `key A minor`, `energetic`, `bright production`) masuk otomatis.

> Catatan: tanpa `analyze.py`, gaya tetap ditebak dari teks metadata — kualitasnya mengikuti judul/deskripsi video.

## Lisensi

MIT
