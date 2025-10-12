import socket

def find_available_port(start_port=8000, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
            return port
        except OSError:
            continue
    return None

port = find_available_port(8010)  # Empezar desde 8010
if port:
    print(f"✅ Puerto disponible: {port}")
else:
    print("❌ No se encontró puerto disponible")
