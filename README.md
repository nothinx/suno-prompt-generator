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

## Catatan

Browser tidak bisa membaca audio, jadi gaya ditebak dari **teks metadata**, bukan suara — kualitas tebakan mengikuti kualitas judul/deskripsi video.

## Lisensi

MIT
