__author__ = 'kanaan'

import numpy as np

from surfer import Brain

brain = Brain('fsaverage5', 'split', 'pial', views = ['lat', 'med'], background='black', cortex='high_contrast')
surf_data = np.genfromtxt ('/Users/kanaan/SCR/workspace/project_touretome/Results_R1/thickness_tstat_CP.csv', delimiter=",")


surf_data_lh = surf_data[:10242]
surf_data_rh = surf_data[10242:]

brain.add_data(surf_data_lh, -5, 5, colormap="jet", alpha=1, hemi='lh')
brain.add_data(surf_data_rh, -5, 5, colormap="jet", alpha=1, hemi='rh')

brain.save_image('/Users/kanaan/Desktop/test.png')





import nibabel as nb
from surfer import Brain

brain = Brain("fsaverage5", "split", "white",  views=['lat', 'med'], background="white", cortex='high_contrast', offscreen = 1)

surf_data_rh =  nb.load('/Users/kanaan/SCR/workspace/project_touretome/test_plt/LZ041_rh2fsaverage5_20.mgh').get_data().ravel()
surf_data_lh =  nb.load('/Users/kanaan/SCR/workspace/project_touretome/test_plt/LZ041_lh2fsaverage5_20.mgh').get_data().ravel()


#brain.add_overlay(surf_data_lh, hemi='lh') # min=0, max=.1, name="",
#brain.add_overlay(surf_data_rh, hemi='rh') # min=0, max=.1, name="",


brain.add_data(surf_data_lh, 0, 3, colormap="jet", alpha=1, hemi='lh')
brain.add_data(surf_data_rh, 0, 3, colormap="Blues", alpha=1, hemi='rh')

brain.save_image('/Users/kanaan/Desktop/test.png')





import nibabel as nb
from surfer import Brain

for hemi in ['lh', 'rh']:

    sub = 'fsaverage5'
    hemi = hemi
    surf = 'white'
    bgcolor = 'w'

    brain = Brain(sub, hemi, surf, config_opts={'background': bgcolor})
    surf_data =  nb.load('/Users/kanaan/SCR/workspace/project_touretome/test_plt/LZ041_%s2fsaverage5_20.mgh'%hemi).get_data().ravel()
    brain.add_data(surf_data, 0, 3, colormap="jet", alpha=1, hemi=hemi)

    ###############################################################################
    # Get a set of images as a montage, note the data could be saved if desired
    image = brain.save_montage(None, ['l','m'], orientation='h')
    brain.close()

    ###############################################################################
    # View created image
    import pylab as pl
    fig = pl.figure(figsize=(50, 30), facecolor='k')
    ax = pl.axes(frameon=False)
    ax.imshow(image, origin='upper')
    pl.xticks(())
    pl.yticks(())
    pl.draw()
    pl.show()
    pl.savefig('/Users/kanaan/Desktop/%s.png'%hemi)





