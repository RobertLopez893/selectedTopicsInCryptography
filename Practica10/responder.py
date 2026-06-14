import socket
import os
import hashlib
import hmac
import json
import base64
from Crypto.Hash import KMAC256
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives import hashes, serialization

# ID fijo del Responder (tu número de equipo)
ID_R = b"RES_ID"

# Etiqueta de dominio para KMAC256 — debe ser idéntica en ambos lados
KMAC_CUSTOM = b"SKEME-AUTH"


def send_b64(conn, data: bytes):
    """Codifica en Base64, añade \n y envía."""
    conn.sendall(base64.b64encode(data) + b'\n')


def recv_b64(conn) -> bytes:
    """Recibe hasta \n y decodifica Base64."""
    buf = b""
    while not buf.endswith(b'\n'):
        chunk = conn.recv(4096)
        if not chunk:
            raise ConnectionError("Conexión cerrada inesperadamente.")
        buf += chunk
    return base64.b64decode(buf.strip())


def kmac256(key: bytes, data: bytes) -> bytes:
    """Wrapper de KMAC256 con parámetros fijos del protocolo."""
    return KMAC256.new(key=key, data=data, mac_len=32, custom=KMAC_CUSTOM).digest()


def main():
    print("[RESPONDER] Generando llaves RSA (2048 bits)...")
    sk_R = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_R = sk_R.public_key()

    pk_R_pem = pk_R.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 65432))
        s.listen()
        print("[RESPONDER] Esperando conexión en puerto 65432...")
        conn, addr = s.accept()

        with conn:
            print(f"[RESPONDER] Conexión desde {addr}")

            # ==========================================
            # SETUP: Intercambio de IDs y llaves RSA (JSON en Base64 + \n)
            # ==========================================
            raw = recv_b64(conn)
            json_I = json.loads(raw.decode('utf-8'))
            ID_I = json_I["id"].encode('utf-8')      # ID dinámico leído del JSON
            pk_I = serialization.load_pem_public_key(json_I["pub_key"].encode('utf-8'))
            print(f"[RESPONDER] Recibió setup de '{ID_I.decode()}'. Llave RSA cargada.")

            payload_R = json.dumps({"id": ID_R.decode('utf-8'), "pub_key": pk_R_pem})
            send_b64(conn, payload_R.encode('utf-8'))
            print(f"[RESPONDER] Envió JSON de setup (id='{ID_R.decode()}' + pub_key).\n")

            # ==========================================
            # FASE 1: SHARE (RSA-OAEP + SHA-256)
            # ==========================================
            print("--- FASE 1: SHARE ---")
            c_I = recv_b64(conn)

            decrypted_I = sk_R.decrypt(
                c_I,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            received_ID_I, k_I = decrypted_I.split(b'||', 1)
            print(f"[RESPONDER] c_I descifrado. ID: {received_ID_I.decode()}. k_I: {k_I.hex()}")

            k_R = os.urandom(16)
            print(f"[RESPONDER] Generó k_R: {k_R.hex()}")

            c_R = pk_I.encrypt(
                k_R,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            send_b64(conn, c_R)
            print(f"[RESPONDER] Envió c_R.")

            # k_mac <- SHA3-256(k_I || k_R)
            k_mac = hashlib.sha3_256(k_I + k_R).digest()
            print(f"[RESPONDER] k_mac (SHA3-256): {k_mac.hex()}\n")

            # ==========================================
            # FASE 2: EXCH (X25519)
            # ==========================================
            print("--- FASE 2: EXCH ---")
            X_bytes = recv_b64(conn)
            pub_I_x25519 = x25519.X25519PublicKey.from_public_bytes(X_bytes)
            print(f"[RESPONDER] Recibió X (llave X25519 del Initiator).")

            priv_R = x25519.X25519PrivateKey.generate()
            pub_R = priv_R.public_key()
            Y_bytes = pub_R.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            send_b64(conn, Y_bytes)
            print(f"[RESPONDER] Generó y envió Y: {Y_bytes.hex()[:16]}...\n")

            # ==========================================
            # FASE 3: AUTH (KMAC256)
            # ==========================================
            print("--- FASE 3: AUTH ---")
            mac_I = recv_b64(conn)
            print(f"[RESPONDER] Recibió mac_I: {mac_I.hex()}")

            # Verificar mac_I <- KMAC256_{k_mac}(Y || X || ID_I || ID_R)
            msg_I = Y_bytes + X_bytes + ID_I + ID_R
            expected_mac_I = kmac256(k_mac, msg_I)

            if hmac.compare_digest(mac_I, expected_mac_I):
                print("[RESPONDER] RESULTADO: Autenticación de mac_I EXITOSA.")

                # mac_R <- KMAC256_{k_mac}(X || Y || ID_R || ID_I)
                msg_R = X_bytes + Y_bytes + ID_R + ID_I
                mac_R = kmac256(k_mac, msg_R)
                send_b64(conn, mac_R)
                print(f"[RESPONDER] Envió mac_R (KMAC256): {mac_R.hex()}")

                shared_secret = priv_R.exchange(pub_I_x25519)
                k_sess = hashlib.sha3_256(shared_secret).digest()
                print(f"[RESPONDER] RESULTADO FINAL: k_sess (SHA3-256): {k_sess.hex()}")
            else:
                print("[RESPONDER] RESULTADO: Falló la autenticación de mac_I.")


if __name__ == "__main__":
    main()
