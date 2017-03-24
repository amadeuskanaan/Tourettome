__author__ = 'kanaan'

import string
valid_chars = '-_.() %s%s' %(string.ascii_letters, string.digits)

def mkdir_path(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    return path


def mkcd_path(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    os.system(path)

def find(name, path):
    import os
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)



def create_fsl_mats(afni_aff_1D):
        import numpy as np
        import os
        aff = np.genfromtxt(afni_aff_1D, skip_header=1)
        cur_dir = os.getcwd()
        mat_list =[]

        try:
            os.makedirs(os.path.join(cur_dir, 'MATS'))
        except OSError:
            print '...........Matrix output folder already created'
        out_dir  = str(os.path.join(cur_dir, 'MATS'))

        for i, line in enumerate(aff):
            mat =  np.zeros((4, 4))
            mat[0] = line[0:4]
            mat[1] = line[4:8]
            mat[2] = line[8:12]
            mat[3] = (0,0,0,1)
            out_file  = os.path.join('%s/MAT_%s.mat' %(out_dir, '{0:0>4}'.format(i)))
            np.savetxt( out_file, mat, delimiter = ' ', fmt="%s")

            mat_list.append(out_file)

        return mat_list


def calc_friston_twenty_four(mov_par):
    import numpy as np
    import os
    twenty_four   = None

    six           = np.genfromtxt(mov_par)
    six_squared   = six**2

    twenty_four   = np.concatenate((six,six_squared), axis=1)

    six_roll      = np.roll(six, 1, axis=0)
    six_roll[0]   = 0

    twenty_four   = np.concatenate((twenty_four, six_roll), axis=1)

    six_roll_squ  = six_roll**2

    twenty_four   = np.concatenate((twenty_four, six_roll_squ), axis=1)
    updated_mov   = os.path.join(os.getcwd(), 'FRISTON_24.1D')
    np.savetxt(updated_mov, twenty_four, fmt='%0.8f', delimiter=' ')

    return updated_mov
