# Penambahan Fitur "Form Pengumpulan Sanksi" pada Server OKK 2026

Fitur ini akan diintegrasikan ke dalam aplikasi server yang sudah berjalan, sehingga panitia dan peserta cukup menggunakan satu sistem terpadu.

## Proposed Changes

1. **Membuat Halaman Form Sanksi (Peserta)**
   - Menambahkan endpoint `/sanksi` di `server.py`
   - Membuat `sanksi_form.html` yang menarik dengan gaya desain BAPENAS 2026.
   - Field Isian: Nama, NIM, Prodi, Kelompok, Jenis Pelanggaran, Keterangan, dan Upload Bukti/Link Tugas Sanksi.

2. **Membuat Halaman Rekap Sanksi (Panitia)**
   - Menambahkan menu baru di Dashboard Panitia untuk melihat daftar pelanggar yang sudah mengumpulkan sanksi.
   - Endpoint `/panitia/sanksi`
   - Menyediakan fitur "Download ke Excel (CSV)" khusus untuk rekap sanksi.

3. **Database**
   - Menyimpan data sanksi ke dalam `data_sanksi.json`.

## Open Questions

> [!IMPORTANT]
> **Mohon Konfirmasi:**
> 1. Untuk bukti pengumpulan sanksi, apakah peserta harus **mengupload file (foto/PDF)** secara langsung ke sistem ini, atau cukup **menempelkan Link Google Drive** tugas mereka?
> 2. Kolom isian apa saja yang persisnya Anda inginkan? (Saran saya: Nama, NIM, Prodi, Kelompok, Jenis Pelanggaran, dan Bukti Sanksi).
