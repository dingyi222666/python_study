from array import array


import matplotlib.pyplot as plt


def func(out: int):
    return out


def main():
    fig, ax = plt.subplots()  # 创建一张白纸figure，包含一个坐标系.

    plt.plot(range(-100, 100), [func(index) for index in range(-100, 100)])  # 在坐标系画图.
    plt.xlabel("x")

    plt.ylabel("y")
    plt.grid(True)
    plt.show()
    # step = (max - min) / (count -1 )


if __name__ == '__main__':
    main()
