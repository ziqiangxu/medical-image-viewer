from enum import Enum, unique


@unique
class Algorithm(Enum):
    BY_THRESHOLD = 'By threshold'
    GROW_EVERY_SLICE = 'Grow every slice'


@unique
class ViewMode(Enum):
    VIEW = '看图'
    PIXEL_SELECTION = '选点'
    ROI_SELECTION = 'ROI选择'
