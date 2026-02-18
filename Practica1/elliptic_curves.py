# Práctica 1: Elliptic Curves.
# López Reyes José Roberto. 7CM1.
import random

from Crypto.Util.number import getPrime, isPrime, getRandomInteger
# Punto al infinito: (0, 1, 0)
# Resto de puntos: (x, y, 1), con x, y elementos de Zp


def find_a_b(p):
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
    p = getPrime(bits)

    while True:
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)

        if ((4 * pow(a, 3, p)) + (27 * pow(b, 2, p))) % p != 0:
            return p, [a, b]


def rational_points(p, a, b):
    points = []
    qr = []
    sr = []

    if p <= 3 or not isPrime(p):
        print("El número debe ser primo y mayor a 3.")
        return points

    points.append((0, 1, 0))

    for x in range(p):
        r = pow(x, 2, p)
        sr.append([r, x])
        if r not in qr:
            qr.append(r)

    print(qr)
    print(sr)

    for x in range(p):
        pass


def add_points(p, q):
    pass


def double_point(p):
    pass


if __name__ == '__main__':
    p = 19
    # p = getPrime(3)
    print(p)
    curvas = find_a_b(p)
    print(curvas)
    print(f"Hay {len(curvas)} curvas posibles.")

    p2, coefs = find_by_bits(2048)
    print(f"Prime: {p2}.")
    print(f"a = {coefs[0]}\nb = {coefs[1]}.")

    rational_points(11, 1, 1)
