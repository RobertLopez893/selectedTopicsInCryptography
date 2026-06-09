# Práctica 8: RSA-PSS.
# López Reyes José Roberto.
# Torres Larios Andrés Emiliano.
# 7CM1.

import base64
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


# Función para generar las llaves
def generate_keys(priv_filename, pub_filename):
    # Generar llave privada RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    # Extraer llave pública
    public_key = private_key.public_key()

    # Serializar en formato binario puro (DER) para luego codificar en Base64
    priv_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Guardar en archivos codificando en Base64
    with open(priv_filename, "wb") as f:
        f.write(base64.b64encode(priv_der))

    with open(pub_filename, "wb") as f:
        f.write(base64.b64encode(pub_der))

    print(f"\nLlaves generadas exitosamente.")
    print(f"    Llave privada: {priv_filename}")
    print(f"    Llave pública: {pub_filename}")


# Función para generar la firma y guardarla en archivo
def sign_message(priv_filename, message_filename, signature_filename):
    # Leer y decodificar la llave privada
    with open(priv_filename, "rb") as f:
        priv_data = base64.b64decode(f.read())

    private_key = serialization.load_der_private_key(
        priv_data,
        password=None
    )

    # Leer el mensaje/archivo a firmar
    with open(message_filename, "rb") as f:
        message = f.read()

    # Firmar utilizando RSASSA-PSS y SHA-256
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    print(f"Firma: {base64.b64encode(signature)}")

    # Guardar la firma codificada en base64 en el archivo especificado
    with open(signature_filename, "wb") as f:
        f.write(base64.b64encode(signature))

    print(f"\nFirma generada y guardada exitosamente en: {signature_filename}")


# Función para verificar la firma desde un archivo
def verify_signature(pub_filename, message_filename, signature_filename):
    # Leer y decodificar la llave pública
    with open(pub_filename, "rb") as f:
        pub_data = base64.b64decode(f.read())

    public_key = serialization.load_der_public_key(pub_data)

    # Leer el archivo con el mensaje original
    with open(message_filename, "rb") as f:
        message = f.read()

    # Leer la firma en base64 desde su archivo
    with open(signature_filename, "rb") as f:
        signature_b64 = f.read()

    # Decodificar la firma a bytes
    try:
        signature = base64.b64decode(signature_b64)
    except Exception:
        return False

    # Verificar firma
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True  # La firma es válida
    except InvalidSignature:
        return False  # La firma no es válida


# 4. Programa principal
def main():
    print("=== Laboratorio 08: RSASSA-PSS ===")
    print("1. Generar par de llaves")
    print("2. Generar firma")
    print("3. Verificar firma")
    print("0. Salir")

    choice = input("\nSelecciona una opción (0-3): ")

    if choice == '1':
        priv_file = input("Ingresa el nombre del archivo para la llave privada (ej. privada.txt): ")
        pub_file = input("Ingresa el nombre del archivo para la llave pública (ej. publica.txt): ")
        generate_keys(priv_file, pub_file)

    elif choice == '2':
        priv_file = input("Ingresa el nombre del archivo de tu llave privada: ")
        msg_file = input("Ingresa el nombre del archivo que deseas firmar: ")
        sig_file = input("Ingresa el nombre del archivo para guardar la firma (ej. firma.txt): ")

        if not os.path.exists(msg_file) or not os.path.exists(priv_file):
            print("Error: El archivo del mensaje o la llave privada no existe.")
            return

        try:
            sign_message(priv_file, msg_file, sig_file)
        except Exception as e:
            print(f"Error al generar la firma: {e}")

    elif choice == '3':
        pub_file = input("Ingresa el nombre del archivo de la llave pública: ")
        msg_file = input("Ingresa el nombre del archivo del mensaje original: ")
        sig_file = input("Ingresa el nombre del archivo que contiene la firma: ")

        if not os.path.exists(msg_file) or not os.path.exists(pub_file) or not os.path.exists(sig_file):
            print("Error: Alguno de los archivos especificados no existe.")
            return

        try:
            is_valid = verify_signature(pub_file, msg_file, sig_file)
            print(f"\n[?] Resultado de verificación: {is_valid}")
            if is_valid:
                print("La firma es VÁLIDA y auténtica.")
            else:
                print("La firma es INVÁLIDA.")
        except Exception as e:
            print(f"Error durante la verificación: {e}")
            print(f"\nResultado de verificación: False")

    elif choice == '0':
        print("Saliendo...")
    else:
        print("Opción inválida.")


if __name__ == "__main__":
    main()
