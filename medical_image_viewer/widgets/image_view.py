"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import numpy as np
import pyqtgraph as pg
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSlider
from PySide2 import QtCore


class MivImageView(QWidget):
    def __init__(self):
        super().__init__()
        self.root_layout = QVBoxLayout()
        self.image_view = pg.ImageView()
        self.slice_slider = QSlider(QtCore.Qt.Horizontal)

        self.root_layout.addWidget(self.image_view)
        self.root_layout.addWidget(self.slice_slider)
        self.setLayout(self.root_layout)

    def set_image(self, img: np.ndarray):
        assert img.ndim == 3
        self.slice_slider.setRange(1, len(img))
        self.image_view.setImage(img[0])

    def show_random_image(self):
        img = np.random.random((60, 60, 60))
        self.set_image(img)


if __name__ == '__main__':
    import pydicom
    from PySide2.QtWidgets import QWidget, QApplication
    import sys

    app = QApplication()

    dcm = pydicom.dcmread('../data/dicom/1_2_8001.DCM', force=True)
    # file_meta没有内容，但是我们需要其中的TranserSyntaxUID字段，没有则设置默认小端
    if not dcm.file_meta.get('TransferSyntaxUID'):
        dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    arr = dcm.pixel_array

    window = MivImageView()
    # window.image_view.setImage(arr)
    window.show_random_image()
    window.show()
    sys.exit(app.exec_())
