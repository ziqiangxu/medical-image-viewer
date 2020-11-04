"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com

Some public functions
"""
import pydicom
import numpy as np


def get_look_up_table():
    """
    序号， R， G, B, A
    对于A：0完全透明，255完全不透明
    :return:
    """
    color_map = np.array([[0, 0, 0, 0, 0],
                          # [1, 0, 0, 255, 255],
                          # [2, 0, 255, 0, 100],
                          [3, 255, 0, 0, 100]])
    return color_map[:, 1:]


if __name__ == '__main__':
    print(get_look_up_table())
