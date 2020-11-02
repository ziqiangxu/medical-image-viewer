"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import numpy as np
import pyqtgraph as pg
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSlider
from PySide2 import QtCore

from store import State


class UiForm:
    def __init__(self, parent: QWidget):
        self.root_layout = QVBoxLayout()
        self.image_view = pg.ImageView()
        self.slice_slider = QSlider(QtCore.Qt.Horizontal)

        # TODO display the frame
        self.text_slice = pg.TextItem()

        self.root_layout.addWidget(self.image_view)
        self.root_layout.addWidget(self.slice_slider)

        parent.setLayout(self.root_layout)


class MivImageView(QWidget):
    def __init__(self, state: State):
        super().__init__()
        self.state = state
        self.ui = UiForm(self)

        self.ui.slice_slider.valueChanged.connect(self._show_current_slice)

    def _show_current_slice(self):
        index = self.ui.slice_slider.value()
        self.ui.image_view.setImage(self.state.volume[index])
        self.ui.image_view.setImage(self.state.volume[index])

    def refresh(self):
        # TODO some other updating operations
        self.ui.slice_slider.setRange(0, self.state.volume.shape[0] - 1)
        self._show_current_slice()

        # TODO remove the test code
        # pg.image(self.state.volume)

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
