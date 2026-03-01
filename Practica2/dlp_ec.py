# Práctica 2: DLP Over Elliptic Curves.
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


def fold_point(a, b, p, P, k):
    error = (-1, -1, -1)

    if ((4 * pow(a, 3, p)) + (27 * pow(b, 2, p))) % p == 0:
        print("Error: La curva ingresada es singular.")
        return error

    if k <= 2:
        print("Error: El coeficiente k debe ser mayor a 2.")
        return error

    k_bin = bin(k)[2:]

    punto_result = P

    for bit in k_bin[1:]:
        punto_result = double_point(punto_result, p, a)

        if bit == '1':
            punto_result = add_points(punto_result, P, p)

    return punto_result


def dlp_sol(a, b, p, G, P):
    if P == G:
        return 1

    k = 1
    actual = G

    while True:
        if actual == G:
            actual = double_point(actual, p, a)
        else:
            actual = add_points(actual, G, p)

        k += 1

        if k % 100000 == 0:
            print(f"... calculando, vamos en k = {k}")

        if actual == P:
            return k

        if actual == (0, 1, 0):
            print("Se alcanzó el punto al infinito. El logaritmo no existe.")
            return None


def menu():
    """
    Muestra un menú interactivo en consola para probar las distintas
    funciones de la Práctica 2.
    """
    while True:
        print("\n" + "=" * 50)
        print("   Práctica 2: DLP Over Elliptic Curves")
        print("   López Reyes José Roberto. 7CM1.")
        print("=" * 50)
        print("1. Calcular producto escalar (kP)")
        print("2. Romper ECDLP (Fuerza Bruta)")
        print("3. Salir")
        print("=" * 50)

        opcion = input("Elige una opción (1-3): ")

        try:
            if opcion == '1':
                print("\n--- CÁLCULO DE kP ---")
                p = int(input("Ingresa el módulo p: "))
                a = int(input("Ingresa el coeficiente a: "))
                b = int(input("Ingresa el coeficiente b: "))
                x = int(input("Ingresa la coordenada x del punto P: "))
                y = int(input("Ingresa la coordenada y del punto P: "))
                z = int(input("Ingresa la coordenada z del punto P (usualmente 1): "))
                k = int(input("Ingresa el escalar k (k > 2): "))

                P = (x, y, z)
                print("\nCalculando...")
                punto_res = fold_point(a, b, p, P, k)

                if punto_res != (-1, -1, -1):
                    print(f"\n=> El punto resultante {k}P es: {punto_res}")

            elif opcion == '2':
                print("\n--- ROMPER ECDLP ---")

                p = int(input("Ingresa el módulo p: "))
                a = int(input("Ingresa el coeficiente a: "))
                b = int(input("Ingresa el coeficiente b: "))

                print("\nDatos del Generador G:")
                xg = int(input("Ingresa x_G: "))
                yg = int(input("Ingresa y_G: "))
                zg = int(input("Ingresa z_G (usualmente 1): "))

                print("\nDatos del Punto Objetivo P:")
                xp = int(input("Ingresa x_P: "))
                yp = int(input("Ingresa y_P: "))
                zp = int(input("Ingresa z_P (usualmente 1): "))

                G = (xg, yg, zg)
                P = (xp, yp, zp)

                print("\nIniciando ataque de fuerza bruta... (Presiona Ctrl+C para cancelar)")
                inicio = time.perf_counter()

                k_encontrada = dlp_sol(a, b, p, G, P)

                fin = time.perf_counter()
                tiempo_total = fin - inicio

                if k_encontrada:
                    print(f"=> Valor de k: {k_encontrada}")
                    print(f"=> Tiempo de ejecución: {tiempo_total:.4f} segundos")
                    print(f"=> Rendimiento: {k_encontrada / tiempo_total:,.0f} sumas por segundo")

            elif opcion == '3':
                print("\nSaliendo del programa.")
                break

            else:
                print("\nOpción no válida. Por favor, elige 1, 2 o 3.")

        except ValueError:
            print("\nError: Asegúrate de ingresar únicamente números enteros.")
        except KeyboardInterrupt:
            print("\n\n[!] Ejecución detenida manualmente por el usuario (Ctrl+C).")
        except Exception as e:
            print(f"\nOcurrió un error inesperado: {e}")


if __name__ == '__main__':
    menu()
