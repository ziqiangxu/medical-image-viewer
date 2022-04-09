"""
@Author: Daryl Xu
"""
from typing import List
import warnings

import pydicom
import numpy as np
from deprecated.sphinx import deprecated


class DcmLoadingException(Exception):
    def __init__(self, msg, *args,**kwargs):
        super(DcmLoadingException, self).__init__(args, kwargs)


@deprecated(version='1.0', reason='replaced by lymphangioma_segmentation.dicom')
def get_slice_location(path: str) -> float:
    """
    Get stack position from the number
    :param path:
    :return:
    """
    warnings.warn('', DeprecationWarning)
    dcm = pydicom.dcmread(path, force=True)
    # return dcm.InStackPositionNumber
    return float(dcm.SliceLocation)


@deprecated(version='1.0', reason='replaced by lymphangioma_segmentation.dicom')
def load_dcm_series(files: List[str]):
    """
    Check and load the given DICOM files
    :param files:
    :return:
    """
    warnings.warn('', DeprecationWarning)
    volume = []
    files.sort(key=get_slice_location)
    for file in files:
        dcm = pydicom.dcmread(file, force=True)
        if not dcm.file_meta.get('TransferSyntaxUID'):
            dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        volume.append(dcm.pixel_array)
    return files, np.stack(volume)


@deprecated(version='1.0', reason='replaced by lymphangioma_segmentation.dicom')
def get_voxel_size(path: str) -> float:
    """
    Get the voxel size of the DICOM file
    :param path:
    :return:
    """
    warnings.warn('', DeprecationWarning)
    dcm = pydicom.dcmread(path, force=True)
    x_str, y_str = dcm.PixelSpacing
    x = float(x_str)
    y = float(y_str)
    z = float(dcm.SpacingBetweenSlices)
    return x * y * z
