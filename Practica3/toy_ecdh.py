# Práctica 3: Toy ECDH.
# López Reyes José Roberto. 7CM1.

import time


# Punto al infinito: (0, 1, 0)
# Resto de puntos: (x, y, 1), con x, y elementos de Zp


def add_points(p, q, n):
    """
    Realiza la suma de dos puntos distintos P y Q sobre una curva elíptica
    en el campo finito módulo 'n'.
    """
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
    """
    Calcula el doble de un punto P (es decir, P + P) sobre una curva elíptica
    en el campo finito módulo 'n' con coeficiente 'a'.
    """
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


def right_left_bin(k, P, p, a):
    k_bin = bin(k)[2:]
    print(f"\nBinario (Right-to-Left): {k_bin}")
    Q = (0, 1, 0)

    for i in range(len(k_bin)):
        print(f"Iteración: {i}")
        if int(k_bin[len(k_bin) - 1 - i]) == 1:
            print("Se va a efectuar adición de puntos por 1.")
            Q = add_points(P, Q, p)
        P = double_point(P, p, a)
        print(f"Q = {Q}")
        print(f"P = {P}")

    return Q


def left_right_bin(k, P, p, a):
    k_bin = bin(k)[2:]
    print(f"\nBinario (Left-to-Right): {k_bin}")
    Q = (0, 1, 0)

    for i in range(len(k_bin)):
        print(f"Iteración: {i}")
        Q = double_point(Q, p, a)
        if int(k_bin[i]) == 1:
            print("Se va a efectuar adición de puntos por 1.")
            Q = add_points(P, Q, p)
        print(f"Q = {Q}")
        print(f"P = {P}")

    return Q


def menu():
    while True:
        try:
            print("\n" + "=" * 50)
            print(" ELLIPTIC CURVE DIFFIE-HELLMAN (ECDH) ".center(50, "="))
            print("=" * 50)
            print("1. Right-to-Left Binary Method")
            print("2. Left-to-Right Binary Method")
            print("3. Simular ECDH (Intercambio de llaves)")
            print("4. Salir")

            opcion = input("\nSelecciona una opción: ")

            if opcion == '1' or opcion == '2':
                print(f"\n--- Algoritmo {opcion} ---")
                p = int(input("Ingresa el módulo (primo p): "))
                a = int(input("Ingresa el coeficiente 'a' de la curva: "))
                x = int(input("Ingresa x del punto P: "))
                y = int(input("Ingresa y del punto P: "))
                k = int(input("Ingresa el escalar k: "))

                inicio = time.perf_counter()

                if opcion == '1':
                    Q = right_left_bin(k, (x, y, 1), p, a)
                else:
                    Q = left_right_bin(k, (x, y, 1), p, a)

                fin = time.perf_counter()

                print(f"\n=> Resultado Q: {Q}")
                print(f"=> Tiempo de ejecución: {fin - inicio:.6f} segundos")

            elif opcion == '3':
                print("\n--- Simulación ECDH ---")
                p = int(input("Ingresa el módulo (primo p): "))
                a = int(input("Ingresa el coeficiente 'a' de la curva: "))
                b = int(input("Ingresa el coeficiente 'b' de la curva: "))
                xg = int(input("Ingresa x del punto Generador G: "))
                yg = int(input("Ingresa y del punto Generador G: "))

                print("\n1. Compute kG (Generar llave pública)")
                print("2. Retrieve secret (Calcular secreto compartido)")
                sub_opc = input("\nSelecciona una sub-opción (1 o 2): ")

                if sub_opc == '1':
                    k = int(input("Selecciona tu valor privado k: "))
                    # Usamos uno de los algoritmos para multiplicar k * G
                    llave_publica = right_left_bin(k, (xg, yg, 1), p, a)
                    print(f"\n=> Tu llave pública calculada (kG) es: {llave_publica}")

                elif sub_opc == '2':
                    x_llave = int(input("Ingrese el valor en x de la llave pública recibida: "))
                    y_llave = int(input("Ingrese el valor en y de la llave pública recibida: "))
                    z_llave = int(input("Ingrese el valor en z de la llave pública recibida (usualmente 1): "))
                    k = int(input("Selecciona tu valor privado k: "))

                    secreto = left_right_bin(k, (x_llave, y_llave, z_llave), p, a)
                    print(f"\n=> El secreto compartido recuperado es: {secreto}")
                else:
                    print("\n[!] Sub-opción no válida.")

            elif opcion == '4':
                print("\nSaliendo del programa. ¡Hasta luego!")
                break

            else:
                print("\n[!] Opción no válida. Por favor, elige 1, 2, 3 o 4.")

        except ValueError:
            print("\n[!] Error: Asegúrate de ingresar únicamente números enteros.")
        except KeyboardInterrupt:
            print("\n\n[!] Ejecución cancelada por el usuario. Saliendo...")
            break


if __name__ == '__main__':
    menu()
