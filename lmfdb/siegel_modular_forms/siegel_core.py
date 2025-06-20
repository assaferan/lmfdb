# This file provides functions for computing dimensions of
# collections of Siegel modular forms. It is partly based on
# code implemented together with David Yuen and Fabien Cléry.
#
# Author: Nils Skoruppa <nils.skoruppa@gmail.com>

from sage.all import QQ, ZZ, PowerSeriesRing, is_even, is_prime
from lmfdb.utils import integer_divisors

tbi = 't.b.i.'
uk = '?'


def _dimension_Sp4Z(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms on $Sp(4,Z)$.

    OUTPUT
        ("Total", "Eisenstein", "Klingen", "Maass", "Interesting")
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H_all = 1 / (1 - x ** 4) / (1 - x ** 6) / (1 - x ** 10) / (1 - x ** 12)
    H_Kl = x ** 12 / (1 - x ** 4) / (1 - x ** 6)
    H_MS = (x ** 10 + x ** 12) / (1 - x ** 4) / (1 - x ** 6)
    if is_even(wt):
        a, b, c, d = H_all[wt], 1 if wt >= 4 else 0, H_Kl[wt], H_MS[wt]
        return (a, b, c, d, a - b - c - d)
    else:
        a = H_all[wt - 35]
        return (a, 0, 0, 0, a)


def _dimension_Sp4Z_2(wt):
    """
    Return the dimensions of subspaces of vector-valued Siegel modular forms on $Sp(4,Z)$
    of weight integral,2.

    OUTPUT
        ("Total", "Non-cusp", "Cusp")

    REMARK
        Satoh's paper does not have a description of the cusp forms.
    """
    if not is_even(wt):
        return (uk, uk, uk)
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H = 1 / (1 - x ** 4) / (1 - x ** 6) / (1 - x ** 10) / (1 - x ** 12)
    V = 1 / (1 - x ** 6) / (1 - x ** 10) / (1 - x ** 12)
    # W = 1 / (1 - x ** 10) / (1 - x ** 12)
    a = H[wt - 10] + H[wt - 14] + H[wt - 16] + V[wt - 16] + V[wt - 18] + V[wt - 22]
    return (a, uk, uk)


def _dimension_Sp6Z(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms on $Sp(4,Z)$.

    OUTPUT
    ("Total", "Miyawaki-Type-1", "Miyawaki-Type-2 (conjectured)", "Interesting")
    Remember, Miywaki type 2 is ONLY CONJECTURED!!
    """
    if not is_even(wt):
        return (0, 0, 0, 0)
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    R = PowerSeriesRing(ZZ, 'y', default_prec=2 * wt - 1)
    y = R.gen()
    H_all = 1 / ((1 - x ** 4) * (1 - x ** 12) ** 2 * (1 - x ** 14) * (1 - x ** 18) *
                 (1 - x ** 20) * (1 - x ** 30)) * (
        1 + x ** 6 + x ** 10 + x ** 12 + 3 * x ** 16 + 2 * x ** 18 + 2 * x ** 20
        + 5 * x ** 22 + 4 * x ** 24 + 5 * x ** 26 + 7 * x ** 28 + 6 * x ** 30 + 9 * x ** 32
        + 10 * x ** 34 + 10 * x ** 36 + 12 * x ** 38 + 14 * x ** 40 + 15 * x ** 42 + 16 * x ** 44
        + 18 * x ** 46 + 18 * x ** 48 + 19 * x ** 50 + 21 * x ** 52 + 19 * x ** 54 + 21 * x ** 56
        + 21 * x ** 58 + 19 * x ** 60 + 21 * x ** 62 + 19 * x ** 64 + 18 * x ** 66 + 18 * x ** 68
        + 16 * x ** 70 + 15 * x ** 72 + 14 * x ** 74 + 12 * x ** 76 + 10 * x ** 78 + 10 * x ** 80
        + 9 * x ** 82 + 6 * x ** 84 + 7 * x ** 86 + 5 * x ** 88 + 4 * x ** 90 + 5 * x ** 92
        + 2 * x ** 94 + 2 * x ** 96 + 3 * x ** 98 + x ** 102 + x ** 104 + x ** 108 + x ** 114)
    H_noncusp = 1 / (1 - x ** 4) / (1 - x ** 6) / (1 - x ** 10) / (1 - x ** 12)
    H_E = y ** 12 / (1 - y ** 4) / (1 - y ** 6)
    H_Miyawaki1 = H_E[wt] * H_E[2 * wt - 4]
    H_Miyawaki2 = H_E[wt - 2] * H_E[2 * wt - 2]
    a, b, c, d = H_all[wt], H_noncusp[wt], H_Miyawaki1, H_Miyawaki2
    return (a, c, d, a - b - c - d)


def _dimension_Sp8Z(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms on $Sp(8,Z)$.

    OUTPUT
        ('Total', 'Ikeda lifts', 'Miyawaki lifts', 'Other')
    """
    if wt > 16:
        raise ValueError('Not yet implemented')
    if wt == 8:
        return (1, 1, 0, 0)
    if wt == 10:
        return (1, 1, 0, 0)
    if wt == 12:
        return (2, 1, 1, 0)
    if wt == 14:
        return (3, 2, 1, 0)
    if wt == 16:
        return (7, 2, 2, 3)
    # odd weight is zero up to weight 15
    return (0, 0, 0, 0)


def __S1k(k):
    y = k % 12
    if k < 12:
        return 0
    if y == 2:
        return (k // 12) - 1
    return (k // 12)


def __JacobiDimension(k, m):
    if (k % 2) == 0:
        x = 0
        if k == 2:
            x = (len(integer_divisors(m)) - 1) // 2
        for j in range(1, m + 1):
            x += (__S1k(k + 2 * j) - ((j * j) // (4 * m)))
        return x
    x = 0
    for j in range(1, m):
        x += (__S1k(k + 2 * j - 1) - ((j * j) // (4 * m)))
    return x


def _dimension_Kp(wt, p):
    """
    Return the dimensions of subspaces of Siegel modular forms on $K(p)$
    for primes $p$.

    OUTPUT
        ("Total", "Gritsenko Lifts", "Nonlifts", "Oldforms")
    """
    oldforms = 0
    grits = __JacobiDimension(wt, p)

    if not is_prime(p):
        return (uk, grits, uk, uk)

    if wt <= 1:
        return (0, 0, 0, 0)
    if wt == 2:
        newforms = '?'
        total = '' + str(grits) + ' - ?'
        if p < 600:
            newforms = 0
            total = grits
            interestingPrimes = [277, 349, 353, 389, 461, 523, 587]
            if p in interestingPrimes:
                if p == 587:
                    newforms = '0 - 2'
                    total = '' + str(grits) + ' - ' + str(grits + 2)
                newforms = '0 - 1'
                total = '' + str(grits) + ' - ' + str(grits + 1)
        return (total, grits, newforms, oldforms)

    total = dimKp(wt, p)
    newforms = total - grits - oldforms
    return (total, grits, newforms, oldforms)

    # for nonprime levels:  return ( tbi, grits, tbi, tbi);


def _dimension_Gamma0_2(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms$Gamma0(2)$.

    OUTPUT
        ( "Total", "Eisenstein", "Klingen", "Maass", "Interesting")

    REMARK
        Only total dimension implemented.
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H_all = 1 / (1 - x ** 2) / (1 - x ** 4) / (1 - x ** 4) / (1 - x ** 6)
    # H_cusp  = ??
    # H_Kl   = ??
    # H_MS = ??
    if is_even(wt):
        a = H_all[wt]
        return (a, tbi, tbi, tbi, tbi)
    else:
        a = H_all[wt - 19]
        return (a, 0, 0, 0, a)


def _dimension_Gamma0_3(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms$Gamma0(3)$.

    OUTPUT
        ( "Total", "Eisenstein", "Klingen", "Maass", "Interesting")

    REMARK
        Only total dimension implemented.
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H_all = (1 + 2 * x ** 4 + x ** 6 + x ** 15 * (1 + 2 * x ** 2 + x ** 6)) / (1 - x ** 2) / (1
                                                                                              - x ** 4) / (1 - x ** 6) ** 2
    # H_cusp  = ??
    # H_Kl   = ??
    # H_MS = ??
    if is_even(wt):
        a = H_all[wt]
        return (a, tbi, tbi, tbi, tbi)
    else:
        a = H_all[wt]
        return (a, tbi, tbi, 0, tbi)


def _dimension_Gamma0_3_psi_3(wt):
    r"""
    Return the dimensions of subspaces of Siegel modular forms $Gamma0(3)$
    with character $\psi_3$.

    OUTPUT
        ( "Total", "Eisenstein", "Klingen", "Maass", "Interesting")

    REMARK
        Not completely implemented
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    B = 1 / (1 - x ** 1) / (1 - x ** 3) / (1 - x ** 4) / (1 - x ** 3)
    H_all_odd = B
    H_all_even = B * x ** 14
    # H_cusp  = ??
    # H_Kl   = ??
    # H_MS = ??
    if is_even(wt):
        a = H_all_even[wt]
        return (a, tbi, tbi, tbi, tbi)
    else:
        a = H_all_odd[wt]
        return (a, tbi, tbi, 0, tbi)


def _dimension_Gamma0_4(wt):
    """
    Return the dimensions of subspaces of Siegel modular forms$Gamma0(4)$.

    OUTPUT
        ( "Total", "Eisenstein", "Klingen", "Maass", "Interesting")

    REMARK
        Not completely implemented
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H_all = (1 + x ** 4)(1 + x ** 11) / (1 - x ** 2) ** 3 / (1 - x ** 6)
    # H_cusp  = ??
    # H_Kl   = ??
    # H_MS = ??
    if is_even(wt):
        a = H_all[wt]
        return (a, tbi, tbi, tbi, tbi)
    else:
        a = H_all[wt]
        return (a, tbi, tbi, 0, tbi)


def _dimension_Gamma0_4_psi_4(wt):
    r"""
    Return the dimensions of subspaces of Siegel modular forms $Gamma0(4)$
    with character $\psi_4$.

    OUTPUT
        ( "Total", "Eisenstein", "Klingen", "Maass", "Interesting")

    REMARK
        The formula for odd weights is unknown or not obvious from the paper.
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=wt + 1)
    x = R.gen()
    H_all_even = (x ** 12 + x ** 14) / (1 - x ** 2) ** 3 / (1 - x ** 6)
    # H_cusp  = ??
    # H_Kl   = ??
    # H_MS = ??
    if is_even(wt):
        a = H_all_even[wt]
        return (a, tbi, tbi, tbi, tbi)
    else:
        return (uk, uk, uk, uk, uk)


def _dimension_Gamma0_4_half(k):
    """
    Return the dimensions of subspaces of Siegel modular forms$Gamma0(4)$
    of half integral weight  k - 1/2.

    INPUT
        The realweight is k-1/2

    OUTPUT
        ('Total', 'Non cusp', 'Cusp')

    REMARK
        Note that formula from Hayashida's and Ibukiyama's paper has formula
        that coefficient of x^w is for weight (w+1/2). So here w=k-1.
    """
    R = PowerSeriesRing(ZZ, 'x', default_prec=k)
    x = R.gen()
    H_all = 1 / (1 - x) / (1 - x ** 2) ** 2 / (1 - x ** 3)
    H_cusp = (2 * x ** 5 + x ** 7 + x ** 9 - 2 * x ** 11 + 4 * x ** 6 - x ** 8 + x ** 10 - 3
              * x ** 12 + x ** 14) / (1 - x ** 2) ** 2 / (1 - x ** 6)
    a, c = H_all[k - 1], H_cusp[k - 1]
    return (a, a - c, c)


# David's code for the dimension of S_k(K(p)), originally written by Cris in Maple #########

def H1(k, p):
    return (p ** 2 + 1) * (2 * k - 2) * (2 * k - 3) * (2 * k - 4) / ZZ(2 ** 9 * 3 ** 3 * 5)


def H2(k, p):
    S1 = ((-1) ** k) * (2 * k - 2) * (2 * k - 4) / ZZ(2 ** 8 * 3 ** 2)
    if p == 2:
        S2 = ((-1) ** k) * (2 * k - 2) * (2 * k - 4) / ZZ(2 ** 9)
    else:
        S2 = ((-1) ** k) * (2 * k - 2) * (2 * k - 4) / ZZ(2 ** 7 * 3)
    return S1 + S2


def tink(L, k):
    return QQ(L[k % len(L)])


def LS5(p):
    """
    Gives the Legendre Symbol (5/p)
    """
    return tink([0, 1, -1, -1, 1], p)


def LS2(p):
    """
    Gives the Legendre Symbol (2/p)
    """
    return ZZ.zero() if p == 2 else ZZ(-1)**((p**2 - 1) // 8)


def LSminus1(p):
    """
    Gives the Legendre Symbol (-1/p)
    """
    return ZZ.one() if p == 2 else ZZ(-1)**((p - 1) // 2)


def LSminus3(p):
    """
    Gives the Legendre Symbol (-3/p) ==(p/3)
    """
    return tink([0, 1, -1], p)


def H3(k, p):
    S1 = tink([k - 2, 1 - k, 2 - k, k - 1], k)
    if p == 2:
        S = 5 * S1 / ZZ(2**5 * 3)
    else:
        S = S1 / ZZ(2**4 * 3)
    return S


def H4(k, p):
    S1 = tink([2 * k - 3, 1 - k, 2 - k], k)
    if p == 3:
        S = 5 * S1 / ZZ(2**2 * 3**3)
    else:
        S = S1 / ZZ(2**2 * 3**3)
    return S


def H5(k, p):
    return tink([-1, 1 - k, 2 - k, 1, k - 1, k - 2], k) / ZZ(2**2 * 3**2)


def H6(k, p):
    S = 0
    if ((p % 4) == 1):
        S = 5 * (2 * k - 3) * (p + 1) / ZZ(2**7 * 3) + (-1)**k * (p + 1) / ZZ(2**7)
    if ((p % 4) == 3):
        S = (2 * k - 3) * (p - 1) / ZZ(2**7) + 5 * (-1)**k * (p - 1) / ZZ(2**7 * 3)
    if p == 2:
        S = 3 * (2 * k - 3) / ZZ(2**7) + 7 * (-1)**k / ZZ(2**7 * 3)
    return S


def H7(k, p):
    S = 0
    S1 = 0
    S1 = tink([0, -1, 1], k)
    if (p % 3) == 1:
        S = (2 * k - 3) * (p + 1) / ZZ(2 * 3**3) + S1 * (p + 1) / ZZ(2**2 * 3**3)
    if (p % 3) == 2:
        S = (2 * k - 3) * (p - 1) / ZZ(2**2 * 3**3) + S1 * (p - 1) / ZZ(2 * 3**3)
    if p == 3:
        S = 5 * (2 * k - 3) / ZZ(2**2 * 3**3) + S1 / ZZ(3**3)
    return S


def H8(k, p):
    return tink([1, 0, 0, -1, -1, -1, -1, 0, 0, 1, 1, 1], k) / ZZ(2 * 3)


def H9(k, p):
    S1 = tink([1, 0, 0, -1, 0, 0], k)
    if p == 2:
        S = S1 / ZZ(2 * 3**2)
    else:
        S = 2 * S1 / ZZ(3**2)
    return S


def H10(k, p):
    S1 = tink([1, 0, 0, -1, 0], k)
    return (LS5(p) + 1) * S1 / ZZ(5)


def H11(k, p):
    S1 = tink([1, 0, 0, -1], k)
    S = (LS2(p) + 1) * S1 / ZZ(2**3)
    if p == 2:
        S = S1 / ZZ(2**3)
    return S


def H12(k, p):
    S1 = tink([0, 1, -1], k) / ZZ(2 * 3)
    S2 = (-1)**k / ZZ(2 * 3)
    S3 = (-1)**k / ZZ(2**2 * 3)
    S = tink([0, S1, 0, 0, 0, 0, 0, 0, 0, 0, 0, S2], p)
    if p == 2:
        S = S3
    if p == 3:
        S = S3
    return S


def H(k, p):
    S = H1(k, p) + H2(k, p) + H3(k, p) + H4(k, p) + H5(k, p) + H6(k, p)
    S += H7(k, p) + H8(k, p) + H9(k, p) + H10(k, p) + H11(k, p) + H12(k, p)
    return S


def I1(k, p):
    S1 = tink([0, 1, 1, 0, -1, -1], k)
    return S1 / ZZ(6)


def I2(k, p):
    S1 = tink([-2, 1, 1], k)
    return S1 / ZZ(2 * 3**2)


def I3(k, p):
    S1 = tink([-2, 1, 1], k) / ZZ(3**2)
    S2 = 2 * tink([-1, 1, 0], k) / ZZ(3**2)
    S3 = 2 * tink([-1, 0, 1], k) / ZZ(3**2)
    S = tink([0, S2, S3], p)
    if p == 3:
        S = S1
    return S


def I4(k, p):
    S1 = tink([-1, 1, 1, -1], k)
    return S1 / ZZ(2**2)


def I5(k, p):
    return (-1)**k / ZZ(2**3)


def I6(k, p):
    return (2 - LSminus1(p)) * (-1)**k / ZZ(2**4)


def I7(k, p):
    return -(-1)**k * (2 * k - 3) / ZZ(2**3 * 3)


def I8(k, p):
    return -p * (2 * k - 3) / ZZ(2**4 * 3**2)


def I9(k, p):
    return QQ(-1) / ZZ(2**3 * 3)


def I10(k, p):
    return (p + 1) / ZZ(2**3 * 3)


def I11(k, p):
    return (1 + LSminus1(p)) * (-1) / ZZ(8)


def I12(k, p):
    return (1 + LSminus3(p)) * (-1) / ZZ(6)


def II(k, p):
    S = I1(k, p) + I2(k, p) + I3(k, p) + I4(k, p) + I5(k, p) + I6(k, p)
    S += I7(k, p) + I8(k, p) + I9(k, p) + I10(k, p) + I11(k, p) + I12(k, p)
    return S


def dimKp(k, p):
    """
    This returns the dimension of cusp forms for K(p)
    of weight k>=3 and PRIME level p
    """
    S = H(k, p) + II(k, p)
    if k == 3:
        S = H(k, p) + II(k, p) + 1
    return S
