import os
import sys

# Ensure QR-ABSEN directory is in Python path for module resolution and template access
qr_absen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "QR-ABSEN"))
if qr_absen_path not in sys.path:
    sys.path.insert(0, qr_absen_path)

from server import app
