# Lab 08: Digital Certificates.
# López Reyes José Roberto.

import datetime
import sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.x509.oid import NameOID


def imprimir_info_certificado(cert, nombre_etiqueta):
    print(f"\n{'=' * 50}")
    print(f" CERTIFICADO: {nombre_etiqueta}")
    print(f"{'=' * 50}")

    # Emitido a (Subject)
    subject = cert.subject
    cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    org = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
    print("\nEMITIDO A")
    print(f"Nombre común (CN):\n{cn}")
    print(f"Organización (O):\n{org}")

    # Número de serie en formato hexadecimal
    serial_hex = format(cert.serial_number, 'x').upper()
    if len(serial_hex) % 2 != 0:
        serial_hex = '0' + serial_hex
    serial_formatted = ':'.join(serial_hex[i:i + 2] for i in range(0, len(serial_hex), 2))
    print(f"\nNúmero de serie:\n{serial_formatted}")

    # Proporcionada por (Issuer)
    issuer = cert.issuer
    iss_cn = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    iss_org = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
    print("\nPROPORCIONADA POR")
    print(f"Nombre común (CN):\n{iss_cn}")
    print(f"Organización (O):\n{iss_org}")

    # Período de validez
    print("\nPERÍODO DE VALIDEZ")
    try:
        valido_desde = cert.not_valid_before_utc.strftime('%d %b %Y')
        valido_hasta = cert.not_valid_after_utc.strftime('%d %b %Y')
    except AttributeError:
        valido_desde = cert.not_valid_before.strftime('%d %b %Y')
        valido_hasta = cert.not_valid_after.strftime('%d %b %Y')

    print(f"Emitido el:\n{valido_desde}")
    print(f"Vence el:\n{valido_hasta}")

    # Huellas digitales SHA-256
    print("\nHUELLAS DIGITALES SHA-256")

    cert_fingerprint = cert.fingerprint(hashes.SHA256()).hex().upper()
    cert_fp_formatted = ' '.join(cert_fingerprint[i:i + 2] for i in range(0, len(cert_fingerprint), 2))
    print(f"Certificado:\n{cert_fp_formatted}")

    pub_key_bytes = cert.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(pub_key_bytes)
    pub_key_fingerprint = digest.finalize().hex().upper()
    pub_fp_formatted = ' '.join(pub_key_fingerprint[i:i + 2] for i in range(0, len(pub_key_fingerprint), 2))
    print(f"\nClave pública:\n{pub_fp_formatted}")
    print(f"{'=' * 50}\n")


def generar_certificado_rsa():
    print("\n--- Generando Certificado RSA-PSS ---")
    ca_private_key_rsa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject_private_key_rsa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject_public_key_rsa = subject_private_key_rsa.public_key()

    issuer_name_rsa = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Instituto Politécnico Nacional"),
        x509.NameAttribute(NameOID.COMMON_NAME, "IPN Root CA RSA-PSS 2026"),
    ])

    subject_name_rsa = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Escuela Superior de Cómputo (ESCOM)"),
        x509.NameAttribute(NameOID.COMMON_NAME, "roberto.escom.ipn.mx"),
    ])

    builder_rsa = (
        x509.CertificateBuilder()
        .subject_name(subject_name_rsa)
        .issuer_name(issuer_name_rsa)
        .public_key(subject_public_key_rsa)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
    )

    pss_padding = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
    cert_rsa = builder_rsa.sign(private_key=ca_private_key_rsa, algorithm=hashes.SHA256(), rsa_padding=pss_padding)

    with open("private_key_rsa.pem", "wb") as f:
        f.write(ca_private_key_rsa.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    with open("certificate_rsa_pss.pem", "wb") as f:
        f.write(cert_rsa.public_bytes(serialization.Encoding.PEM))

    print(" -> Archivos 'private_key_rsa.pem' y 'certificate_rsa_pss.pem' creados exitosamente.")
    imprimir_info_certificado(cert_rsa, "RSA-PSS (ESCOM)")


def generar_certificado_ecdsa():
    print("\n--- Generando Certificado ECDSA ---")
    ca_private_key_ec = ec.generate_private_key(ec.SECP256R1())
    subject_private_key_ec = ec.generate_private_key(ec.SECP256R1())
    subject_public_key_ec = subject_private_key_ec.public_key()

    issuer_name_ec = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Instituto Politécnico Nacional"),
        x509.NameAttribute(NameOID.COMMON_NAME, "IPN Root CA ECDSA 2026"),
    ])

    subject_name_ec = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "MX"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Escuela Superior de Cómputo (ESCOM)"),
        x509.NameAttribute(NameOID.COMMON_NAME, "roberto.escom.ipn.mx"),
    ])

    builder_ec = (
        x509.CertificateBuilder()
        .subject_name(subject_name_ec)
        .issuer_name(issuer_name_ec)
        .public_key(subject_public_key_ec)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
    )

    cert_ec = builder_ec.sign(private_key=ca_private_key_ec, algorithm=hashes.SHA256())

    with open("private_key_ec.pem", "wb") as f:
        f.write(ca_private_key_ec.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    with open("certificate_ecdsa.pem", "wb") as f:
        f.write(cert_ec.public_bytes(serialization.Encoding.PEM))

    print(" -> Archivos 'private_key_ec.pem' y 'certificate_ecdsa.pem' creados exitosamente.")
    imprimir_info_certificado(cert_ec, "ECDSA (ESCOM)")


def menu_principal():
    while True:
        print("\n" + "*" * 40)
        print(" GENERADOR DE CERTIFICADOS X.509 ")
        print("*" * 40)
        print("1. Generar Certificado RSA-PSS")
        print("2. Generar Certificado ECDSA")
        print("3. Generar Ambos")
        print("4. Salir")
        print("*" * 40)

        opcion = input("Selecciona una opción (1-4): ")

        if opcion == '1':
            generar_certificado_rsa()
        elif opcion == '2':
            generar_certificado_ecdsa()
        elif opcion == '3':
            generar_certificado_rsa()
            generar_certificado_ecdsa()
        elif opcion == '4':
            sys.exit(0)
        else:
            print("\nOpción no válida.")


if __name__ == "__main__":
    menu_principal()
