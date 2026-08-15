# VPTI Frontend — Design System Starter

Proyek Vite + React + TypeScript + Tailwind v4, dengan token desain VPTI
(navy `#0F2942` sebagai primary, status amber/emerald/rose untuk
berjalan/selesai/ditolak) dan komponen bergaya shadcn/ui (Button, Badge,
Card, DropdownMenu) + dark mode.

Dibangun & diverifikasi (type-check + production build) di sandbox Claude
sebelum dikirim — bukan sekadar file mentah yang belum dicoba.

## Menjalankan di komputer Anda

```bash
npm install
npm run dev      # dev server, biasanya http://localhost:5173
```

Build produksi:
```bash
npm run build
npm run preview
```

## Catatan

- `npx shadcn add ...` TIDAK dijalankan dari registry resmi (ui.shadcn.com
  tidak terjangkau dari sandbox ini) — komponen `src/components/ui/*.tsx`
  ditulis manual mengikuti pola shadcn/ui standar (New York style, cva,
  Radix primitives). Jika nanti Anda punya akses registry, `npx shadcn add`
  akan tetap bekerja dan mendeteksi `components.json` yang sudah dikonfigurasi.
- Token warna ada di `src/index.css` (empat-langkah arsitektur Tailwind v4:
  variabel CSS di `:root`/`.dark` → `@theme inline` → utility class).
  Ubah nilai `hsl(...)` di sana untuk menyesuaikan palet.
- `src/App.tsx` saat ini adalah halaman **verifikasi token**, bukan
  dashboard produk. Ganti isinya dengan dashboard peran (Importir, Petugas
  Registrasi, dst.) yang sudah dibuat sebelumnya di sesi ini, atau minta
  saya menyalinnya ke sini.
