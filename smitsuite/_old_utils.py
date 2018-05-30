import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns


def _get_appdata_path():
    import ctypes
    from ctypes import wintypes, windll
    CSIDL_APPDATA = 26
    _SHGetFolderPath = windll.shell32.SHGetFolderPathW
    _SHGetFolderPath.argtypes = [wintypes.HWND,
                                 ctypes.c_int,
                                 wintypes.HANDLE,
                                 wintypes.DWORD,
                                 wintypes.LPCWSTR]
    path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
    result = _SHGetFolderPath(0, CSIDL_APPDATA, 0, 0, path_buf)
    return path_buf.value

def dropbox_home():
    from platform import system
    import base64
    import os
    import platform

    if platform.platform() == 'Windows-8-6.2.9200':  # HP LAptop
        host_db_path = os.path.join(os.getenv('LOCALAPPDATA'),
                                    'Dropbox',
                                    'host.db')

    elif _system in ('Windows', 'cli'):
        host_db_path = os.path.join(_get_appdata_path(),
                                    'Dropbox',
                                    'host.db')
    elif _system in ('Linux', 'Darwin'):
        host_db_path = os.path.expanduser('~'
                                          '/.dropbox'
                                          '/host.db')
    else:
        raise RuntimeError('Unknown system={}'
                           .format(_system))


    if not os.path.exists(host_db_path):
        raise RuntimeError("Config path={} doesn't exists"
                           .format(host_db_path))
    with open(host_db_path, 'r') as f:
        data = f.read().split()

    return base64.b64decode(data[1])

def set_wkdir(path=''):
    import os
    dropbox_path = dropbox_home()
    os.chdir(dropbox_path + '/wkdir' + '/' + path)

def rolling_window(a, w):
    #http://stackoverflow.com/questions/6811183/rolling-window-for-1d-arrays-in-numpy
    shape = a.shape[:-1] + (a.shape[-1] - w + 1, w)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def plot_line(*args, **kwargs):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(*args, **kwargs)
    plt.show()

def plot_2d(*args, **kwargs):

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(*args, **kwargs)
    plt.show()

#jasco files
class JascoFile(object):
    def __init__(self, path):
        self.path = path
        from jwslib import read_file
        t = read_file(self.path)
        self.header = t[1]

        if t[0] != 0:
            print t[1]
            raise Exception("Invalid file")

        if len(t[2]) == 1:
            self.y_data = np.array(t[2][0])
            self.y_data_norm = (self.y_data - self.y_data.min()) / (self.y_data.max() - self.y_data.min())
        else:
            raise Exception("Multiple channels")

        self.x_data = np.linspace(self.header.x_for_first_point, self.header.x_for_last_point, num=self.header.point_number)


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


def gen_files():
    for path, subdir, files in os.walk(os.getcwd()):
        for name in files:
            yield os.path.join(path, name)

def filter_files(ext, startwith=None, endwith=None, notendwith=None):
    for filename in gen_files():
        b_ext = os.path.splitext(filename)[1] == ext
        filebasename = os.path.splitext(os.path.basename(filename))[0]
        b_endwith, b_notendwith, b_startwith = True, True, True
        if startwith:
            b_startwith = filebasename[:len(startwith)] == startwith
        if endwith:
            b_endwith = filebasename[-len(endwith):] == name_endwith
        if notendwith:
            b_notendwith = filebasename[-len(notendwith):] != notendwith


        bools = np.array([b_ext, b_startwith, b_endwith, b_notendwith])
        if np.all(bools):
            yield filename


def batch_jws():
    files = [filename for filename in gen_files() if os.path.splitext(filename)[1] == '.jws']
    for f in files:
        print f
        js_file = JascoFile(f)
        js_file.export_ascii()
        js_file.export_plot()

def rec_split(path):
    rest, tail = os.path.split(path)
    while rest not in ('', os.path.sep, 'C:\\'):
        yield tail
        rest, tail = os.path.split(rest)

if __name__ == '__main__':
    import platform
    print platform.platform()
    import sys
    print sys.getwindowsversion()
    print os.getenv('LOCALAPPDATA')
    print _get_appdata_path()
    print dropbox_home()