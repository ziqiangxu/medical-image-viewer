"""
@Author: Daryl Xu
"""
from enum import Enum, unique


@unique
class Algorithm(Enum):
    BY_THRESHOLD = '算法1'
    GROW_EVERY_SLICE = '算法2'


@unique
class ViewMode(Enum):
    VIEW = '看图'
    PIXEL_SELECTION = '选点'
    ROI_SELECTION = 'ROI选择'
