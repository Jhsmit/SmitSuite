import mahotas as mh
from scipy.signal import medfilt
import mahotas as mh
import pybromo


def multi_erode(img, x):
    img = img.astype(bool)
    for i in range(x):
        img = mh.erode(img)

    return img


def multi_dilate(img, x):
    img = img.astype(bool)
    for i in range(x):
        img = mh.dilate(img)

    return img


def generate_background(image, median_kernel=11, gaussian_kernel=11, dtype=int):
    assert median_kernel % 2 == 1
    assert image.ndim == 2
    sp_m = medfilt(image, kernel_size=median_kernel)

    #fill corners
    cz = int((median_kernel - 1) / 2)
    sp_m[:cz, :cz] = sp_m[cz, cz]
    sp_m[:cz, -cz:] = sp_m[cz, -cz]
    sp_m[-cz:, -cz:] = sp_m[-cz, -cz]
    sp_m[-cz:, :cz] = sp_m[-cz, cz]

    gf = mh.gaussian_filter(sp_m, gaussian_kernel)

    return gf.astype(dtype)