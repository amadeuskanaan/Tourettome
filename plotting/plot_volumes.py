__author__ = 'kanaan... 30.03.2017'

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

def plot_quality_old(img, tissue, site, caption, cmap='red', title=None):
        import numpy as np
        import nibabel as nb
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.colors import ListedColormap
        import matplotlib.gridspec as gridspec

        # grab img data and coords
        img_data = np.rot90(nb.load(img).get_data())
        midpoint = img_data.shape[2] * 0.5
        if site == 'HB':
            midpoint = midpoint - 30
        coords = [midpoint - 20, midpoint, midpoint + 20, midpoint + 30, midpoint + 50]

        # plot
        fig = plt.figure()
        fig.set_size_inches(50, 30)
        gs = gridspec.GridSpec(1, 5)

        for i, coord in enumerate(coords):
            if i in xrange(5):
                ax = plt.subplot(gs[0, i])

            ax.imshow(img_data[:, :, int(coord)], cm.bone)
            ax.axes.get_yaxis().set_visible(False)
            ax.axes.get_xaxis().set_visible(False)

            ax.set_xlim(15, 175)
            if site == 'HB':
                ax.set_ylim(230, 40)
            else:
                ax.set_ylim(220, 50)

            plt.subplots_adjust(wspace=0.01, hspace=0.01)
            # ax.set_aspect('equal')

            # grab tissue data
            if tissue:
                tissue_data = edge_detect_ero(np.rot90(nb.load(tissue).get_data()))
                tissue_data[tissue_data == 0] = np.nan
                ax.imshow(tissue_data[:, :, int(coord)], ListedColormap(cmap))

        plt.figtext(0.13, 0.625, caption, fontsize=50, color='r')

        if title:
            plt.save(title, bbox_inches='tight')


def plot_quality(img, tissue, site, caption, color='red', alpha=1., title=None, tissue2=None, tissue3=None):
    import numpy as np
    import nibabel as nb
    import matplotlib; matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import ListedColormap
    import matplotlib.gridspec as gridspec

    # grab img data and coords
    img_data = np.rot90(nb.load(img).get_data())
    midpoint = img_data.shape[2] * 0.5
    if site == 'HB':
        midpoint = midpoint - 30
    coords = [midpoint - 20, midpoint, midpoint + 20, midpoint + 30, midpoint + 50]

    if site == 'MNI':
        midpoint = midpoint - 45
        coords = [midpoint - 20, midpoint, midpoint + 20, midpoint + 30, midpoint + 50]

    if site == 'TSNR':
        coords = [midpoint - 10, midpoint - 5, midpoint, midpoint + 5, midpoint + 10]

    # plot
    fig = plt.figure()
    fig.set_size_inches(50, 30)
    gs = gridspec.GridSpec(1, 5)

    for i, coord in enumerate(coords):
        if i in xrange(5):
            ax = plt.subplot(gs[0, i])

        ax.imshow(img_data[:, :, int(coord)], cm.bone)
        ax.axes.get_yaxis().set_visible(False)
        ax.axes.get_xaxis().set_visible(False)

        # ax.set_xlim(15, 175)
        # if site == 'HB':
        #    ax.set_ylim(230, 40)
        # else:
        #    ax.set_ylim(220, 50)

        plt.subplots_adjust(wspace=0.01, hspace=0.01)
        # ax.set_aspect('equal')

        # grab tissue data
        if tissue:
            tissue_data = edge_detect_ero(np.rot90(nb.load(tissue).get_data()))
            tissue_data[tissue_data == 0] = np.nan
            ax.imshow(tissue_data[:, :, int(coord)], ListedColormap(color))

        if tissue2:
            tissue_data = edge_detect_ero(np.rot90(nb.load(tissue2).get_data()))
            tissue_data[tissue_data == 0] = np.nan
            ax.imshow(tissue_data[:, :, int(coord)], ListedColormap('lime'))

        if tissue3:
            tissue_data = edge_detect_ero(np.rot90(nb.load(tissue3).get_data()))
            tissue_data[tissue_data == 0] = np.nan
            ax.imshow(tissue_data[:, :, int(coord)], ListedColormap('b'))

    plt.figtext(0.13, 0.625, caption, fontsize=50, color='r', alpha=alpha)

    if title:
        plt.savefig(title, transparent = True, bbox_inches='tight')

def plot_temporal(gm, wm, cm, fd, dv, title):
    import matplotlib.pyplot as plt

    fig = plt.figure()
    fig.subplots_adjust(wspace=0.5, hspace=0.1)
    fig.set_size_inches(24, 10)

    ax1 = plt.subplot2grid((4, 1), (0, 0), colspan=1, rowspan=2)
    ax1.imshow(np.concatenate([gm, wm, cm]), interpolation='nearest', aspect='auto', cmap='Greys', vmin=-5, vmax=5)
    ax1.axes.get_xaxis().set_visible(False)
    # ax1.hlines(gm.shape[0], 0,fd.shape[0], linestyles='-', colors='r', linewidth='2')
    # ax1.hlines(gm.shape[0]+wm.shape[0], 0,fd.shape[0], linestyles='-', colors='r', linewidth='2')
    # ax1.hlines(gm.shape[0]+wm.shape[0]+cm.shape[0], 0,fd.shape[0], linestyles='-', colors='r', linewidth='2')
    # ax1.axes.get_yaxis().set_visible(False)
    ax1.set_ylabel('Voxels', size=25, weight='bold')
    plt.yticks([])

    ax2 = plt.subplot2grid((4, 1), (2, 0), colspan=1, rowspan=1)
    ax2.plot(fd, 'b', linewidth='3')
    ax2.hlines(0.2, 0, fd.shape[0], linestyles='--', colors='r', linewidth='3')
    ax2.set_ylabel('FD', size=25, weight='bold')
    ax2.axes.get_xaxis().set_visible(False)
    # plt.title('FD_mu = %s'%fd_mu, size=30, loc='left', weight='bold')
    plt.yticks(fontsize=15, weight='bold')
    ylim = ax2.get_ylim()
    ax2.text(10, ylim[0] + (ylim[1] - ylim[0]) * 0.75, 'FD=%smm' % fd_mu, va='center', size=25, color='r',
             weight='bold')

    ax3 = plt.subplot2grid((4, 1), (3, 0), colspan=1, rowspan=1)
    ax3.plot(dv, 'maroon', linewidth='3', )
    ax3.set_ylabel('DVARS', size=25, weight='bold')
    ax3.set_xlabel('Volumes', size=25, weight='bold')
    plt.yticks(fontsize=15, weight='bold')
    ylim = ax3.get_ylim()
    ax3.text(10, ylim[0] + (ylim[1] - ylim[0]) * 0.75, 'DVARS=%s' % dv_mu, va='center', size=25, color='r',
             weight='bold')

    plt.xticks(fontsize=15, weight='bold')
    # plt.gca().yaxis.grid(True)
    # plt.gca().xaxis.grid(True)

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(0, fd.shape[0] - 1)

    if title:
        plt.savefig(title, transparent=True, bbox_inches='tight')
