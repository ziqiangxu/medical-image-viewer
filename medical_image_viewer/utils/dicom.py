"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
from typing import List

import pydicom
import numpy as np


class DcmLoadingException(Exception):
    def __init__(self, msg, *args,**kwargs):
        super(DcmLoadingException, self).__init__(args, kwargs)


def get_slice_location(path: str):
    """
    Get stack position from the number
    :param path:
    :return:
    """

    dcm = pydicom.dcmread(path, force=True)
    # return dcm.InStackPositionNumber
    return dcm.SliceLocation


def load_dcm_series(files: List[str]):
    """
    Check and load the given DICOM files
    :param files:
    :return:
    """
    volume = []
    files.sort(key=get_slice_location)
    for file in files:
        dcm = pydicom.dcmread(file, force=True)
        if not dcm.file_meta.get('TransferSyntaxUID'):
            dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        volume.append(dcm.pixel_array)
    return files, np.stack(volume)
