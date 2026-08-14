import json
import os
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
import requests
from waitress import serve
import socket
import csv
import io
import openpyxl

app = Flask(__name__)
app.secret_key = "BAPENAS2026_OKK_UNDIKA_SECRET_KEY_X9#mK"

DATA_FILE = "data_absen.json"
SANKSI_FILE = "data_sanksi.json"
ADMIN_PIN = "2026"
TOKEN_WINDOW = 120

data_lock = threading.Lock()

def load_data():
    with data_lock:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {"sesi": {}, "absen": {}}

def save_data(data):
    with data_lock:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

def load_sanksi():
    with data_lock:
        if os.path.exists(SANKSI_FILE):
            try:
                with open(SANKSI_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

def save_sanksi(data):
    with data_lock:
        with open(SANKSI_FILE, "w") as f:
            json.dump(data, f, indent=4)

data_absen = load_data()

LOCAL_IP = socket.gethostbyname(socket.gethostname())
PORT = 5000

def get_base_url():
    url_file = os.path.join(os.path.dirname(__file__), "public_url.txt")
    if os.path.exists(url_file):
        return open(url_file).read().strip()
    return f"http://{LOCAL_IP}:{PORT}"

BASE_URL = get_base_url()
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwscj6QY55qJwWW2P8PJZSqIGliKDM_CpWnnYU8m-HB4JG_GI1p8xII-mHFpA1FzRkN/exec"

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/panitia", methods=["GET", "POST"])
def panitia():
    if request.method == "POST":
        if request.form.get("pin") == ADMIN_PIN:
            return render_template("panitia.html", sesi=data_absen["sesi"], base_url=BASE_URL)
        return "PIN Salah!", 403
    return render_template("login.html")

@app.route("/panitia/buka-sesi", methods=["POST"])
def buka_sesi():
    nama = request.form.get("nama")
    sesi_id = str(len(data_absen["sesi"]) + 1)
    data_absen["sesi"][sesi_id] = {"nama": nama, "aktif": True}
    save_data(data_absen)
    return jsonify({"status": "ok"})

@app.route("/panitia/tutup-sesi/<sesi_id>", methods=["POST"])
def tutup_sesi(sesi_id):
    if sesi_id in data_absen["sesi"]:
        data_absen["sesi"][sesi_id]["aktif"] = False
        save_data(data_absen)
    return jsonify({"status": "ok"})

@app.route("/tampilkan-qr/<sesi_id>")
def tampilkan_qr(sesi_id):
    if sesi_id not in data_absen["sesi"] or not data_absen["sesi"][sesi_id]["aktif"]:
        return "Sesi tidak aktif atau tidak ditemukan."
    return render_template("tampilan_qr.html", sesi_id=sesi_id, sesi=data_absen["sesi"][sesi_id], base_url=BASE_URL)

@app.route("/scan")
def scan():
    sesi_id = request.args.get("sesi")
    if sesi_id not in data_absen["sesi"] or not data_absen["sesi"][sesi_id]["aktif"]:
        return render_template("scan_error.html", error="Sesi Ditutup", detail="Sesi ini sudah tidak menerima absen.")
    return render_template("form_absen.html", sesi_id=sesi_id)

@app.route("/submit-absen", methods=["POST"])
def submit_absen():
    sesi_id = request.form.get("sesi_id")
    nim = request.form.get("nim")
    nama = request.form.get("nama")
    agora = request.form.get("agora", "-")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if sesi_id not in data_absen["sesi"] or not data_absen["sesi"][sesi_id]["aktif"]:
        return render_template("scan_error.html", error="Sesi Ditutup", detail="Sesi ini sudah ditutup.")

    if sesi_id not in data_absen["absen"]:
        data_absen["absen"][sesi_id] = {}

    if nim in data_absen["absen"][sesi_id]:
        return render_template("scan_sukses.html", sudah=True, nim=nim, nama=nama, sesi=data_absen["sesi"][sesi_id])

    data_absen["absen"][sesi_id][nim] = {"nama": nama, "agora": agora, "waktu": waktu}
    save_data(data_absen)

    # Kirim ke Google Sheets
    try:
        requests.post(SCRIPT_URL, data={"nim": nim, "nama": nama, "agora": agora, "sesi": data_absen["sesi"][sesi_id]["nama"], "waktu": waktu}, timeout=3)
    except:
        pass

    return render_template("scan_sukses.html", sudah=False, nim=nim, nama=nama, waktu=waktu, sesi=data_absen["sesi"][sesi_id])

@app.route("/download-excel")
def download_excel():
    wb = openpyxl.Workbook()
    # Hapus sheet default "Sheet"
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    # Kumpulkan data absen per agora
    data_per_agora = {}
    
    for sesi_id, sesi_info in data_absen["sesi"].items():
        sesi_nama = sesi_info["nama"]
        if sesi_id in data_absen["absen"]:
            for nim, maba in data_absen["absen"][sesi_id].items():
                agora = maba.get("agora", "Tidak Diketahui")
                if agora not in data_per_agora:
                    data_per_agora[agora] = []
                data_per_agora[agora].append([sesi_nama, nim, maba["nama"], maba["waktu"]])
                
    # Buat sheet untuk masing-masing agora
    if not data_per_agora:
        ws = wb.create_sheet(title="Kosong")
        ws.append(["Belum ada data"])
    else:
        for agora, rows in data_per_agora.items():
            # Nama sheet Excel maksimal 31 karakter dan tidak boleh ada karakter khusus tertentu
            safe_title = str(agora)[:31].replace("/", "-").replace("\\", "-")
            ws = wb.create_sheet(title=safe_title)
            # Header
            ws.append(["Nama Sesi", "NIM", "Nama Lengkap", "Waktu Absen"])
            # Data
            for r in rows:
                ws.append(r)
                
    # Simpan ke memory
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=Rekap_MultiTab_OKK_ETHIVATION.xlsx"}
    )

@app.route("/api/live-absen/<sesi_id>")
def api_live_absen(sesi_id):
    if sesi_id not in data_absen["absen"]:
        return jsonify([])
    
    # Ambil list semua absen, urutkan dari yang terbaru (berdasarkan waktu insert)
    semua_absen = list(data_absen["absen"][sesi_id].values())
    # Ambil 10 orang terakhir yang absen dan balikkan urutannya agar yang paling baru di atas
    terbaru = semua_absen[-15:]
    terbaru.reverse()
    
    return jsonify(terbaru)

if __name__ == "__main__":
    print(f"  QR ABSEN DINAMIS - OKK ETHIVATION")
    print(f"  Berjalan di port {PORT} dengan Waitress (32 Threads)...")
    serve(app, host="0.0.0.0", port=PORT, threads=32)
