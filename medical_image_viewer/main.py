"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
import logging
from typing import List, Tuple

from PySide2 import QtWidgets
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QMenuBar, QMenu, QAction, QFileDialog, QTextBrowser, \
    QMessageBox
import numpy as np

from store import State
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
            self._load_dcm_files(files)

    @property
    def threshold(self):
        text = self.ui.input_threshold.text()
        threshold = 0
        if text:
            threshold = float(text)
        else:
            self.ui.input_threshold.setText('0.0')
        return threshold

    @Slot()
    def _run(self):
        try:
            threshold = self.threshold
            seed = self.state.seed
            volume = self.state.volume
            logging.info(f'{threshold}, {seed}, volume shape: {volume.shape}')
        except AssertionError as e:
            QMessageBox.warning(self, '警告', f'请检查种子点、分割阈值以及是否成功加载图像。{e}')
            return
        self.ui.text_result.setText(f'Running, seed: {seed}, threshold: {threshold}, shape: {volume.shape}')

        seed = self.state.seed
        # 注意seed和Pixel对象的坐标顺序
        overlay = segmentation.region_grow_3d(volume, Pixel(seed[1], seed[2], seed[0]), self.threshold)
        self.state.set_overlay(overlay)

        self.ui.image_viewer.refresh()
        QMessageBox.information(self, '完成', f'定量计算已完成')

    @Slot()
    def _select_seed(self):
        self.ui.image_viewer.set_view_mode(ViewMode.PIXEL_SELECTION)
        self.ui.image_viewer.pixelSelected.connect(self._pixel_selected)

    @Slot(tuple, float)
    def _pixel_selected(self, pos: Tuple[int, int, int], value):
        index, x, y = pos

        self.state.set_seed(pos)
        self.ui.input_seed.setText(f'({index}, {x}, {y}), {value}')

        self.ui.image_viewer.pixelSelected.disconnect(self._pixel_selected)

    def _display_images(self, volume: np.ndarray, files: List[str]):
        self.state.set_volume(volume, files)
        self.ui.image_viewer.refresh()

    def _load_dcm_files(self, files: List[str]):
        """
        Load DICOM files
        :param files:
        :return:
        """
        try:
            files, volume = dicom.load_dcm_series(files)
            self._display_images(volume, files)
            # TODO display the image in the image view

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
            self._load_dcm_files(files)


class UiForm:
    def __init__(self, form: MainWindow):
        self.menu_bar = QMenuBar(form)

        self.menu_file = QMenu('文件')
        self.menu_bar.addMenu(self.menu_file)
        self.file_action = QAction('打开')
        # menu = QMenu('文件')
        self.menu_file.addAction(self.file_action)

        # 操作按钮
        self.btn_seed_select = QPushButton('选择种子点')
        self.input_seed = QLineEdit()
        self.input_threshold = QLineEdit('1200.0')
        self.btn_run = QPushButton('运行')
        self.text_result = QTextBrowser()

        self.root_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_form = QtWidgets.QFormLayout()
        self.left_result = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()

        self.left_form.addRow(self.btn_seed_select, self.input_seed)
        self.left_form.addRow('生长阈值', self.input_threshold)

        self.image_viewer = MivImageView(form.state)

        self.root_layout.addWidget(self.menu_bar)
        self.right_layout.addWidget(self.image_viewer)
        self.left_result.addWidget(self.btn_run)
        self.left_result.addWidget(self.text_result)

        self.main_layout.addLayout(self.left_layout, 3)
        self.left_layout.addLayout(self.left_form)
        self.left_layout.addLayout(self.left_result)
        self.main_layout.addLayout(self.right_layout, 6)
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

    config_log()
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
