"""
@Author: Daryl Xu
"""
from enum import Enum, unique


@unique
class Algorithm(Enum):
    BY_THRESHOLD = '算法1: by_threshold'
    GROW_EVERY_SLICE = '算法2: grow slices'
    ITK_3d_GROW = 'ITK-3D grow'
    BY_RANGE = '算法3：阈值范围'


@unique
class ViewMode(Enum):
    VIEW = '看图'
    PIXEL_SELECTION = '选点'
    ROI_SELECTION = 'ROI选择'
