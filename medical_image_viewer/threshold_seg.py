import json
import os
from os import PathLike
import nibabel as nib
from nibabel import Nifti1Image
import numpy as np
from numpy import ndarray
from scipy import ndimage

from post_process import remove_small_object


def show_arr_info(name: str, data: ndarray):
    print(f'{name}: {[data.max(), data.min()]}, {data.dtype},{data.shape}, count: {np.count_nonzero(data)}')


class VesselSeg:
    def __init__(self, img_path: PathLike) -> None:
        # 获取id
        self._data_dir = '/home/daryl/usst/vessel_seg'
        self._data_id = img_path[-15: -12]
        self._threshold_file = f'{self._data_dir}/output/threshold_{self._data_id}.json'
        self._finetune_file = f'{self._data_dir}/output/vessel_{self._data_id}.nii.gz'
        liver_path: PathLike = f'{self._data_dir}/liver_seg/vessel_{self._data_id}.nii.gz'
        vessel_mask_path: PathLike = f'{self._data_dir}/vessel_seg/vessel_{self._data_id}.nii.gz'
        img_nii: Nifti1Image = nib.load(img_path)
        self.img_nii = img_nii
        img: ndarray = img_nii.get_fdata()
        self.img = img

        # 标准化
        # min_ = np.min(img)
        # range_ = np.max(img) - min_
        # img = (img - min_) / range_ * 1024
        # show_arr_info('img: ', img)

        # 每层单独标准化，每层的血管亮度值都有偏移
        # for i in range(img.shape[2]):
        #     s = img[:, :, i]
        #     min_ = np.min(s)
        #     range_ = np.max(s) - np.min(s)
        #     img[:, :, i] = (s - min_) / range_ * 1024


        liver_seg_nii: Nifti1Image = nib.load(liver_path)
        liver_seg_mask = liver_seg_nii.get_fdata()
        self.liver_mask = liver_seg_mask
        liver_seg_mask[liver_seg_mask>0] = 1
        # print(liver_seg_mask.shape)
        # return
        # 对z方向切面进行腐蚀
        for i in range(liver_seg_mask.shape[2]):
            # print(liver_seg_mask[:, :, i].shape)
            liver_seg_mask[:, :, i] = ndimage.binary_erosion(liver_seg_mask[:, :, i], iterations=8)
        
        self.liver_roi = self.img * liver_seg_mask

        vessel_mask_nii: Nifti1Image = nib.load(vessel_mask_path)
        vessel_mask: ndarray = vessel_mask_nii.get_fdata()
        self.vessel_mask = vessel_mask
        vessel_mask[vessel_mask>0] = 1
        # vessel_dilation = ndimage.binary_dilation(vessel_mask)
        # self.vessel_erosion = ndimage.binary_erosion(vessel_mask)

        show_arr_info('vessel_mask', vessel_mask)
        vessel_voxel = vessel_mask.sum()
        vessel_voxel2 = (vessel_mask>0).sum()
        print(f'vessel_mask max: {vessel_mask.max()}')

        img_ = img.copy()
        # img_[img_ == 0] = 1400
        print(f'img_ max: {img_.max()}, min: {img_.min()}')
        # 有值的
        vessel_roi: ndarray = img_ * vessel_mask
        self.vessel_roi = vessel_roi
        
        print(vessel_roi.max(), vessel_roi.min())
        statistic_voxel = np.where(vessel_roi.flatten() > 0)[0]
        # step = vessel_roi.max() // 100
        # bins_ = np.arange(1, step * 100 + 1, step)
        step = 0.01
        bins_ = np.arange(0.0000001, 1, step)
        print(f'vessel_roi max: {vessel_roi.max()}, '
            f'statistic max: {statistic_voxel.max()}')
        vessel_roi_flat = vessel_roi.flatten()


        # TODO 如何计算得到这个700
        mean, std = vessel_roi_flat.mean(where=vessel_roi_flat!=0), vessel_roi_flat.std(where=vessel_roi_flat!=0)
        self.vessel_roi_mean = mean
        self.vessel_roi_std = std
        if os.path.exists(self._threshold_file):
            with open(self._threshold_file) as f:
                self.threshold = json.load(f)['threshold']
        else:
            self.threshold = [mean for i in range(img.shape[2])]
        self.threshold_range = (mean - 4 * std, mean + 4 * std)
        threshold = mean + 0.3 * std # 像素值偏离半个标准差的视为疑似血管
        print(f'vessel_roi mean: {mean}, std: {std}, threshold: {threshold}')

        seg_threshold_mask = ( img < mean - 0.3 * threshold ) * liver_seg_mask * 2
        seg_threshold = img * seg_threshold_mask
        seg_threshold = seg_threshold * liver_seg_mask
        show_arr_info('seg_threshold: ', seg_threshold)

        # merge_mask = np.logical_or(seg_threshold_mask, self.vessel_erosion)
        if os.path.exists(self._finetune_file):
            nii: Nifti1Image = nib.load(self._finetune_file)
            self.merge_mask_seprated = nii.get_fdata()
        else:
            self.merge_mask_seprated: ndarray = seg_threshold_mask + self.vessel_mask

    def update_threshold(self, threshold: int, slice_index: int):
        self.threshold[slice_index] = threshold
        new_region = (self.liver_mask[:, :, slice_index] * (self.img[:, :, slice_index] < threshold)) * 2
        self.merge_mask_seprated[:, :, slice_index] = \
            new_region + self.vessel_mask[:, :, slice_index]

    def save_vessel_mask_fintue(self):
        self.merge_mask_seprated[0, 0, :] = 0
        self.img_nii._dataobj = self.merge_mask_seprated
        with open(self._threshold_file, 'w') as f:
            json.dump({'threshold': self.threshold}, f)
        nib.save(self.img_nii, self._finetune_file)
        self.save_debug()

    def save_debug(self):
        TMP_DIR = '/home/daryl/seg-debug'

        def tmp_file(name):
            return os.path.join(TMP_DIR, name)

        img_nii = self.img_nii
        img_nii._dataobj = self.vessel_roi
        nib.save(img_nii, os.path.join(TMP_DIR, 'vessel_roi.nii.gz'))

        img_nii._dataobj = self.img
        nib.save(img_nii, os.path.join(TMP_DIR, 'img.nii.gz'))


        img_nii._dataobj = self.vessel_mask
        nib.save(img_nii, os.path.join(TMP_DIR, 'vessel_mask.nii.gz'))

        img_nii._dataobj = self.merge_mask_seprated
        nib.save(img_nii, os.path.join(TMP_DIR, 'merge_mask_seprated.nii.gz'))

        no_small_obj = remove_small_object(self.merge_mask_seprated, 50)
        img_nii._dataobj = no_small_obj
        nib.save(img_nii, tmp_file('no_small_obj.nii.gz'))

