__author__ = 'kanaan... 30.03.2017'

import os
import numpy as np
import nibabel as nb
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import matplotlib.gridspec as gridspec
from variables.subject_list import *
from utilities.utils import *


def plot_vol_quality(img, tissue, site, caption,fname, cmap = 'red'):

        # grab img data and coords
        img_data = np.rot90(nb.load(img).get_data())
        midpoint = img_data.shape[2] * 0.5
        coords   = [midpoint-30, midpoint-15, midpoint-10, midpoint,
                    midpoint+10, midpoint+20, midpoint+30, midpoint+40]

        # plot
        fig = plt.figure()
        fig.set_size_inches(50, 30)
        gs = gridspec.GridSpec(2, 4)

        for i, coord in enumerate(coords):
            if i in xrange(4):
                ax= plt.subplot(gs[0, i])
            else:
                ax = plt.subplot(gs[1, i-4])

            ax.imshow(img_data[:,:,int(coord)], cm.bone)
            ax.axes.get_yaxis().set_visible(False)
            ax.axes.get_xaxis().set_visible(False)

            if site  == 'HB':
                ax.set_xlim(20, 180)
                ax.set_ylim(230, 40)
            elif site  == 'HA':
                ax.set_xlim(20, 180)
                ax.set_ylim(220, 50)
            elif site  == 'PA':
                ax.set_xlim(20, 180)
                ax.set_ylim(220, 50)
            elif site  == 'LZ':
                ax.set_xlim(20, 180)
                ax.set_ylim(220, 50)

            plt.subplots_adjust(wspace=0.01, hspace=0.01)
            #ax.set_aspect('equal')

            # grab tissue data
            if tissue:
                tissue_data = edge_detect_ero(np.rot90(nb.load(tissue).get_data()))
                tissue_data[tissue_data ==0] = np.nan
                ax.imshow(tissue_data[:,:,int(coord)], ListedColormap(cmap))

        plt.figtext(0.125, 0.9, caption, fontsize = 100, color='r')
        output = os.path.join(os.getcwd(), fname)
        fig.savefig(output,bbox_inches='tight')

