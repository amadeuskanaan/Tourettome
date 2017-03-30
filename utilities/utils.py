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
            print 'Matrix output folder already created'
        out_dir  = str(os.path.join(cur_dir, 'MATS'))

        for i, line in enumerate(aff):
            mat =  np.zeros((4, 4))
            mat[0] = line[0:4]
            mat[1] = line[4:8]
            mat[2] = line[8:12]
            mat[3] = (0,0,0,1)
            out_file  = os.path.join('%s/MAT_%s' %(out_dir, '{0:0>4}'.format(i)))
            np.savetxt( out_file, mat, delimiter = ' ', fmt="%s")

            mat_list.append(out_file)

        return mat_list



def find_cut_coords(img, mask=None, activation_threshold=None):
    import warnings
    import numpy as np
    from scipy import ndimage
    from nilearn._utils import as_ndarray, new_img_like
    from nilearn._utils.ndimage import largest_connected_component
    from nilearn._utils.extmath import fast_abs_percentile
    """ Find the center of the largest activation connected component.
        Parameters
        -----------
        img : 3D Nifti1Image
            The brain map.
        mask : 3D ndarray, boolean, optional
            An optional brain mask.
        activation_threshold : float, optional
            The lower threshold to the positive activation. If None, the
            activation threshold is computed using the 80% percentile of
            the absolute value of the map.
        Returns
        -------
        x : float
            the x world coordinate.
        y : float
            the y world coordinate.
        z : float
            the z world coordinate.
    """
    data = img.get_data()
    # To speed up computations, we work with partial views of the array,
    # and keep track of the offset
    offset = np.zeros(3)

    # Deal with masked arrays:
    if hasattr(data, 'mask'):
        not_mask = np.logical_not(data.mask)
        if mask is None:
            mask = not_mask
        else:
            mask *= not_mask
        data = np.asarray(data)

    # Get rid of potential memmapping
    data = as_ndarray(data)
    my_map = data.copy()
    if mask is not None:
        slice_x, slice_y, slice_z = ndimage.find_objects(mask)[0]
        my_map = my_map[slice_x, slice_y, slice_z]
        mask = mask[slice_x, slice_y, slice_z]
        my_map *= mask
        offset += [slice_x.start, slice_y.start, slice_z.start]

    # Testing min and max is faster than np.all(my_map == 0)
    if (my_map.max() == 0) and (my_map.min() == 0):
        return .5 * np.array(data.shape)
    if activation_threshold is None:
        activation_threshold = fast_abs_percentile(my_map[my_map != 0].ravel(),
                                                   80)
    mask = np.abs(my_map) > activation_threshold - 1.e-15
    # mask may be zero everywhere in rare cases
    if mask.max() == 0:
        return .5 * np.array(data.shape)
    mask = largest_connected_component(mask)
    slice_x, slice_y, slice_z = ndimage.find_objects(mask)[0]
    my_map = my_map[slice_x, slice_y, slice_z]
    mask = mask[slice_x, slice_y, slice_z]
    my_map *= mask
    offset += [slice_x.start, slice_y.start, slice_z.start]

    # For the second threshold, we use a mean, as it is much faster,
    # althought it is less robust
    second_threshold = np.abs(np.mean(my_map[mask]))
    second_mask = (np.abs(my_map) > second_threshold)
    if second_mask.sum() > 50:
        my_map *= largest_connected_component(second_mask)
    cut_coords = ndimage.center_of_mass(np.abs(my_map))
    x_map, y_map, z_map = cut_coords + offset

    coords = []
    coords.append(x_map)
    coords.append(y_map)
    coords.append(z_map)

    # Return as a list of scalars
    return coords


def edge_detect_ero(i):
    import numpy as np
    from scipy import ndimage
    ero  = ndimage.binary_erosion(i,iterations=1).astype(i.dtype)
    edge = i -ero
    edge[edge==0]=np.nan
    return edge

def edge_detect_first(i):
    import numpy as np
    from scipy import ndimage
    ero =  ndimage.binary_erosion(i, iterations=2).astype(i.dtype)
    dil =  ndimage.binary_dilation(i, iterations=1).astype(i.dtype)
    sep = dil-ero
    sep = ndimage.binary_erosion(sep, iterations=1).astype(sep.dtype)
    sep[sep==0]=np.nan
    return sep
