# Práctica 5: Toy ECDSA.
# López Reyes José Roberto. 7CM1.

from random import randint
import re
import csv
import ast


# Functions to fold points from previous sessions
def add_points(p, q, n):
    if p == (0, 1, 0):
        return q

    if q == (0, 1, 0):
        return p

    x1, x2, y1, y2 = p[0], q[0], p[1], q[1]

    if x1 == x2:
        if (y1 + y2) % n == 0:
            return (0, 1, 0)
        elif y1 == y2:
            print("Aviso: Sumando el mismo punto, usa double_point.")
            return (0, 1, 0)

    numerador = (y2 - y1) % n
    denominador_inverso = pow((x2 - x1) % n, -1, n)

    pendiente = (numerador * denominador_inverso) % n

    x3 = (pow(pendiente, 2, n) - x1 - x2) % n
    y3 = (pendiente * (x1 - x3) - y1) % n

    addition = (x3, y3, 1)

    return addition


def double_point(p, n, a):
    if p == (0, 1, 0):
        return p

    x1, x2 = p[0], p[0]
    y1, y2 = p[1], p[1]

    if y1 == 0:
        return (0, 1, 0)

    pendiente = ((3 * pow(x1, 2, n) + a) % n) * pow((2 * y1), -1, n)

    x3 = (pow(pendiente, 2, n) - x1 - x2) % n
    y3 = (pendiente * (x1 - x3) - y1) % n

    addition = (x3, y3, 1)

    return addition


def left_right_bin(k, P, p, a):
    k_bin = bin(k)[2:]
    Q = (0, 1, 0)

    for i in range(len(k_bin)):
        Q = double_point(Q, p, a)
        if int(k_bin[i]) == 1:
            Q = add_points(P, Q, p)

    return Q


# Read the curves
def read_curves(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filename}'. Make sure it's in the same folder.")
        return []

    # Regex pattern to catch all variations and line breaks
    pattern = r"y\^2\s*=\s*x\^3\s*\+\s*(\d+)\*x\s*\+\s*(\d+)\s*over Finite Field[\s\S]*?size\s*(\d+)[\s\S]*?G\s*[:=]\s*\(\s*(\d+)\s*:\s*(\d+)\s*:\s*1\s*\)[\s\S]*?q\s*[:=]\s*(\d+)"

    matches = list(re.finditer(pattern, content))
    curves = []

    # Store all matched curves in a list of dictionaries
    for match in matches:
        curves.append({
            'a': int(match.group(1)),
            'b': int(match.group(2)),
            'p': int(match.group(3)),
            'x': int(match.group(4)),
            'y': int(match.group(5)),
            'q': int(match.group(6))
        })

    return curves


# Key Generation for ECDSA
def gen_keys(p, a, b, q, G):
    d = randint(1, q - 1)
    B = left_right_bin(d, G, p, a)

    return d, p, a, b, q, G, B


# Signature Generation
def sign_gen(m, a, p, q, G, d):
    KE = randint(1, q - 1)
    T = left_right_bin(KE, G, p, a)
    r = T[0] % q
    s = ((m + d * r) * pow(KE, -1, q)) % q

    return r, s


# Verification Signature
def ver_sign(p, a, b, q, G, B, m, r, s):
    w = pow(s, -1, q)
    u1 = (w * m) % q
    u2 = (w * r) % q
    P = add_points(left_right_bin(u1, G, p, a), left_right_bin(u2, B, p, a), p)

    if (P[0] % q) == r:
        return True
    else:
        return False


# Verificate all signatures
# Procesamiento del CSV (Igual al de DSA pero adaptado a ECDSA)
def generar_tabla_ecdsa(ruta_archivo):
    print("\n| Compañero | Mensaje (m) | Firma (r, s) | ¿Es válida? |")
    print("|---|---|---|---|")

    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
            lector = csv.reader(archivo)
            next(lector, None)

            for fila in lector:
                if len(fila) < 11:
                    continue

                nombre = fila[1]

                try:
                    p_val = int(fila[2])
                    a_val = int(fila[3])
                    b_val = int(fila[4])
                    q_val = int(fila[5])

                    G_val = ast.literal_eval(fila[6])
                    B_val = ast.literal_eval(fila[7])

                    m_val = int(fila[8])
                    r_val = int(fila[9])
                    s_val = int(fila[10])

                    es_valida = ver_sign(p_val, a_val, b_val, q_val, G_val, B_val, m_val, r_val, s_val)
                    resultado = "Válida" if es_valida else "Inválida"

                    print(f"| {nombre} | {m_val} | ({r_val}, {s_val}) | {resultado} |")

                except (ValueError, SyntaxError, TypeError):
                    print(f"| {nombre} | N/A | N/A | Faltan datos o formato erróneo |")

    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo '{ruta_archivo}'. Asegúrate de que esté en la misma carpeta.")


def solve_ecdlp(p, a, q, G, B):
    for d_test in range(1, q):
        P_test = left_right_bin(d_test, G, p, a)

        if P_test == B:
            return d_test

    return None


# Hackeando el ECDSA
def generar_tabla_hackeada(ruta_archivo):
    print("\n| Student Name | Message (m) | Signature (r, s) | Cracked Private Key (d) |")
    print("|---|---|---|---|")

    try:
        with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
            lector = csv.reader(archivo)
            next(lector, None)  # Saltar encabezado

            for fila in lector:
                if len(fila) < 11:
                    continue

                nombre = fila[1].title()

                try:
                    p = int(fila[2])
                    a = int(fila[3])
                    q = int(fila[5])

                    G = ast.literal_eval(fila[6])
                    B = ast.literal_eval(fila[7])

                    m = int(fila[8])
                    r = int(fila[9])
                    s = int(fila[10])

                    if p % 2 == 0:
                        cracked_d = "Invalid Modulus (p is even)"
                    else:
                        cracked_d = "Not Found"
                        for d_test in range(1, q):
                            try:
                                P_test = left_right_bin(d_test, G, p, a)
                                if P_test == B:
                                    cracked_d = str(d_test)
                                    break
                            except Exception:
                                pass

                    print(f"| {nombre} | {m} | ({r}, {s}) | {cracked_d} |")

                except (ValueError, SyntaxError, TypeError):
                    pass

    except FileNotFoundError:
        print(f"\nError: No se encontró el archivo '{ruta_archivo}'.")


def main():
    filename = 'EC_primeorder.txt'
    curves = read_curves(filename)

    if not curves:
        return

    print(f"Successfully loaded {len(curves)} curves from {filename}.\n")

    # Print the selection menu
    for i, curve in enumerate(curves):
        print(f"[{i + 1}] Curve over Field Size p = {curve['p']}")

    # Interactive loop
    while True:
        try:
            print("\n" + "-" * 40)
            choice = input("Enter the number of the curve to load (or 'q' to quit): ")

            if choice.lower() == 'q':
                print("Exiting...")
                break

            index = int(choice) - 1

            if 0 <= index < len(curves):
                selected = curves[index]
                p = selected['p']
                a = selected['a']
                b = selected['b']
                xG = selected['x']
                yG = selected['y']
                q = selected['q']
                print("\n--- Extracted Parameters ---")
                print(f"p = {p}")
                print(f"a = {a}")
                print(f"b = {b}")
                print(f"G = ({xG}, {yG})")
                print(f"q = {q}")

                d, p, a, b, q, G, B = gen_keys(p, a, b, q, (xG, yG, 1))
                print(f"Kpriv (d) = {d}")
                print(f"Kpub (p, a, b, q, G, B) = ({p}, {a}, {b}, {q}, {G}, {B})")

                m = randint(1, q - 1)
                r, s = sign_gen(m, a, p, q, G, d)

                print(f"m = {m}")
                print(f"(r, s) = ({r}, {s})")

                if ver_sign(p, a, b, q, G, B, m, r, s):
                    print("La firma es válida.")
                else:
                    print("La firma es inválida.")

                print("--- All classmate signatures verification ---")

                generar_tabla_ecdsa("data.csv")

                print("--- Breaking the ECDSA ---")

                generar_tabla_hackeada("data.csv")
            else:
                print(f"Invalid selection. Please choose a number between 1 and {len(curves)}.")

        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
