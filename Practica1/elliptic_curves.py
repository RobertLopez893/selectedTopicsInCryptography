# Práctica 1: Elliptic Curves.
# López Reyes José Roberto. 7CM1.
import random
from Crypto.Util.number import getPrime, isPrime

# Punto al infinito: (0, 1, 0)
# Resto de puntos: (x, y, 1), con x, y elementos de Zp


def raiz_cuadrada_modular(z, p):
    """
    Calcula la raíz cuadrada modular de z módulo p usando el algoritmo de Tonelli-Shanks.
    Si p % 4 == 3, utiliza una fórmula directa.
    """
    if p % 4 == 3:
        return pow(z, (p + 1) // 4, p)

    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1

    z_n = 2
    while pow(z_n, (p - 1) // 2, p) != p - 1:
        z_n += 1

    m = s
    c = pow(z_n, q, p)
    t = pow(z, q, p)
    r = pow(z, (q + 1) // 2, p)

    while t != 0 and t != 1:
        t2i = t
        i = 0
        for i in range(1, m):
            t2i = pow(t2i, 2, p)
            if t2i == 1:
                break

        b = pow(c, 2 ** (m - i - 1), p)
        m = i
        c = pow(b, 2, p)
        t = (t * c) % p
        r = (r * b) % p

    return r


def find_a_b(p):
    """
    Encuentra y devuelve todas las parejas de coeficientes (a, b) válidas
    para formar una curva elíptica sobre el campo primo p.
    """
    curvas = []

    if isPrime(p):
        if p > 3:
            for a in range(p):
                for b in range(p):
                    if ((4 * pow(a, 3, p)) + (27 * pow(b, 2, p))) % p != 0:
                        curvas.append((a, b))
        else:
            print("El primo debe ser mayor a 3.")
    else:
        print("El valor debe ser primo.")

    return curvas


def find_by_bits(bits):
    """
    Genera aleatoriamente un número primo 'p' de tamaño 'bits'
    y encuentra un par de coeficientes (a, b) válidos para una curva elíptica.
    """
    p = getPrime(bits)

    while True:
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)

        if ((4 * pow(a, 3, p)) + (27 * pow(b, 2, p))) % p != 0:
            return p, [a, b]


def rational_points(p, a, b):
    """
    Calcula y devuelve todos los puntos racionales (x, y, 1) que pertenecen
    a la curva elíptica definida por y^2 = x^3 + ax + b (mod p).
    Incluye el punto al infinito (0, 1, 0).
    """
    points = []

    if p <= 3:
        print("El número debe ser primo y mayor a 3.")
        return points

    points.append((0, 1, 0))

    for x in range(p):
        z = (pow(x, 3, p) + (a * x) % p + b) % p

        if z == 0:
            points.append((x, 0, 1))

        elif pow(z, (p - 1) // 2, p) == 1:
            y = raiz_cuadrada_modular(z, p)

            points.append((x, y, 1))
            points.append((x, p - y, 1))

    return points


def add_points(p, q, n):
    """
    Realiza la suma de dos puntos distintos P y Q sobre una curva elíptica
    en el campo finito módulo 'n'.
    """
    x1, x2, y1, y2 = p[0], q[0], p[1], q[1]

    if x1 == x2:
        return

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
    x1, x2 = p[0], p[0]
    y1, y2 = p[1], p[1]

    pendiente = ((3 * pow(x1, 2, n) + a) % n) * pow((2 * y1), -1, n)

    x3 = (pow(pendiente, 2, n) - x1 - x2) % n
    y3 = (pendiente * (x1 - x3) - y1) % n

    addition = (x3, y3, 1)

    return addition


def menu():
    """
    Muestra un menú interactivo en consola para probar las distintas
    funciones de la práctica de curvas elípticas.
    """
    while True:
        print("\n" + "=" * 50)
        print("   Práctica 1: Elliptic Curves")
        print("   López Reyes José Roberto. 7CM1.")
        print("=" * 50)
        print("1. Encontrar curvas (a, b) válidas para un primo 'p'")
        print("2. Generar parámetros (p, a, b) por tamaño de bits")
        print("3. Encontrar puntos racionales de una curva")
        print("4. Sumar dos puntos P y Q")
        print("5. Doblar un punto P")
        print("6. Salir")
        print("=" * 50)

        opcion = input("Elige una opción (1-6): ")

        try:
            if opcion == '1':
                p = int(input("Ingresa el número primo p: "))
                curvas = find_a_b(p)
                if curvas:
                    print(f"\n=> Se encontraron {len(curvas)} curvas posibles.")
                    ver = input("¿Deseas imprimir todas las combinaciones? (s/n): ").lower()
                    if ver == 's':
                        print(curvas)

            elif opcion == '2':
                bits = int(input("Ingresa el tamaño en bits (ej. 1024, 2048): "))
                p2, coefs = find_by_bits(bits)
                print(f"\n=> Prime generado: {p2}")
                print(f"=> Coeficientes válidos: a = {coefs[0]}, b = {coefs[1]}")

            elif opcion == '3':
                p = int(input("Ingresa el primo p: "))
                a = int(input("Ingresa el coeficiente a: "))
                b = int(input("Ingresa el coeficiente b: "))
                points = rational_points(p, a, b)
                if points:
                    print(f"\n=> Hay {len(points)} puntos racionales en esta curva.")
                    ver = input("¿Deseas imprimir todos los puntos? (s/n): ").lower()
                    if ver == 's':
                        print(points)

            elif opcion == '4':
                n = int(input("Ingresa el módulo (primo n): "))
                x1 = int(input("Ingresa x del punto P: "))
                y1 = int(input("Ingresa y del punto P: "))
                x2 = int(input("Ingresa x del punto Q: "))
                y2 = int(input("Ingresa y del punto Q: "))

                punto_P = (x1, y1, 1)
                punto_Q = (x2, y2, 1)

                resultado = add_points(punto_P, punto_Q, n)
                print(f"\n=> La suma de {punto_P} + {punto_Q} es: {resultado}")

            elif opcion == '5':
                n = int(input("Ingresa el módulo (primo n): "))
                a = int(input("Ingresa el coeficiente 'a' de la curva: "))
                x1 = int(input("Ingresa x del punto P: "))
                y1 = int(input("Ingresa y del punto P: "))

                punto_P = (x1, y1, 1)

                resultado = double_point(punto_P, n, a)
                print(f"\n=> El doble del punto {punto_P} es: {resultado}")

            elif opcion == '6':
                print("\nSaliendo del programa...")
                break

            else:
                print("\nOpción no válida. Por favor, elige un número del 1 al 6.")

        except ValueError:
            print("\nError: Asegúrate de ingresar únicamente números enteros donde se solicitan.")
        except Exception as e:
            print(f"\nOcurrió un error inesperado durante el cálculo: {e}")


if __name__ == '__main__':
    menu()
