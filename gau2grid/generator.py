"""
This is a Python-based automatic generator.
"""

import numpy as np


def numpy_generator(L, function_name="generated_compute_numpy_shells"):

    # Builds a few tmps
    s1 = "    "
    s2 = "    " * 2
    s3 = "    " * 3

    ret = []
    ret.append("def %s(xyz, L, coeffs, exponents, center, grad=2):" % function_name)

    ret.append("")
    ret.append(s1 + "# Make sure NumPy is in locals")
    ret.append(s1 + "import numpy as np")
    ret.append("")

    ret.append(s1 + "# Unpack shell data")
    ret.append(s1 + "nprim = len(coeffs)")
    ret.append(s1 + "npoints = xyz.shape[0]")
    ret.append("")

    ret.append(s1 + "# First compute the diff distance in each cartesian")
    ret.append(s1 + "xc = xyz[:, 0] - center[0]")
    ret.append(s1 + "yc = xyz[:, 1] - center[1]")
    ret.append(s1 + "zc = xyz[:, 2] - center[2]")
    ret.append(s1 + "R2 = xc * xc + yc * yc + zc * zc")
    ret.append("")

    ret.append(s1 + "# Build up the derivates in each direction")
    ret.append(s1 + "V1 = np.zeros((npoints))")
    ret.append(s1 + "V2 = np.zeros((npoints))")
    ret.append(s1 + "V3 = np.zeros((npoints))")
    ret.append(s1 + "for K in range(nprim):")
    ret.append(s1 + "    T1 = coeffs[K] * np.exp(-exponents[K] * R2)")
    ret.append(s1 + "    T2 = -2.0 * exponents[K] * T1")
    ret.append(s1 + "    T3 = -2.0 * exponents[K] * T2")
    ret.append(s1 + "    V1 += T1")
    ret.append(s1 + "    V2 += T2")
    ret.append(s1 + "    V3 += T3")
    ret.append("")
    ret.append(s1 + "S0 = V1.copy()")
    ret.append(s1 + "SX = V2 * xc")
    ret.append(s1 + "SY = V2 * yc")
    ret.append(s1 + "SZ = V2 * zc")
    ret.append(s1 + "SXY = V3 * xc * yc")
    ret.append(s1 + "SXZ = V3 * xc * zc")
    ret.append(s1 + "SYZ = V3 * yc * zc")
    ret.append(s1 + "SXX = V3 * xc * xc + V2")
    ret.append(s1 + "SYY = V3 * yc * yc + V2")
    ret.append(s1 + "SZZ = V3 * zc * zc + V2")
    ret.append("")

    ret.append(s1 + "# Power matrix for higher angular momenta")
    ret.append(s1 + "xc_pow = np.zeros((L + 1, npoints))")
    ret.append(s1 + "yc_pow = np.zeros((L + 1, npoints))")
    ret.append(s1 + "zc_pow = np.zeros((L + 1, npoints))")
    ret.append("")
    ret.append(s1 + "xc_pow[0] = 1.0")
    ret.append(s1 + "yc_pow[0] = 1.0")
    ret.append(s1 + "zc_pow[0] = 1.0")

    ret.append(s1 + "for LL in range(1, L + 1):")
    ret.append(s1 + "    xc_pow[LL] = xc_pow[LL - 1] * xc")
    ret.append(s1 + "    yc_pow[LL] = yc_pow[LL - 1] * yc")
    ret.append(s1 + "    zc_pow[LL] = zc_pow[LL - 1] * zc")
    ret.append("")

    ret.append(s1 + "# Allocate data")
    ret.append(s1 + "ncart = int((L + 1) * (L + 2) / 2)")
    ret.append("")

    ret.append(s1 + "output = {}")
    ret.append(s1 + "output['PHI'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "if grad > 0:")
    ret.append(s1 + "    output['PHI_X'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_Y'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_Z'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "if grad > 1:")
    ret.append(s1 + "    output['PHI_XX'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_YY'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_ZZ'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_XY'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_XZ'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "    output['PHI_YZ'] = np.zeros((ncart, npoints))")
    ret.append(s1 + "if grad > 2:")
    ret.append(s1 + "    raise ValueError('Only grid derivatives through Hessians (grad = 2) has been implemented')")
    ret.append("")

    ret.append("# Angular momentum loops")
    for l in range(L + 1):
        ret.append(s1 + "if L == %d:" % l)
        ret.extend(_numpy_am_build(l, s2))

    ret.append(s1 + "return output")

    return "\n".join(ret)


def _numpy_am_build(L, spacer=""):
    ret = []
    names = ["X", "Y", "Z"]
    # Generator
    idx = 0
    for i in range(L + 1):
        l = L - i + 2
        for j in range(i + 1):
            m = i - j + 2
            n = j + 2

            ld1 = l - 1
            ld2 = l - 2
            md1 = m - 1
            md2 = m - 2
            nd1 = n - 1
            nd2 = n - 2

            # Set grads back to zero
            x_grad, y_grad, z_grad = False, False, False

            name = "X" * ld2 + "Y" * md2 + "Z" * nd2
            if name == "":
                name = "0"

            # Density
            ret.append("# Density AM=%d Component=%s" % (L, name))

            # AX = _build_xyz_pow("A", 1.0, l, m, n)
            ret.append(spacer + _build_xyz_pow("A", 1.0, l, m, n))
            ret.append(spacer + "output['PHI'][%d] = S0 * A" % idx)

            # Gradient
            ret.append("# Gradient AM=%d Component=%s" % (L, name))
            ret.append(spacer + "output['PHI_X'][%d] = SX * A" % idx)
            ret.append(spacer + "output['PHI_Y'][%d] = SY * A" % idx)
            ret.append(spacer + "output['PHI_Z'][%d] = SZ * A" % idx)

            AX = _build_xyz_pow("AX", ld2, ld1, m, n)
            if AX is not None:
                x_grad = True
                ret.append(spacer + AX)
                ret.append(spacer + "output['PHI_X'][%d] += S0 * AX" % idx)

            AY = _build_xyz_pow("AY", md2, l, md1, n)
            if AY is not None:
                y_grad = True
                ret.append(spacer + AY)
                ret.append(spacer + "output['PHI_Y'][%d] += S0 * AY" % idx)

            AZ = _build_xyz_pow("AZ", nd2, l, m, nd1)
            if AZ is not None:
                z_grad = True
                ret.append(spacer + AZ)
                ret.append(spacer + "output['PHI_Z'][%d] += S0 * AZ" % idx)

            # Hessian temporaries
            ret.append("# Hessian AM=%d Component=%s" % (L, name))

            # S Hess
            # We will build S Hess, grad 1, grad 2, A Hess

            # XX
            ret.append(spacer + "output['PHI_XX'][%d] = SXX * A" % idx)
            if x_grad:
                ret.append(spacer + "output['PHI_XX'][%d] += SX * AX" % idx)
                ret.append(spacer + "output['PHI_XX'][%d] += SX * AX" % idx)

            AXX = _build_xyz_pow("AXX", ld2 * (ld2 - 1), ld2, m, n)
            if AXX is not None:
                ret.append(spacer + AXX)
                ret.append(spacer + "output['PHI_XX'][%d] += S0 * AXX" % idx)

            # YY
            ret.append(spacer + "output['PHI_YY'][%d] = SYY * A" % idx)
            if y_grad:
                ret.append(spacer + "output['PHI_YY'][%d] += SY * AY" % idx)
                ret.append(spacer + "output['PHI_YY'][%d] += SY * AY" % idx)
            AYY = _build_xyz_pow("AYY", md2 * (md2 - 1), l, md2, n)
            if AYY is not None:
                ret.append(spacer + AYY)
                ret.append(spacer + "output['PHI_YY'][%d] += S0 * AYY" % idx)

            # ZZ
            ret.append(spacer + "output['PHI_ZZ'][%d] = SZZ * A" % idx)
            if z_grad:
                ret.append(spacer + "output['PHI_ZZ'][%d] += SZ * AZ" % idx)
                ret.append(spacer + "output['PHI_ZZ'][%d] += SZ * AZ" % idx)
            AZZ = _build_xyz_pow("AZZ", nd2 * (nd2 - 1), l, m, nd2)
            if AZZ is not None:
                ret.append(spacer + AZZ)
                ret.append(spacer + "output['PHI_ZZ'][%d] += S0 * AZZ" % idx)

            # XY
            ret.append(spacer + "output['PHI_XY'][%d] = SXY * A" % idx)

            if y_grad:
                ret.append(spacer + "output['PHI_XY'][%d] += SX * AY" % idx)
            if x_grad:
                ret.append(spacer + "output['PHI_XY'][%d] += SY * AX" % idx)

            AXY = _build_xyz_pow("AXY", ld2 * md2, ld1, md1, n)
            if AXY is not None:
                ret.append(spacer + AXY)
                ret.append(spacer + "output['PHI_XY'][%d] += S0 * AXY" % idx)

            # XZ
            ret.append(spacer + "output['PHI_XZ'][%d] = SXZ * A" % idx)
            if z_grad:
                ret.append(spacer + "output['PHI_XZ'][%d] += SX * AZ" % idx)
            if x_grad:
                ret.append(spacer + "output['PHI_XZ'][%d] += SZ * AX" % idx)
            AXZ = _build_xyz_pow("AXZ", ld2 * nd2, ld1, m, nd1)
            if AXZ is not None:
                ret.append(spacer + AXZ)
                ret.append(spacer + "output['PHI_XZ'][%d] += S0 * AXZ" % idx)

            # YZ
            ret.append(spacer + "output['PHI_YZ'][%d] = SYZ * A" % idx)
            if z_grad:
                ret.append(spacer + "output['PHI_YZ'][%d] += SY * AZ" % idx)
            if y_grad:
                ret.append(spacer + "output['PHI_YZ'][%d] += SZ * AY" % idx)
            AYZ = _build_xyz_pow("AYZ", md2 * nd2, l, md1, nd1)
            if AYZ is not None:
                ret.append(spacer + AYZ)
                ret.append(spacer + "output['PHI_YZ'][%d] += S0 * AYZ" % idx)

            idx += 1
            ret.append(" ")

    return ret


def _build_xyz_pow(name, pref, l, m, n, shift=2):
    l = l - shift
    m = m - shift
    n = n - shift

    if (pref <= 0) or (l < 0) or (n < 0) or (m < 0):
        return None

    mul = " "
    if pref == 1:
        ret = name + " ="
    else:
        ret = name + " = %d" % pref
        mul = " * "

    if l > 0:
        ret += mul + "xc_pow[%d]" % l
        mul = " * "

    if m > 0:
        ret += mul + "yc_pow[%d]" % m
        mul = " * "

    if n > 0:
        ret += mul + "zc_pow[%d]" % n
        mul = " * "

    if mul == " ":
        ret += " 1"

    return ret
