# Suno Prompt Console

Punya lagu di YouTube yang vibe-nya pengen kamu tiru, dan secarik puisi yang
pengen kamu jadikan lagu? Tool ini menjembatani keduanya: dari link YouTube ia
menebak gaya musiknya, dari puisimu ia merangkai lirik bertag, lalu menyodorkan
dua kolom yang tinggal kamu tempel ke [Suno](https://suno.com) — *Style of Music*
dan *Lyrics*.

**Coba langsung:** https://nothinx.github.io/suno-prompt-generator/

Tidak ada yang perlu dipasang. Satu berkas `index.html`, semuanya jalan di
browser, dan tidak ada yang dikirim ke mana pun selain ke YouTube saat menebak
judul lagu.

## Alurnya

Empat langkah, dari kiri ke kanan seperti rantai sinyal:

1. **Source** — tempel link YouTube. Tool membaca metadata lagu dan menebak
   genre, mood, vokal, instrumen, era, sampai karakter produksinya.
2. **Style** — hasil tebakan muncul sebagai tag. Buang yang meleset, tambah dari
   palet, atau ketik sendiri. Ini punyamu untuk diutak-atik.
3. **Lyrics** — tempel puisi mentah, pisahkan tiap bait dengan baris kosong.
   Tool memberinya tag Suno; bait yang berulang otomatis jadi `[Chorus]`.
4. **Prompt** — salin, tempel ke Suno, selesai.

## Soal tebakan gaya

Jujur saja: kualitas tebakan mengikuti seberapa kaya teks yang tersedia. Tanpa
apa-apa, YouTube cuma memberi judul dan nama channel — sering kali itu hanya
cukup untuk satu-dua tag. Ada dua cara membuatnya jauh lebih akurat:

- **Tempel deskripsi videonya.** Buka video, salin deskripsinya (yang di balik
  tombol "...Selengkapnya"), tempel di kotak yang tersedia. Cara paling cepat,
  tanpa setup apa pun. Dari judul saja biasanya dapat satu tag; ditambah
  deskripsi bisa belasan.
- **Pakai API key.** Dengan [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
  (gratis), tool ikut membaca deskripsi, tags, dan kategori genre resmi secara
  otomatis. Panduan langkah demi langkahnya ada langsung di dalam aplikasi.
  Key-nya disimpan di browsermu sendiri, bukan di server mana pun.

## Menebak dari suaranya, bukan teksnya

Browser tidak bisa mendengar. Jadi kalau kamu mau detail yang hanya bisa
diketahui dari audio asli — tempo, nada dasar, dinamika, terang-gelapnya
mix — ada `analyze.py` yang jalan di komputermu sendiri:

```bash
pip install -r requirements.txt          # butuh ffmpeg di PATH juga
python analyze.py "https://youtu.be/..."  # menghasilkan style.json
python analyze.py lagu.mp3                 # atau dari berkas lokal
```

Script-nya mengunduh audio (yt-dlp) dan mengukur fiturnya (librosa), lalu
menulis `style.json`. Balik ke web, buka **Source → Impor analisa audio**, pilih
berkas itu, dan tag seperti `122 BPM`, `key A minor`, atau `bright production`
langsung masuk.

Mau cek logikanya tanpa memasang apa-apa? `python analyze.py --selftest`.

## Menjalankan sendiri

Klon repo ini lalu buka `index.html` di browser. Sungguh, itu saja.

```bash
git clone https://github.com/nothinx/suno-prompt-generator.git
```

## Lisensi

MIT — pakai, ubah, sebar sesukamu.
