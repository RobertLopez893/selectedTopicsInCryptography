import socket
import os
import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import rsa, padding, x25519
from cryptography.hazmat.primitives import hashes, serialization

ID_R = b"RESPONDER_NODE_HYBRID"


def main():
    print("[RESPONDER] Generando llaves RSA (2048 bits)...")
    sk_R = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pk_R = sk_R.public_key()

    pk_R_bytes = pk_R.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 65432))
        s.listen()
        print("[RESPONDER] Esperando conexión en el puerto 65432...")
        conn, addr = s.accept()

        with conn:
            print(f"[RESPONDER] Conexión establecida desde {addr}")

            # --- SETUP ---
            ID_I = conn.recv(1024)
            conn.sendall(ID_R)
            pk_I_bytes = conn.recv(2048)
            conn.sendall(pk_R_bytes)
            pk_I = serialization.load_pem_public_key(pk_I_bytes)
            print(f"[RESPONDER] Llave pública y ID de {ID_I.decode()} recibidos.\n")

            # ==========================================
            # FASE 1: SHARE (RSA-OAEP + SHA-256)
            # ==========================================
            print("--- FASE 1: SHARE ---")
            c_I = conn.recv(2048)

            # Descifrado con RSA-OAEP usando SHA-256 (Requisito 1)
            decrypted_I = sk_R.decrypt(
                c_I,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            received_ID_I, k_I = decrypted_I.split(b'||')
            print(f"[RESPONDER] c_I descifrado. k_I obtenido: {k_I.hex()}")

            k_R = os.urandom(16)
            print(f"[RESPONDER] Generó k_R: {k_R.hex()}")

            # Cifrado con RSA-OAEP usando SHA-256
            c_R = pk_I.encrypt(
                k_R,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            conn.sendall(c_R)

            # k_mac <- h(k_I | k_R) usando SHA3-256
            k_mac = hashlib.sha3_256(k_I + k_R).digest()
            print(f"[RESPONDER] k_mac (SHA3-256) calculado: {k_mac.hex()}\n")

            # ==========================================
            # FASE 2: EXCH (X25519)
            # ==========================================
            print("--- FASE 2: EXCH ---")
            X_bytes = conn.recv(32)
            pub_I = x25519.X25519PublicKey.from_public_bytes(X_bytes)
            print(f"[RESPONDER] Recibió llave pública X25519 (X) del Initiator.")

            priv_R = x25519.X25519PrivateKey.generate()
            pub_R = priv_R.public_key()

            Y_bytes = pub_R.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            conn.sendall(Y_bytes)
            print(f"[RESPONDER] Generó y envió llave pública X25519 (Y): {Y_bytes.hex()[:16]}...\n")

            # ==========================================
            # FASE 3: AUTH (HMAC + SHA3-256)
            # ==========================================
            print("--- FASE 3: AUTH ---")
            mac_I = conn.recv(1024)
            print(f"[RESPONDER] mac_I recibido: {mac_I.hex()}")

            # Verificar mac_I usando HMAC-SHA3-256 (Requisito 3)
            msg_I = Y_bytes + X_bytes + ID_I + ID_R
            expected_mac_I = hmac.new(k_mac, msg_I, hashlib.sha3_256).digest()

            if hmac.compare_digest(mac_I, expected_mac_I):
                print("[RESPONDER] RESULTADO: Autenticación de mac_I EXITOSA.")

                # mac_R <- MAC_{k_mac}(X | Y | ID_R | ID_I)
                msg_R = X_bytes + Y_bytes + ID_R + ID_I
                mac_R = hmac.new(k_mac, msg_R, hashlib.sha3_256).digest()
                conn.sendall(mac_R)

                # k_sess <- h(shared_secret) usando SHA3-256
                shared_secret = priv_R.exchange(pub_I)
                k_sess = hashlib.sha3_256(shared_secret).digest()
                print(f"[RESPONDER] RESULTADO FINAL: Llave de sesión (k_sess) establecida con SHA3-256: {k_sess.hex()}")
            else:
                print("[RESPONDER] RESULTADO: Falló la autenticación de mac_I.")


if __name__ == "__main__":
    main()
