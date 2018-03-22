__author__ = 'kanaan 10.01.2018... re-written 19.10.2018'

import os
import numpy as np
import pandas as pd
from scipy import cluster
from sklearn.cluster import AgglomerativeClustering
from sklearn import preprocessing
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')

from variables.subject_list import *
from utilities.utils import mkdir_path
from plotting.cmaps import cmap_gradient

def plot_heat_cluster():
    cluster_controls = sns.clustermap(sca_controls_resid_z, xticklabels=False, yticklabels=False,
                                      cmap=cmap_gradient, row_cluster=False, vmin=-3, vmax=3,
                                      method='ward', metric='euclidean')

def plot_dendogram(df, method='ward', metric='euclidean'):
    Z = cluster.hierarchy.linkage(df, method=method, metric=metric, optimal_ordering=False)
    fig, axes = plt.subplots(1, 1, figsize=(12, 8))
    ax = cluster.hierarchy.dendrogram(Z, show_contracted=True)#, truncate_mode='lastp')
    plt.ylabel('Cluster Size')
    plt.ylabel('Distance')
    plt.axhline(1000, linestyle='--', linewidth=3, color= 'k')
    plt.axhline(700, linestyle='--', linewidth=3, color= 'k')
    plt.ylim((0,2500))

def plot_site_clust_dist(df):

    clusterx = AgglomerativeClustering(n_clusters=3, affinity='euclidean', linkage='ward')
    clusterx.fit(df)
    df_clust = pd.DataFrame(index= df.index)
    df_clust['labels']= clusterx.labels_

    def n_site_per_cluster(site):
        c1 = [i for i  in df_clust.index if df_clust.loc[i]['labels'] == 0 if i[0:2] == site]
        c2 = [i for i  in df_clust.index if df_clust.loc[i]['labels'] == 1 if i[0:2] == site]
        c3 = [i for i  in df_clust.index if df_clust.loc[i]['labels'] == 2 if i[0:2] == site]
        return len(c1) ,len(c2) ,len(c3)

    n_cluster = 3
    HA = n_site_per_cluster('HA')
    HB = n_site_per_cluster('HB')
    LZ = n_site_per_cluster('LZ')
    PA = n_site_per_cluster('PA')

    ha = (HA[0], HA[1], HA[2])
    hb = (HB[0], HB[1], HB[2])
    lz = (LZ[0], LZ[1], LZ[2])
    pa = (PA[0], PA[1], PA[2])

    ind = np.arange(n_cluster)
    width = 0.85

    cmap = ['#e41a1c', '#377eb8', '#4daf4a', '#223ea2']
    cmap =  cmap[::-1]
    #cmap = ['#1b9e77', '#d95f02', '#7570b3', '#7570b3']

    fig = plt.figure(figsize=(7,7))
    p1 = plt.bar(ind, ha, width, color=cmap[0],edgecolor='white', )
    p2 = plt.bar(ind, hb, width, bottom=ha, color=cmap[1],edgecolor='white', )
    p3 = plt.bar(ind, lz, width, bottom=np.array(ha)+np.array(hb), color=cmap[2],edgecolor='white', )
    p4 = plt.bar(ind, pa, width, bottom=np.array(ha)+np.array(hb)+np.array(lz), color=cmap[3],edgecolor='white', )

    #plt.ylabel('Scores')
    #plt.title('Scores by group and gender')
    #plt.xticks(ind, ('C1', 'C2', 'C3'))
    plt.yticks(np.arange(0, 40, 10))
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('Hannover_A', 'Hannover_B', 'Leipzig', 'Paris'))

    plt.show()


def heirarchical_clustering(feature_df, derivatives_dir):

    # Determine number of optimal clusters
    # Run h-clustering in loop with k=1-20


    # bootstrap-stable cluster analysis

    # return labels

    # save featurmats as seprate dataframes for each feature (SCA, CT, ECM)

