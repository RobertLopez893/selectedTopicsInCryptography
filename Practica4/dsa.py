# Práctica 4: DSA.
# López Reyes José Roberto. 7CM1.

from sympy import randprime, isprime
from random import randint

# Key Generation for DSA


def gen_primes():
    q = randprime(11, 1025)
    k = 2

    while True:
        p = k * q + 1

        if isprime(p):
            break

        k += 1

    return p, q


def find_gen(p, q):
    e = (p - 1) // q

    while True:
        h = randint(1, p - 1)
        g = pow(h, e, p)

        if 2 <= g <= p - 1:
            if pow(g, q, p) == 1:
                break

    return g


def gen_key_pair():
    p, q = gen_primes()
    g = find_gen(p, q)
    d = randint(1, q - 1)
    beta = pow(g, d, p)

    return d, p, q, g, beta


# Signature generation
def gen_sign(m, p, q, g, d):
    if not 1 <= m <= q - 1:
        print("Error: m está fuera del rango establecido.")
        return

    ke = randint(1, q - 1)
    r = pow(g, ke, p) % q
    s = ((m + d * r) * pow(ke, -1, q)) % q

    return r, s


# Verification signature
def verify_sign(p, q, g, beta, m, r, s):
    w = pow(s, -1, q)
    u1 = (w * m) % q
    u2 = (w * r) % q
    v = ((pow(g, u1, p) * pow(beta, u2, p)) % p) % q

    if v == r:
        return True
    else:
        return False


def main():
    while True:
        print("\n" + "=" * 40)
        print(" LABORATORIO 04: DSA ")
        print("=" * 40)
        print("1. Ejecutar proceso completo (Llaves automáticas, firma y verificación)")
        print("2. Generar mis llaves y firmar un mensaje")
        print("3. Verificar una firma manual (Ingresar parámetros)")
        print("4. Salir")

        opcion = input("\nSelecciona una opción (1-4): ")

        if opcion == '1':
            print("\n--- PROCESO COMPLETO ---")
            d, p, q, g, beta = gen_key_pair()
            print(f"Private key: {d}. Public Key: ({p}, {q}, {g}, {beta}).")

            m = randint(1, q - 1)
            r, s = gen_sign(m, p, q, g, d)
            print(f"Signature for {m}: ({r}, {s})")

            validation = verify_sign(p, q, g, beta, m, r, s)
            if validation:
                print("-> La firma es válida.")
            else:
                print("-> La firma no es válida.")

        elif opcion == '2':
            print("\n--- GENERACIÓN DE LLAVES Y FIRMA ---")
            d, p, q, g, beta = gen_key_pair()
            print(f"Llave privada (d): {d}")
            print(f"Llave pública (p, q, g, beta): ({p}, {q}, {g}, {beta})")

            try:
                m = int(input(f"\nIngresa el mensaje m (entero entre 1 y {q - 1}): "))
                r, s = gen_sign(m, p, q, g, d)
                if r is not None and s is not None:
                    print(f"Firma generada para el mensaje {m}:")
                    print(f"r = {r}")
                    print(f"s = {s}")
            except ValueError:
                print("Error: Por favor ingresa un número entero válido.")

        elif opcion == '3':
            print("\n--- VERIFICACIÓN DE FIRMA MANUAL ---")
            print("Por favor, ingresa los valores solicitados:")
            try:
                p = int(input("Ingresa p: "))
                q = int(input("Ingresa q: "))
                g = int(input("Ingresa g: "))
                beta = int(input("Ingresa la clave pública beta: "))
                m = int(input("Ingresa el mensaje (m): "))
                r = int(input("Ingresa la firma r: "))
                s = int(input("Ingresa la firma s: "))

                print("\nIniciando verificación...")
                validation = verify_sign(p, q, g, beta, m, r, s)
                if validation:
                    print("-> ¡Resultado: La firma es VÁLIDA!")
                else:
                    print("-> Resultado: La firma es INVÁLIDA.")
            except ValueError:
                print("Error: Todos los parámetros deben ser números enteros.")

        elif opcion == '4':
            print("\nSaliendo del programa... ¡Éxito en tu reporte!")
            break
        else:
            print("\nOpción no válida. Por favor, intenta de nuevo.")


if __name__ == '__main__':
    main()
