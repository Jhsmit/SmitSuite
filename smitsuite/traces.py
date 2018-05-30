import mahotas as mh
import numpy as np
import numpy.core.defchararray as np_str
from skimage.feature import peak_local_max


def find_peaks(image, min_distance=1, threshold_abs=None, threshold_rel=None, exclude_border=True,
               num_peaks=np.inf, footprint=None, Bc='square', max_size=None, verbose=True):

    bin_im = peak_local_max(image, min_distance=min_distance, threshold_abs=threshold_abs,
                            threshold_rel=threshold_rel, exclude_border=exclude_border, num_peaks=num_peaks,
                            footprint=footprint, indices=False)

    struct_elems = {
        'cross': np.array([
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0]]),
        'square': np.ones((3, 3))
    }
    if type(Bc) == str:
        Bc = struct_elems[Bc]
    elif type(Bc) == np.ndarray:
        pass
    else:
        raise TypeError('Invalid structuring element Bc')

    labeled, n = mh.label(bin_im, Bc=Bc)
    l, n1 = mh.labeled.filter_labeled(labeled, max_size=1)
    if verbose and n - n1 != 0:
        print('Found {} flat peaks with size > 1'.format(n - n1))

    if max_size:
        labeled, n = mh.labeled.filter_labeled(labeled, max_size=max_size, remove_bordering=exclude_border)

    return mh.center_of_mass(bin_im, labeled)[1:]


def get_traces(image_stack, xy_coords, box_size=3, func=np.mean):
    assert box_size % 2 == 1
    if np.issubdtype(xy_coords.dtype, np.float):
        print('Input coordinate float converted to integers')
        xy_coords = xy_coords.astype(np.int)

    r = int((box_size - 1) / 2)
    traces = np.stack([func(image_stack[:, y - r:y + r + 1, x - r:x + r + 1], axis=(1, 2)) for y, x in xy_coords])

    return traces


def trace_export(traces, time, x, y):
    index = np.arange(traces.shape[0])
    to_add = [' ', x.astype(int).astype('str'), ' ', y.astype(int).astype('str')]
    header = index.astype('str')
    for entry in to_add:
        header = np_str.add(header, entry)

    header = np.insert(header, 0, 'time (s)')
    export = np.vstack((header,
                        np.vstack((time, traces)).T))

    return export