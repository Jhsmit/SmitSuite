__author__ = 'Jochem Smit'


import numpy as np
import matplotlib.pyplot as plt
from tifffile import imread, imsave
import os
from skimage.feature import register_translation
from scipy.ndimage.interpolation import shift as scipy_shift
from symfit import Parameter, Variable, Fit
import argparse
import sys


class DriftCorrect(object):
    def __init__(self, data_arr):
        self.data_arr = data_arr

    def correct(self, step_size=1, interpolation='poly', upsample_factor=100):
        self.calc_drift(step_size=step_size, interpolation=interpolation, upsample_factor=upsample_factor)
        self.apply_shifts()

        return self.corrected

    def calc_drift(self, step_size=1, interpolation='poly', upsample_factor=100):
        f = np.arange(len(self.data_arr))

        data = self.data_arr[::step_size]
        shifts = list(self.gen_drift_shift(data, upsample_factor=upsample_factor))
        self.x_shift, self.y_shift = np.array(shifts).T
        indices = np.arange(0, len(self.data_arr), step_size)

        if interpolation == 'poly':
            model = self._get_poly(6)
            x_result = Fit(model, indices, self.x_shift).execute()
            y_result = Fit(model, indices, self.y_shift).execute()
            self.x = model(f, **x_result.params)
            self.y = model(f, **y_result.params)
        #
        # if 'deg' in interpolation:
        #     pass
        elif interpolation == 'linear':
            #todo always include last frame
            self.x = np.interp(f, indices, self.x_shift)
            self.y = np.interp(f, indices, self.y_shift)

        return self.x, self.y

    def apply_shifts(self):
        #todo rename x, s_shift also y
        self.corrected = np.array([frame for frame in self._gen_corrected_im(self.x, self.y, self.data_arr)])

    @staticmethod
    def _gen_corrected_im(x, y, data):
        for i, (xs, ys, frame) in enumerate(zip(x, y, data)):
            corrected = scipy_shift(frame, (xs, ys))
            printProgress(i, len(data))
            yield corrected

    def plot_shifts(self):
        #todo catch no drift calculated exception
        f = np.arange(len(self.data_arr))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(f, self.x)
        ax.plot(f, self.y)
        plt.xlabel('Frame number')
        plt.ylabel('Shift')
        plt.show()

    @staticmethod
    def _get_poly(degree):
        x = Variable(name='x')
        params = [Parameter(name='a' + str(i)) for i in range(degree + 1)]
        p = params[0]
        for i in np.arange(1, degree + 1):
            p += params[i] * x ** i

        return p

    @staticmethod
    def gen_drift_shift(data_arr, upsample_factor=100):
        ref_frame = data_arr[0]
        yield (0, 0) # Yield shift for first frame
        for i, frame in enumerate(data_arr[1:]):
            shift, error, diffphase = register_translation(ref_frame, frame, upsample_factor=upsample_factor)

            printProgress(i, len(data_arr) - 1)
            yield shift


#http://scikit-image.org/docs/dev/auto_examples/transform/plot_register_translation.html
class DriftCorrectFile(object):
    def __init__(self, file_path):
        self.file_path = file_path
        print(self.file_path)
        self.data_arr = None

    def read_data(self, **kwargs): # rename
        print("Loading data")
        self.data_arr = imread(self.file_path, **kwargs)
        print("Data successfully loaded")

    def write_data(self, file_path, type='uint16', **kwargs):
        if not 'imagej' in kwargs:
            kwargs['imagej'] = True
        imsave(file_path, self.corrected.astype(type))

    def calc_drift(self, step_size=1, interpolation='poly', upsample_factor=100):
        if not self.data_arr:
            self.read_data()

        #todo add last frame
        f = np.arange(len(self.data_arr))

        data = self.data_arr[::step_size]
        shifts = list(self.gen_drift_shift(data, upsample_factor=upsample_factor))
        self.x_shift, self.y_shift = np.array(shifts).T
        indices = np.arange(0, len(self.data_arr), step_size)

        if interpolation == 'poly':
            model = self._get_poly(6)
            x_result = Fit(model, indices, self.x_shift).execute()
            y_result = Fit(model, indices, self.y_shift).execute()
            self.x = model(f, **x_result.params)
            self.y = model(f, **y_result.params)
        #
        # if 'deg' in interpolation:
        #     pass
        elif interpolation == 'linear':
            #todo always include last frame
            self.x = np.interp(f, indices, self.x_shift)
            self.y = np.interp(f, indices, self.y_shift)

        return self.x, self.y

    def apply_shifts(self):
        #todo rename x, s_shift also y
        self.corrected = np.array([frame for frame in self._gen_corrected_im(self.x, self.y, self.data_arr)])

    @staticmethod
    def _gen_corrected_im(x, y, data):
        for i, (xs, ys, frame) in enumerate(zip(x, y, data)):
            corrected = scipy_shift(frame, (xs, ys))
            printProgress(i, len(data))
            yield corrected

    def plot_shifts(self):
        #todo catch no drift calculated exception
        f = np.arange(len(self.data_arr))

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(f, self.x)
        ax.plot(f, self.y)
        plt.xlabel('Frame number')
        plt.ylabel('Shift')
        plt.show()

    @staticmethod
    def _get_poly(degree):
        x = Variable(name='x')
        params = [Parameter(name='a' + str(i)) for i in range(degree + 1)]
        p = params[0]
        for i in np.arange(1, degree + 1):
            p += params[i] * x ** i

        return p

    @staticmethod
    def gen_drift_shift(data_arr, upsample_factor=100):
        ref_frame = data_arr[0]
        yield (0, 0) # Yield shift for first frame
        for i, frame in enumerate(data_arr[1:]):
            shift, error, diffphase = register_translation(ref_frame, frame, upsample_factor=upsample_factor)

            printProgress(i, len(data_arr) - 1)
            yield shift


#http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
#@Vladimir Ignatyev @Greenstick
def printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = 'X' * filledLength + '-' * (barLength - filledLength)
    line = '\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)
    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stdout.write(line)
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def drift_correct(file_path, step_size=100, upsample_factor=100, verbose=False):
    d = DriftCorrect(file_path)
    d.calc_drift(step_size=step_size, upsample_factor=upsample_factor)
    if verbose:
        d.plot_shifts()
        sys.stdout.write('\n')
        confirm = input("Apply drift correction? [Y/n]")
        if confirm is not '' or 'y':
            return 0

    d.apply_shifts()

    fname = os.path.splitext(os.path.basename(file_path))[0]
    dirname = os.path.dirname(file_path)
    out_dir = os.path.join(dirname, fname + '_corrected.tif')
    d.write_data(out_dir)
    sys.stdout.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Drift correction')
    parser.add_argument('file', help='Input tiff stack file path')
    parser.add_argument('--stepsize', default=100, help='Step size between frames for calculating drift')
    parser.add_argument('--upscalefactor', default=100, help='Upscale factor for images before calculating drift. Determines max resolution')
    #todo add -f to do all files
    #todo interpolation
    args = parser.parse_args()
    d = DriftCorrect(args.file)
    d.calc_drift(step_size=int(args.stepsize), upsample_factor=int(args.upscalefactor))
    d.plot_shifts()

    sys.stdout.write('\n')
    confirm = input("Apply drift correction? [Y/n]")
    if confirm is '' or 'y':
        d.apply_shifts()

        fname = os.path.splitext(os.path.basename(args.file))[0]
        dirname = os.path.dirname(args.file)
        out_dir = os.path.join(dirname, fname + 'corrected.tif')
        d.write_data(out_dir)