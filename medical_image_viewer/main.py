"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import logging
from typing import List, Tuple

from PySide2 import QtWidgets
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QMenuBar, QMenu, QAction, QFileDialog, QTextBrowser, \
    QMessageBox, QLabel
import numpy as np

from store import State
from widgets.histogram_lut import MivHistogramLUTWidget
from widgets.image_view import MivImageView, ViewMode
from utils import dicom
from lymphangioma_segmentation import segmentation
from lymphangioma_segmentation.image import Pixel


class MainWindow(QWidget):
    def __init__(self, files: List[str] = []):
        super().__init__()
        self.state = State()
        self.ui = UiForm(self)

        # pg.show(np.random.random([4, 5, 6]))
        self.ui.file_action.triggered.connect(self.open_files)
        self.ui.btn_seed_select.clicked.connect(self._select_seed)
        self.ui.btn_run.clicked.connect(self._run)

        if files:
            self._load_files(files)

    @property
    def threshold(self):
        text = self.ui.input_threshold.text()
        threshold = 0
        if text:
            threshold = float(text)
        else:
            self.ui.input_threshold.setText('0.0')
        return threshold

    @staticmethod
    def _create_seed_pixel(seed: Tuple[int, int, int]):
        return Pixel(seed[1], seed[2], seed[0])

    @Slot()
    def _run(self):
        try:
            threshold = self.threshold
            seed_ = self.state.seed
            # convert the coordinate to a Pixel object
            seed = self._create_seed_pixel(seed_)
            volume = self.state.volume
            logging.info(f'{threshold}, {seed_}, volume shape: {volume.shape}')
        except AssertionError as e:
            QMessageBox.warning(self, '警告', f'请检查种子点、分割阈值以及是否成功加载图像。{e}')
            return
        self.ui.text_result.setText(f'Running, seed: {seed_}, threshold: {threshold}, shape: {volume.shape}')

        # 注意seed和Pixel对象的坐标顺序

        overlay = segmentation.region_grow_3d(volume, seed, threshold)
        # overlay, _, _ = segmentation.grow_by_every_slice(seed, volume)

        self.state.set_overlay(overlay)

        self.ui.image_viewer.refresh()
        # QMessageBox.information(self, '完成', f'定量计算已完成')

        # Display the result in the text_result(QTextBrowser)
        num = overlay.sum()
        # TODO sure every slice has the same thickness and spacing
        voxel_size = float(self.ui.input_voxel_size.text())
        result_text = f'分割已结束\n' \
                      f'种子点：{seed}\n' \
                      f'阈值：{threshold}\n' \
                      f'体素数目: {num / 1000:.2f}k\n' \
                      f'体积：{num * voxel_size / 1000 : .2f}cm3'
        self.ui.text_result.setText(result_text)

    @Slot()
    def _select_seed(self):
        self.ui.image_viewer.set_view_mode(ViewMode.PIXEL_SELECTION)
        self.ui.image_viewer.pixelSelected.connect(self._pixel_selected)

    @Slot(tuple, float)
    def _pixel_selected(self, pos: Tuple[int, int, int], value):
        index, x, y = pos

        self.state.set_seed(pos)
        self.ui.input_seed.setText(f'({index}, {x}, {y}), {value}')

        # compute the threshold
        seed_pixel = self._create_seed_pixel(self.state.seed)
        volume = self.state.volume

        def get_reference_intensity():
            neighbors = seed_pixel.get_26_neighborhood_3d(volume)
            value_arr = []
            for s in neighbors:
                value_arr.append(s.get_pixel_3d(volume))
            return np.array(value_arr).mean()

        # reference_intensity = get_reference_intensity()
        # slice_ = seed_pixel.get_slice(volume)
        # threshold, _ = segmentation.get_optimized_threshold(slice_, seed_pixel, reference_intensity, 1.1)

        _, mean, std = segmentation.grow_by_every_slice(seed_pixel, volume, 3)
        # threshold = mean - std * 1.5
        threshold = mean - std
        # threshold = mean

        self.ui.input_threshold.setText(f'{threshold:.1f}')

        self.ui.image_viewer.pixelSelected.disconnect(self._pixel_selected)

    def _display_images(self, volume: np.ndarray, files: List[str]):
        # Clear the overlay
        self.ui.image_viewer.clear_overlay()

        self.ui.image_viewer.refresh()

    def _load_files(self, files: List[str]):
        """
        Load DICOM files
        :param files:
        :return:
        """
        state = self.state
        try:
            files, volume = dicom.load_dcm_series(files)
            # np.save('test2.npy', volume)
            voxel_size = dicom.get_voxel_size(files[0])
            # state.set_voxel_size(voxel_size)
            self.ui.input_voxel_size.setText(str(voxel_size))

            state.set_overlay(None)
            state.set_volume(volume, files)

            self._display_images(volume, files)

        except dicom.DcmLoadingException:
            # TODO show error box
            pass

    @Slot()
    def open_files(self):
        """
        This is the test function,
        :return:
        """
        files, _ = QFileDialog.getOpenFileNames()
        if files:
            self._load_files(files)


class UiForm:
    def __init__(self, form: MainWindow):
        self.menu_bar = QMenuBar(form)

        self.menu_file = QMenu('文件')
        self.menu_bar.addMenu(self.menu_file)
        self.file_action = QAction('打开')
        # menu = QMenu('文件')
        self.menu_file.addAction(self.file_action)

        #
        self.root_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_form = QtWidgets.QFormLayout()
        self.left_result = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()

        # 操作按钮
        self.btn_seed_select = QPushButton('选择种子点')
        self.input_seed = QLineEdit()
        self.input_seed.setDisabled(True)

        self.input_threshold = QLineEdit('')
        self.input_threshold.setPlaceholderText('')

        self.input_voxel_size = QLineEdit('')
        self.btn_run = QPushButton('运行')
        self.text_result = QTextBrowser()

        #
        self.left_form.addRow(self.btn_seed_select, self.input_seed)
        self.left_form.addRow('生长阈值', self.input_threshold)
        self.left_form.addRow('体素尺寸(mm3)', self.input_voxel_size)

        #
        self.image_viewer = MivImageView(form.state)
        self.histogram_LUT = MivHistogramLUTWidget(self.image_viewer.ui.image_item)

        self.root_layout.addWidget(self.menu_bar)
        self.right_layout.addWidget(self.image_viewer)
        self.left_result.addWidget(self.btn_run)
        self.left_result.addWidget(QLabel('计算结果'))
        self.left_result.addWidget(self.text_result)

        self.main_layout.addLayout(self.left_layout, 3)
        self.left_layout.addLayout(self.left_form)
        self.left_layout.addLayout(self.left_result)
        self.main_layout.addLayout(self.right_layout, 6)
        self.main_layout.addWidget(self.histogram_LUT, 1)
        self.root_layout.addLayout(self.main_layout)
        form.setLayout(self.root_layout)


def config_log():
    logging.basicConfig(level=logging.DEBUG,
                        # filename="debug.log",
                        format="%(asctime)s %(filename)s %(lineno)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S",
                        filemode="w")


if __name__ == '__main__':
    import sys
    import os

    # config_log()
    app = QtWidgets.QApplication([])

    dcm_files = []
    if len(sys.argv) > 1:
        dcm_dir = sys.argv[1]
        dcm_files = os.listdir(dcm_dir)
        for i in range(len(dcm_files)):
            dcm_files[i] = os.path.join(dcm_dir, dcm_files[i])

    widget = MainWindow(files=dcm_files)

    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
