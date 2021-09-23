import numpy as np


def first_array():
    array = np.array([[1, 2, 3], [3, 4, 5]])  # 两行三列
    print(array)
    print(array.reshape([3, 2]))  # 三行两列
    print(array.ndim)  # 维数


def array_2():
    array = np.arange(0, 20)
    print(array)
    print(np.zeros([5, 5]))  # 创建5行5列都为0的数组
    print(np.ones([3, 4]))  # 创建3行4列都为1的数组


def array_3():
    # 开始值 结束值 生成个数（默认50个)
    # 计算步长 (最大值-最小值) / （个数 - 1)
    array = np.linspace(1, 10, 10)
    print(array)
    array = np.linspace(1, 10, 10, endpoint=False)
    # 不包含最后的值
    print(array, np.linspace(1, 10, 11))  # 其实endpoint就是把取的数字加一，然后舍弃掉最后一个数字
    print(np.logspace(1, 10, 10, base=2))


def array_4():
    data1 = np.array([[1, 2, 3, 4], [4, 7, 8, 11]])

    data2 = np.array([2, 3, 1, 4])

    '''
    在进行运算时 因为data1和data2两个的列和维度不一样，data2会先扩展到和data1一样的大小，然后在去和data1里面的元素去做启用
    '''

    print(data1 + data2)

    data1 = np.array([1, 2, 3, 5])
    data2 = np.array([3, 4, 4, 5])
    print(data1 + data2)


def array_5():
    data = np.array([1, 3, 4, 5, 6, 7, 8, 7])

    for value in np.nditer(data):  # 直接for输出
        print(value)


def array_6():
    data = np.array([
        [1, 2, 3],
        [4, 5, 6]])

    print(data.sum(axis=1))  # 横向为1
    print(data.sum(axis=0))  # 竖向为0

    data = np.array([
        [
            [2, 3, 4],
            [4, 5, 5]
        ],

    ])

    print(data.sum(axis=1))  # 横向为1
    print(data.sum(axis=0))  # 竖向为0

    print(data.sum(axis=2))


def array_7():
    data = np.array([
        [1, 2, 3, 4, 6],
        [4, 3, 5, 8, 12],
        [np.nan, 4, 12, 45, 34]
    ])

    print(data.sum(axis=0))
    print(data[:, 0])
    print(data.shape)  # (3,5)

    # 因为每个nan都是不相等的，所以两个相同的数组做比较 不相等的一定是nan
    for i in range(data.shape[1]):
        temp_data = data[:, i]  # 取得列
        count = np.count_nonzero(temp_data != temp_data)  # !=是指判断是否不一样的个数
        if count > 0:
            temp_no_nan: np.ndarray = temp_data[temp_data == temp_data]
            # 有nan
            print(temp_no_nan)
            # 均值补充方法
            # temp_data[np.isnan(temp_data)] = temp_no_nan.mean()
            # 中位数补充方法
            temp_data[np.isnan(temp_data)] = np.median(temp_no_nan)

    print(data)


def main():
    funcs = [first_array, array_2, array_3, array_4, array_5, array_6, array_7]
    for func in funcs:
        print("run function : {} ".format(func.__name__).center(60, "-"))
        func()


if __name__ == '__main__':
    main()
