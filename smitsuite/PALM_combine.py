import bioformats as bf
import javabridge
import tifffile
import numpy as np
import os
import itertools


def read_stack(file_path, axis='T'):
    xml = bf.OMEXML(bf.get_omexml_metadata(file_path))
    sizeZ = xml.image().Pixels.SizeZ
    sizeC = xml.image().Pixels.SizeC
    sizeT = xml.image().Pixels.SizeT
    sizeX = xml.image().Pixels.SizeX
    sizeY = xml.image().Pixels.SizeY

    axes = {'z': sizeZ, 'c': sizeC, 't': sizeT}
    ax3 = axes[axis.lower()]

    out_arr = np.zeros((ax3, sizeX, sizeY), dtype='uint16')
    with bf.ImageReader(file_path) as r:
        for i in range(ax3):
            kwargs = {axis.lower(): i}
            im = r.read(rescale=False, **kwargs)
            out_arr[i] = im

    return out_arr


def _stack_all(data_dir, output_dir, axis='T'):

    l = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    keyfunc = lambda x: x[:-3]

    groups = []
    keys = []
    for k, g in itertools.groupby(l, key=keyfunc):
        groups.append(list(g))
        keys.append(k)

    for k, g in zip(keys, groups):
        stack = np.concatenate(
            [read_stack(os.path.join(data_dir, f, 'stack1', 'frame_t_0.ets'), axis=axis) for f in g],
            axis=0)
        tifffile.imsave(os.path.join(output_dir, k + '.tif'), stack)


def stack_all(data_dir, output_dir, axis='T'):
    javabridge.start_vm(class_path=bf.JARS, run_headless=True)
    _stack_all(data_dir, output_dir, axis=axis)
    javabridge.kill_vm()


def start_vm():
    javabridge.start_vm(class_path=bf.JARS, run_headless=True)

def stop_vm():
    javabridge.kill_vm()

if __name__ == '__main__':
    data_dir = r'C:\Users\Smit\Data\20170524_yichen_ecoli_uptake\20170524DH5_250nM_NeoBRhoB'
    output_dir = r'C:\Users\Smit\Data\20170524_yichen_ecoli_uptake'
    stack_all(data_dir, output_dir)