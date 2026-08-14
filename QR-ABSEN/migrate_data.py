import os
import json
import requests
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), "data_absen.json")

def migrate():
    print("==================================================")
    print("  SCRIPT MIGRASI DATA OKK BAPENAS KE SUPABASE")
    print("==================================================")

    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_KEY", "")

    if not url or not key:
        print("\n[PERINGATAN] Variable SUPABASE_URL atau SUPABASE_KEY belum diset.")
        url = input("Masukkan SUPABASE_URL (contoh: https://xxxx.supabase.co): ").strip().rstrip("/")
        key = input("Masukkan SUPABASE_KEY (anon/public key): ").strip()

    if not url or not key:
        print("Error: SUPABASE_URL dan SUPABASE_KEY wajib diisi!")
        sys.exit(1)

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    if not os.path.exists(DATA_FILE):
        print(f"File {DATA_FILE} tidak ditemukan. Tidak ada data untuk dimigrasi.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    sesi_dict = data.get("sesi", {})
    absen_dict = data.get("absen", {})

    print(f"\nMenemukan {len(sesi_dict)} sesi dan data presensi...")

    # 1. Migrasi Sesi
    for sesi_id, sesi_info in sesi_dict.items():
        payload = {
            "id": str(sesi_id),
            "nama": sesi_info["nama"],
            "aktif": sesi_info.get("aktif", False)
        }
        res = requests.post(f"{url}/rest/v1/sesi", headers=headers, json=payload)
        if res.status_code in [200, 201, 204]:
            print(f"  [OK] Sesi '{sesi_info['nama']}' (ID: {sesi_id}) berhasil dimigrasi.")
        else:
            print(f"  [GAGAL] Sesi '{sesi_info['nama']}': {res.text}")

    # 2. Migrasi Absen
    total_absen = 0
    for sesi_id, maba_map in absen_dict.items():
        for nim, maba in maba_map.items():
            payload = {
                "sesi_id": str(sesi_id),
                "nim": str(nim),
                "nama": maba["nama"],
                "agora": maba.get("agora", "-"),
                "waktu": maba["waktu"]
            }
            res = requests.post(f"{url}/rest/v1/absen", headers=headers, json=payload)
            if res.status_code in [200, 201, 204]:
                total_absen += 1
            else:
                print(f"  [GAGAL] Absen NIM {nim}: {res.text}")

    print(f"\n[SELESAI] Berhasil memindahkan {len(sesi_dict)} sesi dan {total_absen} data presensi ke Supabase Cloud!")

if __name__ == "__main__":
    migrate()
