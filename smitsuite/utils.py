import os
import numpy as np
import re
from symfit import Parameter, Variable, Fit, exp

class CreateDict(dict):
    def __getitem__(self, item):
        try:
            return super(CreateDict, self).__getitem__(item)
        except KeyError:
            self[item] = CreateDict()
            return super(CreateDict, self).__getitem__(item)


def model_gauss2d(a_val, x_mu_val, y_mu_val, sig_x_val, sig_y_val, base, has_base=True):
    a = Parameter(name='a', value=a_val)
    sig_x = Parameter(name='sig_x', value=sig_x_val)
    sig_y = Parameter(name='sig_y', value=sig_y_val)
    x_mu = Parameter(name='x_mu', value=x_mu_val)
    y_mu = Parameter(name='y_mu', value=y_mu_val)

    if has_base:
        b = Parameter(name='b', value=base)
    else:
        b = base
    x_var = Variable(name='x_var')
    y_var = Variable(name='y_var')
    z_var = Variable(name='z_var')

    model = {z_var: a * exp(-(((x_var - x_mu) ** 2 / (2 * sig_x ** 2)) + ((y_var - y_mu) ** 2 / (2 * sig_y ** 2)))) + b}
    return model


def fit_gauss2d(arr):
    Y, X = np.indices(arr.shape)

    total = arr.sum()
    x = (X * arr).sum() / total
    y = (Y * arr).sum() / total
    col = arr[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size) - y) ** 2 * col).sum() / col.sum())
    row = arr[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size) - x) ** 2 * row).sum() / row.sum())
    base = 0

    idx = np.argmax(arr)
    y_mu, x_mu = np.unravel_index(idx, arr.shape)

    print(arr.max(), x_mu, y_mu, width_x, width_y, base)
    model = model_gauss2d(arr.max(), x_mu, y_mu, width_x, width_y, base, has_base=False)

    fit = Fit(model, z_var=arr, x_var=X, y_var=Y)
    return fit.execute(), fit.model


# All credits to giltay
#https://stackoverflow.com/questions/120656/directory-listing-in-python
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def splitname(d):
    return os.path.splitext(os.path.basename(d))[0]


def find_max_square(img, corner=None):
    """
    find the largest subarray in img where all elements are 1

    corner can be any of 'lower_right', 'upper_right', 'lower_left', 'upper_left' to indicate which (if any)
    corner of the images is all 1

    """
    ymax, xmax = img.shape
    img = img.astype('int')

    def get_idx(diffs, y):
        try:
            return np.where(diffs[y] == 1)[0][0]
        except IndexError:
            return np.nan

    if corner == 'lower_right':
        diffs = np.abs(np.diff(img, axis=1))
        ys = np.arange(0, ymax).astype(int)
        xs = np.array([get_idx(diffs, y) for y in ys]).astype(int)
        areas = np.nan_to_num((ymax - ys) * (xmax - xs - 1))
        i = np.where(areas == areas.max())[0][0]

        min1, max1, min2, max2 = ys[i], ymax, xs[i] + 1, xmax

    elif corner == 'upper_right':
        diffs = np.abs(np.diff(img, axis=1))
        ys = np.arange(0, ymax).astype(int)
        xs = np.array([get_idx(diffs, y) for y in ys]).astype(int)

        areas = np.nan_to_num(ys * (xmax - xs))
        i = np.where(areas == areas.max())[0][0]

        min1, max1, min2, max2 = 0, ys[i], xs[i], xmax

    elif corner == 'lower_left':
        diffs = np.abs(np.diff(img, axis=1))
        ys = np.arange(0, ymax).astype(int)
        xs = np.array([get_idx(diffs, y) for y in ys]).astype(int)

        areas = np.nan_to_num((xs + 1) * (ymax - ys))
        i = np.where(areas == areas.max())[0][0]

        min1, max1, min2, max2 = ys[i], ymax, 0, xs[i] + 1

    elif corner == 'upper_left':
        diffs = np.abs(np.diff(img, axis=1))
        ys = np.arange(0, ymax).astype(int)
        xs = np.array([get_idx(diffs, y) for y in ys]).astype(int)

        areas = np.nan_to_num((xs + 1) * (ys + 1))
        i = np.where(areas == areas.max())[0][0]

        min1, max1, min2, max2 = 0, ys[i] + 1, 0, xs[i] + 1

    else:
        return ValueError('Invalid value for corner')

    selection = img[min1:max1, min2:max2]

    assert np.all(selection)
    return min1, max1, min2, max2
	
	

def gen_files(folder=None, ext=None):
    if not folder:
        folder = os.getcwd()
    for path, subdir, files in os.walk(folder):
        for name in files:
            if ext:
                if os.path.splitext(name)[1] == ext:
                    yield os.path.join(path, name)
            else:
                yield os.path.join(path, name)

#todo depracate endswith, startswith
def filter_files(file_list, ext=None, regex=None, endswith=None, startswith=None):
    #todo return list not gen
    for f in file_list:
        filename = os.path.basename(f)
        basename, f_ext = os.path.splitext(filename)
        b = True

        if ext:
            if not ext == f_ext:
                b = False
        if regex: #todo re.match(...)
            match = re.search(regex, filename)
            if not match:
                b = False

        if endswith:
            if not basename[-len(endswith):] == endswith:
                b = False

        if startswith:
            pass

        if b:
            yield f

