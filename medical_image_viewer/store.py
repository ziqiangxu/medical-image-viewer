"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import os
from typing import List, Tuple

import numpy as np


class State:
    """
    共享
    """
    def __init__(self):
        self.name = 'state'
        self._dcm_files: List[str] = []
        self._volume: np.ndarray = None
        self._overlay: np.ndarray = None
        self._seed: Tuple[int, int, int] = None
        self._voxel_size = 0

    @property
    def voxel_size(self):
        assert self._voxel_size != 0
        return self._voxel_size

    def set_voxel_size(self, size: float):
        assert size > 0
        self._voxel_size = size
        # TODO 移除本行代码
        raise BaseException('暂时不将本属性存储在store中')

    @property
    def dcm_files(self):
        assert self._dcm_files
        return self._dcm_files

    @property
    def seed(self):
        assert self._seed is not None
        return self._seed

    def set_seed(self, seed: Tuple[int, int, int]):
        self._seed = seed

    @property
    def volume(self):
        # TODO add a decorator for every property to sure the value not be a None object
        assert self._volume is not None
        return self._volume

    def set_volume(self, volume: np.ndarray, dcm_files: List):
        """
        :param volume:
        :param dcm_files: DICOM files sorted by the acquire position
        :return:
        """
        assert volume.ndim == 3 and volume.shape[0] == len(dcm_files)
        self._volume = volume
        self._dcm_files = dcm_files

    @property
    def overlay(self):
        # TODO add a decorator for every property to sure the value not be a None object
        return self._overlay

    def set_overlay(self, overlay: np.ndarray):
        """
        :param overlay:
        :return:
        """
        if overlay is not None:
            assert overlay.shape == self.volume.shape
        self._overlay = overlay
