import sys, pathlib, socket, subprocess, time, os, signal, pytest

# Asegura importar el repo
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def server():
    port = _free_port()
    proc = subprocess.Popen(["uvicorn","core.main:app","--port", str(port)])
    time.sleep(1.2)
    base_url = f"http://localhost:{port}"
    try:
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            os.kill(proc.pid, signal.SIGKILL)

@pytest.fixture
def client(server):
    import httpx
    with httpx.Client(base_url=server, timeout=5) as c:
        yield c
