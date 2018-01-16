import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')

def plot_heatmap(df, fname, figsize=(12, 10), cmap='jet', vmin=-0.7, vmax=0.7):
    fig = plt.figure(figsize=figsize)
    sns.heatmap(df, xticklabels=False, yticklabels=False, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.savefig('%s.png'%fname, bbox_inches='tight')
