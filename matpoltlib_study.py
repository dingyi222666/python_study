from array import array

import matplotlib.pyplot as plt

import numpy as np


def draw_1():
    x = range(2, 24 + 2, 2)
    y = np.random.randint(14, 26 + 1, 12)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=80)
    fig: plt.Figure = fig
    ax: plt.Axes = ax
    ax.set_xticks(range(2,24+1)) #设置x的轴间隔
    ax.set_yticks(range(y.min(),y.max()+1))

    ax.plot(x, y)
    plt.show()


def main():
    draw_1()


if __name__ == '__main__':
    main()
