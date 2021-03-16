"""
@Author: Daryl Xu
"""
import logging
import math

import numpy as np
from numpy import ndarray
import pyqtgraph as pg
from PySide2.QtCore import Slot, QRect
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout, QComboBox, QMessageBox
from PySide2 import QtCore
from lymphangioma_segmentation.image import Pixel
from lymphangioma_segmentation import segmentation as seg
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent

from store import State, UpdateMode
from utils import public
from constant import ViewMode, Algorithm


class MivImageView(QWidget):
    # signal
    pixelSelected = QtCore.Signal(tuple, float)

    def __init__(self, state: State):
        super().__init__()
        self.state = state
        self.ui = UiForm(self)

        self._mode = ViewMode.VIEW
        self.roi: pg.ROI
        self.ui.image_item.mouseClickEvent = self._image_item_clicked
        self.ui.slice_slider.valueChanged.connect(self._show_current_slice)

    @property
    def view_mode(self):
        return self._mode

    def _check_roi(self):
        if hasattr(self, 'roi'):
            return True
        else:
            QMessageBox.warning(self, '注意', '请选择要调整的区域')
            return False

    def segment_roi(self, algorithm: Algorithm, threshold: float):
        if not self._check_roi():
            return
        current_slice = self.get_current_slice()
        roi_arr = self.roi.getArrayRegion(current_slice, self.ui.image_item)

        if Algorithm.GROW_EVERY_SLICE == algorithm:
            mask = seg.fine_tune_roi(roi_arr, self.state.volume, self.state.overlay)
        else:
            mask = seg.fine_tune_roi1(roi_arr, threshold)
        self._update_mask_under_roi(mask, UpdateMode.APPEND)

    def erase_roi(self):
        if not self._check_roi():
            return
        w_, h_ = self.roi.size()
        w, h = int(math.ceil(w_)), int(math.ceil(h_))
        mask = np.zeros((int(w), int(h)), np.int8)
        self._update_mask_under_roi(mask, UpdateMode.OVER_WRITE)

    def _update_mask_under_roi(self, mask, update_mode: UpdateMode):
        """
        更新overlay ROI选中的区域
        Update the area in overlay where selected by ROI
        :param mask:
        :param update_mode: update mode
        :return:
        """
        w_, h_ = self.roi.size()
        w, h = int(math.ceil(w_)), int(math.ceil(h_))
        assert mask.shape == (w, h)
        x, y = self.roi.pos()
        position = Pixel(int(y), int(x), self.ui.slice_slider.value())
        self.state.update_overlay(position, mask, update_mode)
        self.refresh()

    def get_current_slice(self) -> ndarray:
        index = self.ui.slice_slider.value()
        return self.state.volume[index]

    def set_view_mode(self, mode: ViewMode):
        """
        the mode can be ViewMode
        :param mode:
        :return:
        """
        if mode == self._mode:
            return
        self._mode = mode
        self.ui.view_mode_selector.setCurrentText(mode.value)

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

    def clear_overlay(self):
        self.ui.image_item_overlay.clear()

    def _image_item_clicked(self, event: MouseClickEvent):
        if ViewMode.VIEW == self._mode:
            return

        index = self.ui.slice_slider.value()
        position = event.pos()
        x, y = int(position[0]), int(position[1])
        if ViewMode.PIXEL_SELECTION == self._mode:
            logging.debug(f'the position: ({x}, {y})')
            value = self.state.volume[index][x, y]
            logging.debug(f'value of the clicked pixel: {value}')
            # The pixel's index and intensity of the pixel
            self.pixelSelected.emit((index, x, y), value)
        elif ViewMode.ROI_SELECTION == self._mode:
            # TODO create a ROI widget on self.image_item
            roi = pg.ROI((x, y), pg.Point(20, 40))
            if hasattr(self, 'roi'):
                # remove the previous roi
                self.ui.view_box.removeItem(self.roi)
            self.roi = roi
            roi.addScaleHandle([1, 1], [0, 0])
            roi.addScaleHandle([0, 0], [1, 1])
            self.ui.view_box.addItem(roi)

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
        self.view_box.setBackgroundColor([80, 80, 80])
        self.graphic_view.setCentralItem(self.view_box)

        self.image_item = pg.ImageItem()  # 显示图像的控件
        self.view_box.addItem(self.image_item)

        self.image_item_overlay = pg.ImageItem()
        self.image_item_overlay.setLookupTable(public.get_look_up_table())  # 配置overlay控件的颜色查找表
        self.view_box.addItem(self.image_item_overlay)

        # self.graphic_view.addItem(self.image_item)

        self.text_top_right = pg.TextItem()
        self.text_top_right.setText('')
        self.graphic_view.addItem(self.text_top_right)

        # Qt的相关控件
        self.slice_slider = QSlider(QtCore.Qt.Horizontal)
        self.slice_label = QLabel()
        self.view_mode_selector = QComboBox()
        self.view_mode_selector.setEnabled(False)
        self.view_mode_selector.addItems([mode.value for mode in ViewMode.__members__.values()])

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
