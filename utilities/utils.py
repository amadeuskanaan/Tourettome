__author__ = 'kanaan'

import string
valid_chars = '-_.() %s%s' %(string.ascii_letters, string.digits)

import os
import numpy as np
import pandas as pd
import nibabel as nb
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')

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

def os_system(list_cmd):
    import os
    os.system(' '.join(list_cmd))

def regress_covariates(df_features, df_pheno, population, popname, features_dir, cmap='jet'):
    from patsy import dmatrix
    import statsmodels.formula.api as smf


    # There is a bug in patsy(dmatrix).... do it manually.
    # # Build design Matrix
    # design_matrix = dmatrix("0 + Sex + Site + Age + qc_func_fd + qc_anat_cjv", df_pheno, return_type="dataframe")
    # design_matrix.sort_index(axis=1, inplace=True)
    # design_matrix.columns = ['age', 'female', 'male', 'hannover_a', 'hannover_b','hamburg', 'leipzig', 'paris', 'cjv', 'fd' ]
    # design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in population], axis = 0)

    design_matrix = pd.DataFrame(index=df_pheno.index)

    # populate design matrix with vars
    def make_dmat_category(old_col, new_col):
        for i in design_matrix.index:
            if df_pheno.loc[i][old_col] == new_col:
                design_matrix.loc[i, new_col] = 1
            else:
                design_matrix.loc[i, new_col] = 0

    design_matrix['Age'] = df_pheno['Age']
    make_dmat_category('Sex', 'male')
    make_dmat_category('Sex', 'female')
    make_dmat_category('Site', 'HANNOVER_A')
    make_dmat_category('Site', 'HANNOVER_B')
    make_dmat_category('Site', 'HAMBURG')
    make_dmat_category('Site', 'Leipzig')
    make_dmat_category('Site', 'PARIS')
    design_matrix['qc_func_fd'] = df_pheno['qc_func_fd']
    design_matrix['qc_anat_cjv'] = df_pheno['qc_anat_cjv']

    design_matrix.columns = ['AGE', 'MALE', 'FEMALE', 'HANNOVER_A', 'HANNOVER_B', 'HAMBURG', 'LEIPZIG', 'PARIS', 'QC_CJV', 'QC_FD']
    design_matrix = design_matrix.drop([i for i in design_matrix.index if i not in population], axis = 0)

    # Save design matrix data
    dmat = design_matrix
    dmat['AGE'] = dmat['AGE']/100   # divide age by 100 for vis purposes
    f = plt.figure(figsize=(12, 8))
    sns.heatmap(dmat, yticklabels=False, cmap=cmap, vmin=0, vmax=2)
    plt.xticks(size=20, rotation=90, weight='bold')
    plt.savefig('%s/design_matrix_%s.png'%(features_dir, popname), bbox_inches='tight')
    design_matrix.to_csv('%s/design_matrix_%s.csv'%(features_dir, popname))

    # Regress features
    df_features = np.nan_to_num(df_features).T
    df_features_resid = []

    print '...... %s dmatrix  shape=%s' %(popname,design_matrix.shape)
    print '...... %s features shape=%s' %(popname,df_features.shape)

    for vertex_id in range(df_features.shape[1]):
        mat = design_matrix
        mat['y'] = df_features[:, vertex_id]
        formula = 'y ~ AGE + MALE + FEMALE + HANNOVER_A + HANNOVER_B + HAMBURG + LEIPZIG + PARIS + QC_CJV + QC_FD'
        model = smf.ols(formula=formula, data=pd.DataFrame(mat))
        df_features_resid.append(model.fit().resid)

    # save residual data
    df_features_resid = pd.concat(df_features_resid, axis=1)
    df_features_resid = df_features_resid.T
    df_features_resid.to_csv('%s/sca_%s_resid.csv' % (features_dir, popname))

    # plot residual data
    f = plt.figure(figsize=(12, 10))
    sns.heatmap(df_features_resid, xticklabels=False, yticklabels=False, cmap=cmap, vmin=-.7, vmax=0.7)
    plt.savefig('%s/sca_%s_resid.png' % (features_dir, popname), bbox_inches='tight')

    return df_features_resid.T




def return_sca_data(seed, population, derivatives_dir):
    import os
    import numpy as np
    import pandas as pd

    df_features = []
    for subject in population:

        lh = os.path.join(derivatives_dir, 'func_seed_correlation/%s/%s_sca_z_fwhm6_lh.npy' % (seed, subject))
        rh = os.path.join(derivatives_dir, 'func_seed_correlation/%s/%s_sca_z_fwhm6_rh.npy' % (seed, subject))

        if os.path.isfile(lh) and os.path.isfile(rh):
            sca_lh = np.load(lh).ravel()
            sca_rh = np.load(rh).ravel()
        else:
            print '.... Subject %s missing %s RSFC data' %(subject, seed)

        df_sca_lh = pd.DataFrame(sca_lh, columns=[subject],
                                 index=['%s_lh_%s' % (seed, str(i)) for i in range(sca_lh.shape[0])])
        df_sca_rh = pd.DataFrame(sca_rh, columns=[subject],
                                 index=['%s_rh_%s' % (seed, str(i)) for i in range(sca_rh.shape[0])])

        df_features.append(pd.concat([df_sca_lh, df_sca_rh], axis=0))

    # dict_sca = {'lh': np.array(np.mean(df_features, axis=1))[:10242],
    #             'rh': np.array(np.mean(df_features, axis=1))[10242:],
    #             'sca': pd.concat(df_features, axis=1)
    #             }

    return pd.concat(df_features, axis=1)

def return_ct_data(population, derivatives_dir):
    df_features = []
    for subject in population:
        ct_lh = nb.load(os.path.join(derivatives_dir, 'struct_cortical_thickness',
                                     '%s_ct2fsaverage5_fwhm20_lh.mgh' % subject)).get_data().ravel()
        ct_rh = nb.load(os.path.join(derivatives_dir, 'struct_cortical_thickness',
                                     '%s_ct2fsaverage5_fwhm20_rh.mgh' % subject)).get_data().ravel()

        ct_lh = pd.DataFrame(ct_lh, columns=[subject],
                                index=['ct_lh_' + str(i) for i in range(ct_lh.shape[0])])
        ct_rh = pd.DataFrame(ct_rh, columns=[subject],
                                index=['ct_rh_' + str(i) for i in range(ct_rh.shape[0])])

    df_features = pd.concat(df_features.append(pd.concat([ct_lh, ct_rh], axis=0)), axis=1)

    return df_features