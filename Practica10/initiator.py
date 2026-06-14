import socket
import os
import hashlib
import hmac
import json
import base64
from Crypto.Hash import KMAC256
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives import hashes, serialization

# El ID del iniciador (el tuyo / de tu equipo)
ID_I = b"INI_ID"

# Etiqueta de dominio para KMAC256 — debe ser idéntica en ambos lados
KMAC_CUSTOM = b"SKEME-AUTH"


def send_b64(sock, data: bytes):
    """Codifica en Base64, añade \n y envía."""
    sock.sendall(base64.b64encode(data) + b'\n')


def recv_b64(sock) -> bytes:
    """Recibe hasta \n y decodifica Base64."""
    buf = b""
    while not buf.endswith(b'\n'):
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Conexión cerrada inesperadamente.")
        buf += chunk
    return base64.b64decode(buf.strip())


def kmac256(key: bytes, data: bytes) -> bytes:
    """Wrapper de KMAC256 con parámetros fijos del protocolo."""
    return KMAC256.new(key=key, data=data, mac_len=32, custom=KMAC_CUSTOM).digest()


def main():
    print("[INITIATOR] Generando llaves RSA (2048 bits)...")
    sk_I = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_I = sk_I.public_key()

    pk_I_pem = pk_I.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 65432))
        print("[INITIATOR] Conectado al Responder.")

        # ==========================================
        # SETUP: Intercambio de IDs y llaves RSA (JSON en Base64 + \n)
        # ==========================================
        payload_I = json.dumps({"id": ID_I.decode('utf-8'), "pub_key": pk_I_pem})
        send_b64(s, payload_I.encode('utf-8'))
        print(f"[INITIATOR] Envió JSON de setup (id + pub_key).")

        raw = recv_b64(s)
        json_R = json.loads(raw.decode('utf-8'))
        ID_R = json_R["id"].encode('utf-8')
        pk_R = serialization.load_pem_public_key(json_R["pub_key"].encode('utf-8'))
        print(f"[INITIATOR] Recibió setup de '{ID_R.decode()}'. Llave RSA cargada.\n")

        # ==========================================
        # FASE 1: SHARE (RSA-OAEP + SHA-256)
        # ==========================================
        print("--- FASE 1: SHARE ---")
        k_I = os.urandom(16)
        print(f"[INITIATOR] Generó k_I: {k_I.hex()}")

        c_I = pk_R.encrypt(
            ID_I + b'||' + k_I,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        send_b64(s, c_I)
        print(f"[INITIATOR] Envió c_I (RSA-OAEP cifrado).")

        c_R = recv_b64(s)
        k_R = sk_I.decrypt(
            c_R,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(f"[INITIATOR] c_R descifrado. k_R obtenido: {k_R.hex()}")

        # k_mac <- SHA3-256(k_I || k_R)
        k_mac = hashlib.sha3_256(k_I + k_R).digest()
        print(f"[INITIATOR] k_mac (SHA3-256): {k_mac.hex()}\n")

        # ==========================================
        # FASE 2: EXCH (X25519)
        # ==========================================
        print("--- FASE 2: EXCH ---")
        priv_I = x25519.X25519PrivateKey.generate()
        pub_I = priv_I.public_key()

        X_bytes = pub_I.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        send_b64(s, X_bytes)
        print(f"[INITIATOR] Envió llave pública X25519 (X): {X_bytes.hex()[:16]}...")

        Y_bytes = recv_b64(s)
        pub_R_x25519 = x25519.X25519PublicKey.from_public_bytes(Y_bytes)
        print(f"[INITIATOR] Recibió llave pública X25519 (Y) del Responder.\n")

        # ==========================================
        # FASE 3: AUTH (KMAC256)
        # ==========================================
        print("--- FASE 3: AUTH ---")
        # mac_I <- KMAC256_{k_mac}(Y || X || ID_I || ID_R)
        msg_I = Y_bytes + X_bytes + ID_I + ID_R
        mac_I = kmac256(k_mac, msg_I)
        send_b64(s, mac_I)
        print(f"[INITIATOR] Envió mac_I (KMAC256): {mac_I.hex()}")

        mac_R = recv_b64(s)
        print(f"[INITIATOR] Recibió mac_R: {mac_R.hex()}")

        # Verificar mac_R <- KMAC256_{k_mac}(X || Y || ID_R || ID_I)
        msg_R = X_bytes + Y_bytes + ID_R + ID_I
        expected_mac_R = kmac256(k_mac, msg_R)

        if hmac.compare_digest(mac_R, expected_mac_R):
            print("[INITIATOR] RESULTADO: Autenticación de mac_R EXITOSA.")
            shared_secret = priv_I.exchange(pub_R_x25519)
            k_sess = hashlib.sha3_256(shared_secret).digest()
            print(f"[INITIATOR] RESULTADO FINAL: k_sess (SHA3-256): {k_sess.hex()}")
        else:
            print("[INITIATOR] RESULTADO: Falló la autenticación de mac_R.")


if __name__ == "__main__":
    main()
