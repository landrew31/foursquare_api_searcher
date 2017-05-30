from matplotlib import pyplot as plt
import numpy as np
from spatial_module import (
    calculate_local_moran,
    calculate_durbin,
)


def get_np_array(ar):
    return np.array([[int(j[0]) for j in ar[i * 7: (i + 1) * 7]] for i in range(8)])


def plot(category):
    lm = calculate_local_moran(category)
    arr = np.array([lm.Is[i*7: (i + 1)*7] for i in range(8)])
    arrr = []
    for i in arr:
        a = []
        for j in i:
            if j < -0.3:
                j += 0.5
            a.append(j)
        arrr.append(a)
    arr = np.array(arrr)
    plt.pcolor(arr)
    plt.colorbar()
    plt.show()


def plot_histograms(category):
    d = calculate_durbin(category)
    arr = get_np_array(d.u)
    cmap = plt.get_cmap('RdBu', np.max(arr)-np.min(arr)+1)
    mat = plt.matshow(
        arr,
        cmap=cmap,
        vmin=np.min(arr)-.5,
        vmax=np.max(arr)+.5
    )
    plt.colorbar(
        mat,
        ticks=np.arange(np.min(arr), np.max(arr)+1)
    )
    plt.show()
