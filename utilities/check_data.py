
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

    return pd.concat(df_features, axis=1)

def return_ct_data(population, derivatives_dir):
    df_features = []
    for subject in population:
        if not os.path.isfile(os.path.join(derivatives_dir, 'struct_cortical_thickness',
                                           '%s_ct2fsaverage5_fwhm20_lh.mgh' % subject)):
            print 'subject %s missing ct data' % subject
        else:
            ct_lh = nb.load(os.path.join(derivatives_dir, 'struct_cortical_thickness',
                                         '%s_ct2fsaverage5_fwhm20_lh.mgh' % subject)).get_data().ravel()
            ct_rh = nb.load(os.path.join(derivatives_dir, 'struct_cortical_thickness',
                                         '%s_ct2fsaverage5_fwhm20_rh.mgh' % subject)).get_data().ravel()

            ct_lh = pd.DataFrame(ct_lh, columns=[subject],
                                 index=['ct_lh_' + str(i) for i in range(ct_lh.shape[0])])
            ct_rh = pd.DataFrame(ct_rh, columns=[subject],
                                 index=['ct_rh_' + str(i) for i in range(ct_rh.shape[0])])
        df_features.append(pd.concat([ct_lh, ct_rh], axis=0))
        df_features.append(pd.concat([ct_lh, ct_rh], axis=0))

    return pd.concat(df_features, axis=1)

