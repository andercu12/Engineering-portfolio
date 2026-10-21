"""A small comparison figure for the example and README."""
import matplotlib.pyplot as plt
import numpy as np
import config as cfg


def plot_comparison(results, target, material, path, show=True):
    names = ['Coarse grid', 'Fine grid', 'Local\nL-BFGS-B']
    colors = ['#527a96', '#d69946', '#4b8b72']
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), layout='constrained')
    x = np.arange(len(results))
    settings = [('thickness_mm', 'Predicted thickness', 'Thickness [mm]', '.3f'),
                ('time_s', 'Travel time', 'Time [s]', '.2f'),
                ('score', 'Objective score', 'Score (lower is better)', '.4f')]
    for ax, (key, title, unit, fmt) in zip(axes, settings):
        values = [r[key] for r in results]
        bars = ax.bar(x, values, color=colors, width=0.6)
        ax.bar_label(bars, labels=[format(v, fmt) for v in values], padding=4, fontsize=10)
        ax.set_xticks(x, names)
        ax.set_title(title, fontsize=12)
        ax.set_ylabel(unit)
        ax.set_ylim(0, max(max(values), target if key == 'thickness_mm' else 0, 1e-6) * 1.25)
        ax.spines[['top', 'right']].set_visible(False)
        ax.yaxis.grid(True, alpha=0.2)
        ax.set_axisbelow(True)
    axes[0].axhline(target, color='#333333', linestyle='--', linewidth=1.2, label=f'Target: {target:g} mm')
    axes[0].legend(frameon=False, fontsize=9, loc='upper right')
    fig.suptitle(f'Coating process comparison · {material}', fontsize=15)
    fig.supxlabel(f'Simplified model · constant power {cfg.MACHINE_POWER_KW:g} kW · energy follows travel time', fontsize=10)
    fig.savefig(path, dpi=180, bbox_inches='tight')
    if show:
        plt.show()
    plt.close(fig)
