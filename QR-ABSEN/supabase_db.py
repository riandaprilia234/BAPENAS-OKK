import os
import json
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def is_supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# --- SESI ---

def get_all_sesi():
    if not is_supabase_configured():
        return {}
    try:
        url = f"{SUPABASE_URL}/rest/v1/sesi?select=*"
        res = requests.get(url, headers=get_headers(), timeout=5)
        if res.status_code == 200:
            sesi_dict = {}
            for item in res.json():
                sesi_dict[str(item["id"])] = {
                    "nama": item["nama"],
                    "aktif": item["aktif"]
                }
            return sesi_dict
    except Exception as e:
        print("Error get_all_sesi Supabase:", e)
    return {}

def create_sesi(nama):
    if not is_supabase_configured():
        return None
    try:
        url = f"{SUPABASE_URL}/rest/v1/sesi"
        # Generate a unique sesi ID
        sesi_id = str(len(get_all_sesi()) + 1)
        payload = {"id": sesi_id, "nama": nama, "aktif": True}
        res = requests.post(url, headers=get_headers(), json=payload, timeout=5)
        if res.status_code in [200, 201]:
            return sesi_id
    except Exception as e:
        print("Error create_sesi Supabase:", e)
    return None

def tutup_sesi(sesi_id):
    if not is_supabase_configured():
        return False
    try:
        url = f"{SUPABASE_URL}/rest/v1/sesi?id=eq.{sesi_id}"
        payload = {"aktif": False}
        res = requests.patch(url, headers=get_headers(), json=payload, timeout=5)
        return res.status_code in [200, 204]
    except Exception as e:
        print("Error tutup_sesi Supabase:", e)
        return False

# --- ABSEN ---

def get_absen_by_sesi(sesi_id):
    if not is_supabase_configured():
        return {}
    try:
        url = f"{SUPABASE_URL}/rest/v1/absen?sesi_id=eq.{sesi_id}&select=*"
        res = requests.get(url, headers=get_headers(), timeout=5)
        if res.status_code == 200:
            absen_dict = {}
            for item in res.json():
                absen_dict[str(item["nim"])] = {
                    "nama": item["nama"],
                    "agora": item.get("agora", "-"),
                    "waktu": item["waktu"]
                }
            return absen_dict
    except Exception as e:
        print("Error get_absen_by_sesi Supabase:", e)
    return {}

def submit_absen(sesi_id, nim, nama, agora, waktu):
    if not is_supabase_configured():
        return False
    try:
        headers = get_headers()
        headers["Prefer"] = "resolution=merge-duplicates"
        url = f"{SUPABASE_URL}/rest/v1/absen"
        payload = {
            "sesi_id": str(sesi_id),
            "nim": str(nim),
            "nama": nama,
            "agora": agora or "-",
            "waktu": waktu
        }
        res = requests.post(url, headers=headers, json=payload, timeout=5)
        return res.status_code in [200, 201, 204]
    except Exception as e:
        print("Error submit_absen Supabase:", e)
        return False

def get_all_absen_grouped():
    if not is_supabase_configured():
        return {}, {}
    
    sesi_map = get_all_sesi()
    absen_map = {}
    try:
        url = f"{SUPABASE_URL}/rest/v1/absen?select=*"
        res = requests.get(url, headers=get_headers(), timeout=10)
        if res.status_code == 200:
            for item in res.json():
                s_id = str(item["sesi_id"])
                nim = str(item["nim"])
                if s_id not in absen_map:
                    absen_map[s_id] = {}
                absen_map[s_id][nim] = {
                    "nama": item["nama"],
                    "agora": item.get("agora", "-"),
                    "waktu": item["waktu"]
                }
    except Exception as e:
        print("Error get_all_absen_grouped Supabase:", e)
        
    return sesi_map, absen_map
