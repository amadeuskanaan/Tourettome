import os
import numpy as np
import nibabel as nb
import matplotlib
from variables.subject_list import *
from utilities.utils import *
from plots.plot_volumes import *


def make_quality_reports(population, workspace):


    for subject in population:

        print '###############################################################################'
        print 'Creating Quality Control Report for subject %s' % subject
        print ''

        subdir = os.path.join(workspace, subject)
        qcdir  = mkdir_path(os.path.join(subdir, 'QUALITY'))
        os.chdir(qcdir)

        anat      = os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_BRAIN.nii.gz' )
        gm        = os.path.join(subdir, 'ANATOMICAL', 'ANATOMICAL_GM.nii.gz')
        gm2mni    = os.path.join(subdir, 'REGISTRATION','ANATOMICAL_GM_MNI1mm.nii.gz')
        func2anat = os.path.join(subject,'REGISTRATION', 'REST_EDIT_MOCO_BRAIN_MEAN_BBR_ANAT1mm.nii.gz')

        # Plot native anatomical with GM
        plot_vol_quality(anat, gm, subject[0:2], '%s - Native Anatomical' %subject, 'plot_anat_native,png', cmap = 'r' )

        # Plot anat2mni reg quality using GM as a boundary
        plot_vol_quality(mni_brain_1mm, gm2mni, subject[0:2], '%s - Anatomical to MNI xfm' %subject, 'plot_anatgm_mni,png', cmap = 'r' )

        # Plot func2anat reg quality using GM as a boundary
        plot_vol_quality(func2anat, gm, subject[0:2], '%s - Func to Anat xfm' %subject, 'plot_func2anat,png', cmap = 'r' )

make_quality_reports(['HA013'], tourettome_workspace)


###########
# ANATOMICAL
# 1- RAW
# 2- Deskulled
# 3- GM/WM/CSF
# 4- Reg to mni

###########
# Functional
# 1- Raw Mean
# 2- TSNR
# 3- FD
# 4- DVARS
# 5- denoised imshow


# GM/WM/CSF
# PLOT FUNCTIONAL MEAN ax-cor-sagg at level of BG




# make qap pipe