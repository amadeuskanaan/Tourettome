__author__ = 'Seyma Bayrak & Ahmad Seif Kanaan 28.11.2017, based on work by Daniel Margulies (PNAS, 2016)'

sys.path.append(os.path.expanduser('/scr/malta1/Github/Tourettome/algorithms/mapalign/mapalign'))
import os, sysm, h5py, embed
import numpy as np
import nibabel as nb
from sklearn.metrics import pairwise_distances
from nilearn import plotting, input_data, connectome
import numexpr as ne
from utilities.utils import *
from variables.subject_list import *
ne.set_num_threads(ne.ncores) # inclusive HyperThreading cores

def create_group_gm(population, workspace):

    os.chdir(tourettome_embedding)
    masks = [os.path.join(workspace, subject, 'REGISTRATION', 'REST_GM_MNI3mm.nii.gz') for subject in population]
    os.system('fslmaths %s tourettome_GM_MNI3mm'%((' -add '.join(masks))))

create_group_gm(tourettome_subjects, tourettome_workspace)

def diffusion_embedding(population, workspace, popname):

    mask          =   os.path.join(workspace, 'PA001', 'REGISTRATION/REST_GM_MNI3mm.nii.gz')
    corrmat_shape = np.count_nonzero(nb.load(mask).get_data())
    corrmat_sum   = np.zeros((corrmat_shape, corrmat_shape))
    embed_dir = mkdir_path(os.path.join(workspace, 'EMBEDDING'))

    if not os.path.isfile(os.path.join(embed_dir, "corrmat_mean_%s.npy"%popname)):
        for subject in population:

            print 'Creating correlatiom matrix for Subject %s' %subject
            #I/O
            subject_dir = os.path.join(workspace, subject)
            func        = os.path.join(subject_dir, 'DENOISE/residuals_compcor/residual_bp_z_fwhm6.nii.gz')
            mask        = os.path.join(workspace, 'PA001', 'REGISTRATION/REST_GM_MNI3mm.nii.gz')

            # Get timeseries
            masker = input_data.NiftiMasker(mask)
            time_series = masker.fit_transform(func)
            print '....', time_series.shape
            correlation_measure = connectome.ConnectivityMeasure(kind='correlation')
            ###########add R to Z
            correlation_matrix  = correlation_measure.fit_transform([time_series])[0]
            print '....', correlation_matrix.shape

            corrmat_sum += correlation_matrix
            print corrmat_sum.shape

            # modify this to save mat files... make sure they are deleted after embedding. will help looping
            # embed_dir = mkdir_path(os.path.join(subject_dir, 'EMBED'))
            #save matrix as h5py file
            # h5 = h5py.File('%s/corrmat_%s.h5'%(embed_dir, subject), 'w')
            # h5.create_dataset('data', data=correlation_matrix)
            # all_mats.append(correlation_matrix)

        print 'Calculating average correlation matrix'
        corrmat_mean = corrmat_sum / len(population)
        print '....',corrmat_mean.shape
        os.chdir(embed_dir)
        np.save(os.path.join(embed_dir, "corrmat_mean_%s.npy"%popname), corrmat_mean)


    # Nonlinear decomposition with Emebdding
    print 'Eembedding'

    # add Z to R
    corrmat_mean  = np.load(os.path.join(embed_dir, "corrmat_mean_%s.npy" % popname))

    ###### Threshold each row of corr matrix at 90th percentile ##
    print "thresholding each row at its 90th percentile..."
    percentile90 = np.array([np.percentile(x, 90) for x in corrmat_mean])
    for i in range(corrmat_mean.shape[0]):
        # print "Row %d" % i
        corrmat_mean[i, corrmat_mean[i, :] < percentile90[i]] = 0

    ##### get affinity matrix via cosine similarity ##############
    print "calculating affinity matrix..."
    aff = 1 - pairwise_distances(corrmat_mean, metric = 'cosine')

    # Check for minimum & maximum value
    print "....Minimum value of aff is %f" % aff.min()
    print "....Maximum value of aff is %f" % aff.max()

    print "saving affinity matrix..."
    h = h5py.File(os.path.join(embed_dir, 'affinity_matrix.h5'), 'w')
    h.create_dataset("data", data=aff)
    h.close()

    ##### Get embedding components on affinity matrix ############
    print "calculating connectivity components..."
    emb, res = embed.compute_diffusion_map(aff, alpha=0.5, n_components=10)
    np.save(os.path.join(embed_dir,'embedding_dense_emb.npy'), emb)
    np.save(os.path.join(embed_dir,'embedding_dense_res.npy'), res)


    #### Step #9: projecting components back to MNI space as nifti #######
    print "saving components as nifti..."

    emb = np.load(os.path.join(embed_dir,'embedding_dense_emb.npy'))


    ##### get indices of voxels, which are equal to 1 in mask
    mask_array = nb.load(mask).get_data()
    voxel_x    = np.where(mask_array==1)[0]
    voxel_y    = np.where(mask_array==1)[1]
    voxel_z    = np.where(mask_array==1)[2]

    print "%s voxels are in GM..." % len(voxel_x)

    mni_affine = nb.load(mni_brain_3mm).get_affine()
    data_temp  = np.zeros(nb.load(mni_brain_3mm).get_data().shape)

    for j in range(0, 10):
        print np.shape(emb[:,j])
        data_temp[voxel_x, voxel_y, voxel_z] = emb[:,j]
        img_temp  = nb.Nifti1Image(data_temp, mni_affine)
        name_temp = os.path.join(embed_dir, 'mni3_component_%s.nii.gz' % (j+1))
        nb.save(img_temp, name_temp)


# diffusion_embedding(paris[1:3], tourettome_workspace, 'test_paris')
