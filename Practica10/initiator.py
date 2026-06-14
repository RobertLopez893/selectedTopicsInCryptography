import socket
import os
import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives import hashes, serialization

ID_I = b"INITIATOR_ROB_HYBRID"


def main():
    print("[INITIATOR] Generando llaves RSA (2048 bits)...")
    sk_I = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_I = sk_I.public_key()

    pk_I_bytes = pk_I.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 65432))
        print("[INITIATOR] Conectado al Responder mediante sockets.")

        # --- SETUP ---
        s.sendall(ID_I)
        ID_R = s.recv(1024)
        s.sendall(pk_I_bytes)
        pk_R_bytes = s.recv(2048)
        pk_R = serialization.load_pem_public_key(pk_R_bytes)
        print(f"[INITIATOR] Llave pública y ID de {ID_R.decode()} recibidos.\n")

        # ==========================================
        # FASE 1: SHARE (RSA-OAEP + SHA-256)
        # ==========================================
        print("--- FASE 1: SHARE ---")
        k_I = os.urandom(16)
        print(f"[INITIATOR] Generó k_I: {k_I.hex()}")

        # Cifrado con RSA-OAEP usando SHA-256 (Requisito 1)
        c_I = pk_R.encrypt(
            ID_I + b'||' + k_I,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        s.sendall(c_I)

        c_R = s.recv(2048)
        k_R = sk_I.decrypt(
            c_R,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        print(f"[INITIATOR] c_R descifrado. k_R obtenido: {k_R.hex()}")

        # k_mac <- h(k_I | k_R) usando SHA3-256 (Transición hacia Requisito 3)
        k_mac = hashlib.sha3_256(k_I + k_R).digest()
        print(f"[INITIATOR] k_mac (SHA3-256) calculado: {k_mac.hex()}\n")

        # ==========================================
        # FASE 2: EXCH (X25519)
        # ==========================================
        print("--- FASE 2: EXCH ---")
        # Generación de llaves X25519 (Requisito 2)
        priv_I = x25519.X25519PrivateKey.generate()
        pub_I = priv_I.public_key()

        X_bytes = pub_I.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        s.sendall(X_bytes)
        print(f"[INITIATOR] Generó y envió llave pública X25519 (X): {X_bytes.hex()[:16]}...")

        Y_bytes = s.recv(32)
        pub_R = x25519.X25519PublicKey.from_public_bytes(Y_bytes)
        print(f"[INITIATOR] Recibió llave pública X25519 (Y) del Responder.\n")

        # ==========================================
        # FASE 3: AUTH (HMAC + SHA3-256)
        # ==========================================
        print("--- FASE 3: AUTH ---")
        # mac_I <- MAC_{k_mac}(Y | X | ID_I | ID_R) usando SHA3-256 (Requisito 3)
        msg_I = Y_bytes + X_bytes + ID_I + ID_R
        mac_I = hmac.new(k_mac, msg_I, hashlib.sha3_256).digest()
        s.sendall(mac_I)
        print(f"[INITIATOR] Envió mac_I (HMAC-SHA3).")

        mac_R = s.recv(1024)
        print(f"[INITIATOR] Recibió mac_R: {mac_R.hex()}")

        # Verificar mac_R
        msg_R = X_bytes + Y_bytes + ID_R + ID_I
        expected_mac_R = hmac.new(k_mac, msg_R, hashlib.sha3_256).digest()

        if hmac.compare_digest(mac_R, expected_mac_R):
            print("[INITIATOR] RESULTADO: Autenticación de mac_R EXITOSA.")

            # k_sess <- h(shared_secret) usando SHA3-256
            shared_secret = priv_I.exchange(pub_R)
            k_sess = hashlib.sha3_256(shared_secret).digest()
            print(f"[INITIATOR] RESULTADO FINAL: Llave de sesión (k_sess) establecida con SHA3-256: {k_sess.hex()}")
        else:
            print("[INITIATOR] RESULTADO: Falló la autenticación.")


if __name__ == "__main__":
    main()
