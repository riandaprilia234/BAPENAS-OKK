import urllib.request
import subprocess
import time
import re
import os
import sys

CF_EXE = "cloudflared.exe"

print("====================================================")
print("  MEMBUKA JALUR INTERNET DENGAN CLOUDFLARE")
print("====================================================")

# Download cloudflared if not exists
if not os.path.exists(CF_EXE):
    print("Mengunduh modul internet (cloudflared)... Mohon tunggu...")
    try:
        urllib.request.urlretrieve("https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe", CF_EXE)
        print("Selesai mengunduh!")
    except Exception as e:
        print("Gagal mengunduh cloudflared:", e)
        sys.exit(1)

print("Menghubungkan ke server Cloudflare...")

# Run cloudflared
process = subprocess.Popen(
    [CF_EXE, "tunnel", "--url", "http://localhost:5000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

public_url = None

# Parse stderr/stdout for the trycloudflare.com URL
start_time = time.time()
while time.time() - start_time < 30:
    line = process.stdout.readline()
    if not line:
        continue
    # print("[CF]", line.strip()) # Debug
    match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
    if match:
        public_url = match.group(1)
        break

if public_url:
    print(f"\n[SUKSES] URL INTERNET ANDA: {public_url}")
    
    with open("public_url.txt", "w", encoding="utf-8") as f:
        f.write(public_url)
    
    print("\nMenjalankan Server Absen...\n")
    os.system("python server.py")
else:
    print("\n[GAGAL] Gagal mendapatkan URL dari Cloudflare. Cek koneksi internet Anda.")
    process.terminate()

if os.path.exists("public_url.txt"):
    os.remove("public_url.txt")
