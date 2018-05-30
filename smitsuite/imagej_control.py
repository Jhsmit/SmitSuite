import subprocess
import os
#http://forum.imagej.net/t/running-multiple-instances-of-imagej-simultaneously-on-windows-oss/1466

ij_dir = r'C:\Users\Smit\data_software\Fiji.app\ImageJ-win64.exe'



def run_macro(macro, ij_args=''):
    args = ij_dir + ' --headless --console -macro ' + macro + ' ' + ij_args
    print(args)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)

    while p.poll() is None:
        l = p.stdout.readline()
        if l:
            print(l.decode('ascii'))

    p.wait()


def run_peak_count(folder, thd, min_dst=4, rectangle=(0, 0, 0, 0)):
    assert(type(folder) == str)
    folder += os.path.sep
    print(folder)
    # if not folder[-1] == r'\':
    #     folder += r'\'
    ij_arg_list = [str(folder), str(thd), str(min_dst)] + [str(r) for r in rectangle]
    assert('#' not in ''.join(ij_arg_list))  # there can be no '#' in the args
    ij_args = '#'.join(ij_arg_list)

    macro = 'peak_count_headless.ijm' #this doesnt work since discoidal avg filter doesnt work in headless mode
    run_macro(macro, ij_args=ij_args)