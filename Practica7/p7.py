# Práctica 7: RSA with CRT.
# López Reyes José Roberto.
# Torres Larios Andrés Emiliano.
# 7CM1.

import base64
import json
from Crypto.Util.number import getPrime, GCD, inverse, bytes_to_long, long_to_bytes
from Crypto.Hash import SHA256


def gen_keys():
    phi = 0
    e = 65537

    while GCD(e, phi) != 1:
        p, q = getPrime(512), getPrime(512)

        if q > p:
            p, q = q, p

        n = p * q
        phi = (p - 1) * (q - 1)

    d = inverse(e, phi)
    dP = d % (p - 1)
    dQ = d % (q - 1)
    qInv = inverse(q, p)

    public_key = {"n": n, "e": e}
    private_key = {
        "n": n,
        "e": e,
        "d": d,
        "p": p,
        "q": q,
        "dP": dP,
        "dQ": dQ,
        "qInv": qInv
    }

    pub_bytes = json.dumps(public_key).encode('utf-8')
    pub_b64 = base64.b64encode(pub_bytes).decode('utf-8')

    print(pub_b64)

    priv_bytes = json.dumps(private_key).encode('utf-8')
    priv_b64 = base64.b64encode(priv_bytes).decode('utf-8')

    print(priv_b64)

    with open("public_key.txt", "w") as pub_file:
        pub_file.write(pub_b64)

    with open("private_key.txt", "w") as priv_file:
        priv_file.write(priv_b64)

    print("Claves RSA-CRT generadas.")


def sign_message(priv_key, message, signature):
    with open(priv_key, "r") as archivo:
        priv_b64 = archivo.read()

    priv_bytes = base64.b64decode(priv_b64)
    priv_json = priv_bytes.decode('utf-8')

    k_priv = json.loads(priv_json)
    print("Clave privada cargada correctamente.")

    with open(message, "rb") as archivo:
        M = archivo.read()

    hash = SHA256.new(M)
    h = bytes_to_long(hash.digest())

    s1 = pow(h, k_priv['dP'], k_priv['p'])
    s2 = pow(h, k_priv['dQ'], k_priv['q'])
    t = (k_priv['qInv'] * (s1 - s2)) % k_priv['p']
    s = s2 + (t * k_priv['q'])

    firma_bytes = long_to_bytes(s)
    firma_64 = base64.b64encode(firma_bytes).decode('utf-8')

    print(f"\nFirma generada en Base64:\n{firma_64}")

    with open(signature, "w") as f_file:
        f_file.write(firma_64)


def verify_sign(pub_key, message, signature):
    with open(pub_key, "r") as archivo:
        pub_b64 = archivo.read()

    pub_bytes = base64.b64decode(pub_b64)
    pub_json = pub_bytes.decode('utf-8')
    k_pub = json.loads(pub_json)

    with open(signature, "r") as archivo:
        firma_b64 = archivo.read()

    firma_bytes = base64.b64decode(firma_b64)
    s = bytes_to_long(firma_bytes)

    with open(message, "rb") as archivo:
        mensaje_bytes = archivo.read()

    hash = SHA256.new(mensaje_bytes)
    h_prima = bytes_to_long(hash.digest())

    h = pow(s, k_pub['e'], k_pub['n'])

    if h == h_prima:
        print("\nFirma válida.")
        return True
    else:
        print("\nFirma inválida.")
        return False


while True:
    print("\n" + "=" * 45)
    print("   SISTEMA DE FIRMAS RSA-CRT (Práctica 7)")
    print("=" * 45)
    print("1. Generar nuevo par de claves")
    print("2. Firmar un documento")
    print("3. Verificar una firma")
    print("4. Salir")
    print("=" * 45)

    opcion = input("Elige una opción (1-4): ")

    if opcion == '1':
        gen_keys()

    elif opcion == '2':
        print("\n--- FIRMAR DOCUMENTO ---")
        priv = input("Ruta de la clave privada: ")
        msg = input("Ruta del documento a firmar: ")
        out = input("Nombre del archivo de salida: ")
        sign_message(priv, msg, out)

    elif opcion == '3':
        print("\n--- VERIFICAR FIRMA ---")
        pub = input("Ruta de la clave pública del remitente: ") or "public_key.txt"
        msg = input("Ruta del documento recibido: ")
        sig = input("Ruta de la firma: ") or "signature.txt"
        verify_sign(pub, msg, sig)

    elif opcion == '4':
        break

    else:
        print("\nOpción no válida.")
