"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import logging
from enum import Enum, unique

import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import Slot, QRect
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout
from PySide2 import QtCore
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent

from store import State
from utils import public


@unique
class ViewMode(Enum):
    VIEW = 0
    PIXEL_SELECTION = 1


class MivImageView(QWidget):
    # signal
    pixelSelected = QtCore.Signal(tuple, float)

    def __init__(self, state: State):
        super().__init__()
        self.state = state
        self.ui = UiForm(self)

        self._mode = ViewMode.VIEW

        self.ui.image_item.mouseClickEvent = self._image_item_clicked
        self.ui.slice_slider.valueChanged.connect(self._show_current_slice)

    @property
    def view_mode(self):
        return self._mode

    def set_view_mode(self, mode: ViewMode):
        """
        the mode can be ViewMode
        :param mode:
        :return:
        """
        self._mode = mode

    @Slot(int)
    def _show_current_slice(self, index: int):
        """
        :param index: value of the slider
        :return:
        """
        self.ui.image_item.setImage(self.state.volume[index])
        self.ui.image_item.setImage(self.state.volume[index])

        self._show_overlay(index)

        # Update the slice index
        self.ui.slice_label.setText(f'{index + 1} / {self.state.volume.shape[0]}')

    def _add_overlay(self, overlay: np.ndarray):
        self.state.set_overlay(overlay)

    def _show_overlay(self, index):
        overlay = self.state.overlay
        if overlay is not None:
            self.ui.image_item_overlay.setImage(overlay[index])

    def _image_item_clicked(self, event: MouseClickEvent):
        if self._mode == ViewMode.PIXEL_SELECTION:
            index = self.ui.slice_slider.value()
            position = event.pos()
            x, y = int(position[0]), int(position[1])
            logging.debug(f'the position: ({x}, {y})')
            value = self.state.volume[index][x, y]
            logging.debug(f'value of the clicked pixel: {value}')
            # The pixel's index and intensity of the pixel
            self.pixelSelected.emit((index, x, y), value)

    def refresh(self):
        # TODO what about overwrite update?
        self.ui.slice_slider.setRange(0, self.state.volume.shape[0] - 1)
        index = self.ui.slice_slider.value()
        self._show_current_slice(index)

    def show_random_image(self):
        img = np.random.random((60, 60, 60))
        self.set_image(img)


class UiForm:
    def __init__(self, parent: MivImageView):
        self.root_layout = QVBoxLayout()

        self.graphic_view = pg.GraphicsView()  # 被改写过的QGraphicView
        self.view_box = pg.ViewBox(invertY=True)  # 用于盛放图像控件，支持缩放功能
        self.view_box.setBackgroundColor([0, 0, 200])
        self.graphic_view.setCentralItem(self.view_box)

        self.image_item = pg.ImageItem()  # 显示图像的控件
        self.view_box.addItem(self.image_item)
        self.image_item_overlay = pg.ImageItem()
        self.image_item_overlay.setLookupTable(public.get_look_up_table())  # 配置overlay控件的颜色查找表
        self.view_box.addItem(self.image_item_overlay)

        # self.graphic_view.addItem(self.image_item)

        self.text_top_right = pg.TextItem()
        self.text_top_right.setText('the text item')
        self.graphic_view.addItem(self.text_top_right)

        # Qt的相关控件
        self.slice_slider = QSlider(QtCore.Qt.Horizontal)
        self.slice_label = QLabel()

        # 布局相关
        self.root_layout.addWidget(self.graphic_view)

        self.layout_slider = QHBoxLayout()
        self.layout_slider.addWidget(self.slice_slider)
        self.layout_slider.addWidget(self.slice_label)
        self.root_layout.addLayout(self.layout_slider)

        parent.setLayout(self.root_layout)


if __name__ == '__main__':
    import pydicom
    from PySide2.QtWidgets import QWidget, QApplication
    import sys

    app = QApplication()

    dcm = pydicom.dcmread('../data/dicom/1_2_8001.DCM', force=True)
    # file_meta没有内容，但是我们需要其中的TransferSyntaxUID字段，没有则设置默认小端
    if not dcm.file_meta.get('TransferSyntaxUID'):
        dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    arr = dcm.pixel_array

    window = MivImageView()
    # window.image_view.setImage(arr)
    window.show_random_image()
    window.show()
    sys.exit(app.exec_())
