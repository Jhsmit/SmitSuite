import os
import numpy as np

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