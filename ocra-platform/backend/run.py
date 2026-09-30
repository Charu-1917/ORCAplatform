"""
Starts the ORCA backend + frontend on all network interfaces.

    python run.py

Open the printed URL on this PC, on other PCs in the same network, or on a phone.
"""
import os
import socket
import sys

import uvicorn

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BACKEND_DIR)  # checkpoints/ and data/ paths are relative to the backend folder
sys.path.insert(0, BACKEND_DIR)

from app.config import settings  # noqa: E402


def lan_addresses():
    addrs = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            addrs.add(info[4][0])
    except socket.gaierror:
        pass
    try:
        # Finds the address of the interface that routes to the internet / LAN
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            addrs.add(s.getsockname()[0])
    except OSError:
        pass
    return sorted(a for a in addrs if not a.startswith("127."))


if __name__ == "__main__":
    port = settings.PORT
    print("\n  ORCA Ocean Intelligence is starting...\n")
    print(f"  This PC:            http://localhost:{port}")
    for ip in lan_addresses():
        print(f"  Other PCs / phone:  http://{ip}:{port}")
    print(f"  Phone over USB:     adb reverse tcp:{port} tcp:{port}  ->  http://localhost:{port}")
    print(f"  API docs:           http://localhost:{port}/docs")
    print(f"  Ollama model:       {settings.OLLAMA_MODEL} @ {settings.OLLAMA_BASE_URL}\n")
    uvicorn.run("app.main:app", host=settings.HOST, port=port)
