from scipy import ndimage
import numpy as np
from numpy import ndarray
import nibabel as nib


def remove_small_object(input: ndarray, size_threshold: int) -> ndarray:
    """
    移除小对象，联通域
    """
    labels, num = ndimage.label(input, np.ones((3, 3, 3)))
    save_mask = np.zeros(input.shape)
    print(labels.shape, f'{num} objects found!')
    for i in range(1, num):
        current_label = labels == i
        volume = np.count_nonzero(current_label)
        if volume > size_threshold:
            print(f'label: {i}, volume: {volume}')
            save_mask[labels == i] = 1
    return save_mask


if __name__ == '__main__':
    manual_vessel = '/home/daryl/seg-tmp/vessel_mask.nii.gz'
    merged_vessel_path = '/home/daryl/merge_mask_seprated.nii.gz'
    nii: nib.Nifti1Image = nib.load(merged_vessel_path)
    img = nii.get_fdata()
    output = remove_small_object(img, 100)

    nii._dataobj = output
    nib.save(nii, '/home/daryl/target_mask.nii.gz')

    nii = nib.load(manual_vessel)
    manual_vessel_mask = nii.get_fdata()
    debug = output + manual_vessel_mask
    nii._dataobj = debug
    nib.save(nii, '/home/daryl/debug.nii.gz')
