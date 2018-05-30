from atomicplot.fileIO import JWSFile
from atomicplot.utils import gen_files, filter_files
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os


def main(folder=None, type='mpl'):
    file_list = filter_files(gen_files(folder), ext='.jws')
    jws_list = [JWSFile(file_path).to_dataobject() for file_path in file_list]

    for jws in jws_list:

def export_ascii(self):
    export_data = np.column_stack((self.x_data, self.y_data, self.y_data_norm))
    name = os.path.splitext(self.path)[0] + '.txt'
    np.savetxt(name, export_data, fmt='%10.5f')


def export_plot(self):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(self.x_data, self.y_data, linewidth=2)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(os.path.basename(self.path))
    plt.savefig(os.path.splitext(self.path)[0] + '.png')
    plt.close()



if __name__ == '__main__':
    file_list = filter_files(gen_files(), ext='.jws')
