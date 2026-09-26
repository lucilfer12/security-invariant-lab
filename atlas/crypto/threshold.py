PRIME = 257


def _eval(coeffs, x):
    value = 0
    for coeff in reversed(coeffs):
        value = (value * x + coeff) % PRIME
    return value


def split_secret(secret: bytes, participants: int, threshold: int):
    if participants <= 0 or not 1 <= threshold <= participants or participants >= PRIME:
        raise ValueError("invalid threshold")
    shares = [[] for _ in range(participants)]
    seed = 0
    for byte in secret:
        coeffs = [byte]
        for _ in range(threshold - 1):
            seed = (1103515245 * (seed + byte + 1) + 12345) % PRIME
            coeffs.append(seed)
        for x in range(1, participants + 1):
            shares[x - 1].append(_eval(coeffs, x))
    return [(i + 1, tuple(values)) for i, values in enumerate(shares)]


def combine_secret(shares):
    if not shares:
        raise ValueError("shares required")
    width = len(shares[0][1])
    if any(len(values) != width for _, values in shares):
        raise ValueError("inconsistent share size")
    out = bytearray()
    for position in range(width):
        value = 0
        for i, (x_i, values_i) in enumerate(shares):
            numerator = 1
            denominator = 1
            for j, (x_j, _) in enumerate(shares):
                if i == j:
                    continue
                numerator = (numerator * (-x_j)) % PRIME
                denominator = (denominator * (x_i - x_j)) % PRIME
            basis = numerator * pow(denominator % PRIME, -1, PRIME)
            value = (value + values_i[position] * basis) % PRIME
        out.append(value)
    return bytes(out)
