def berlekamp_massey(s):
    n = len(s)
    c = [1.0]
    b = [1.0]
    L = 0
    m = 1
    b_val = 1.0
    for i in range(n):
        d = 0.0
        for j in range(L + 1):
            if i - j >= 0 and j < len(c):
                d += c[j] * s[i - j]
        if abs(d) < 1e-9:
            m += 1
        else:
            t = c[:]
            coef = d / b_val
            for j in range(len(b)):
                if m + j >= len(c):
                    c.append(0.0)
                c[m + j] -= coef * b[j]
            if 2 * L <= i:
                L = i + 1 - L
                b = t
                b_val = d
                m = 1
            else:
                m += 1
    return c

seq = [1, 3, 11, 45, 199, 929, 4505, 22459]
# Add 9 and 10 to check if BM can find a relation
# Since we only have 8 terms, BM can find a relation of degree up to 4.
poly = berlekamp_massey(seq)
print("Berlekamp-Massey Poly for first 8 terms:", [round(x, 2) for x in poly])
