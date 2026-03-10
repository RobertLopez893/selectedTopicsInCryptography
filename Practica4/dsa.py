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
        h = randprime(1, p)
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


if __name__ == '__main__':
    d, p, q, g, beta = gen_key_pair()
    print(f"Private key: {d}. Public Key: ({p}, {q}, {g}, {beta}).")

    m = randint(1, q - 1)
    r, s = gen_sign(m, p, q, g, d)
    print(f"Signature for {m}: ({r}, {s})")

    validation = verify_sign(p, q, g, beta, m, r, s)
    if validation:
        print("La firma es válida.")
    else:
        print("La firma no es válida.")
