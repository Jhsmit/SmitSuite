import numba
import numpy as np


@numba.jit
def acorrelate(t):

    acf = np.zeros(t.size, dtype=float)
    for lag in range(acf.size):
        acf[lag] = (t[:t.size-lag] * t[lag:]).mean()

    return acf





    #
    #
    #
    # if maxlag is None:
    #     maxlag = u.size
    # maxlag = int(min(u.size, maxlag))
    # C = np.zeros(maxlag, dtype=np.int64)
    # for lag in range(C.size):
    #     tmax = min(u.size - lag, t.size)
    #     umax = min(u.size, t.size + lag)
    #     C[lag] = (t[:tmax] * u[lag:umax]).sum()
    # return C