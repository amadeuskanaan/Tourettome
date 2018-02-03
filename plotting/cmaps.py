########################################################################################################################
##### Colormaps


import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')
import matplotlib.colors as colors
import numpy as np

first = int((128*2)-np.round(255*(1.-0.50)))
second = (256-first)
cmap_gradient = colors.LinearSegmentedColormap.from_list('my_colormap',
                                                  np.vstack((plt.cm.YlOrRd(np.linspace(0.98, 0.25, second)),
                                                            plt.cm.viridis(np.linspace(.98, 0.0, first)))))
cmap_drysdale = colors.ListedColormap(['#00ffff', '#00afff','#0000ff', '#260000', '#530000','#fe0000', '#ff6a00',
                                           '#ffff00'])

cmap_ted = colors.ListedColormap(['#00ffff', '#00afff','#0000ff', '#260000', '#530000','#fe0000', '#ff6a00',
                                      '#ffff00', '#ffffff'])
