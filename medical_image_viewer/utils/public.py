"""
@Author: Daryl Xu

Some public functions
"""
import pydicom
import numpy as np


def get_look_up_table(opacity: int=50):
    """
    序号， R， G, B, A
    对于A：0完全透明，255完全不透明
    :return:
    """
    color_map = np.array([[0, 0, 0, 0, 0],
                          [1, 255, 0, 0, opacity],
                          [2, 0, 255, 0, opacity],
                          [3, 0, 0, 255, opacity],
                        #   [255, 255, 255, 255, opacity]
                          ])
    return color_map[:, 1:]


if __name__ == '__main__':
    print(get_look_up_table())
