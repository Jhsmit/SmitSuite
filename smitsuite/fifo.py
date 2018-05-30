import numpy as np


class FifoFile(object):
    """ Manager for single photon arrival file (.fifo).
    The object is initiated with a file_path but does not proceed to opening the file.
    This is done lazily to conserve resources; 'with FifoFile('file.fifo):' causes to file be opened on runtime.
    When analysis type is selected this runs.
    """

    def __enter__(self):
        return self._read_to_np()

    def __exit__(self, type, value, traceback):
        return False

    def __init__(self, file_path, *args, **kwargs):
        super(FifoFile, self).__init__(*args, **kwargs)
        self.file_path = file_path

    def _read_to_np(self):
        self.data = np.fromfile(self.file_path, dtype='>u4')
        print('data', self.data.dtype)
        # Lowest 10 bits for sync counter
        nsync = np.bitwise_and(self.data, 1023)
        # Next 15 bits for time between photon event and last sync event (not used)
        dtime = np.bitwise_and(np.right_shift(self.data, 10), 32767)  #2**15 -1
        # print(dtime)
        # print(np.unique(dtime))
        # y = np.bincount(dtime.astype('int'))
        # ii = np.nonzero(y)[0]
        # print(zip(ii, y[ii]))

        # Next 6 bit for the channel number, 63 when sync time overflows (macro_time is incremented)
        #!! warning when 32 bit can only do up to ~54 seconds
        channel = np.bitwise_and(np.right_shift(self.data, 25), 63).astype('uint64')
        print(np.unique(channel))


        # Last special bit, 1 when special event, either sync overflow or marker event (not used)
        # special = np.bitwise_and(np.right_shift(self.data, 31), 1)


        # Increment macro time when channel == 63
        macro_time = np.cumsum((channel/63)*1024).astype('uint64')
        print('macro_time', macro_time.dtype)
        print(np.unique(macro_time))
        # Times are kept in integer format for faster correlation
        times = (nsync + macro_time)
        print(times.dtype)

        #Write time data to two ChannelData instances
        ch1_mask = channel == 0
        ch2_mask = channel == 1

        #return np.array([times[ch1_mask], times[ch2_mask]], dtype=[('ch1', 'uint64'), ('ch2', 'uint64')])
        return np.array([times[ch1_mask], times[ch2_mask]])


def apply_binning(photons, binning_time=10e-3, time_resolution=12.5e-9):
    #time data in integer multiples of binning_time
    t = np.floor(photons*(time_resolution / binning_time)).astype('int')
    binned = np.bincount(t)

    max_val = (t.max())*binning_time
    num = int(np.round(max_val / binning_time))  #  need np.round to prevent rounding error in rare cases
    #such as t_arr = 3066471884, 38.3308919 sec
    time = np.linspace(0, max_val, num=num+1)
    assert time.shape == binned.shape
    return time, binned