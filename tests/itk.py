import SimpleITK as sitk
import numpy as np
# from ..SimpleITK_Notebooks.Python import gui

print(sitk.Version())
file_path = '/home/daryl/002/liver/CleanNII/liver_2.nii.gz'
T1_WINDOW_LEVEL = (1050, 500)
img_T1 = sitk.ReadImage(file_path)
# img_T1_255 = sitk.Cast(sitk.IntensityWindowing(img_T1), sitk.sitkUInt8)

# sitk.Show(img_T1)
arr = sitk.GetArrayFromImage(img_T1)
min_pixel = arr.min()
arr -= min_pixel
max_pixel = arr.max()
arr = arr.astype(np.float_) / max_pixel * 255
# arr = arr / max_pixel * 255
print(min_pixel, max_pixel)
img = sitk.GetImageFromArray(arr)
sitk.Show(img, debugOn=True)


