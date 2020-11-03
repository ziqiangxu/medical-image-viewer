"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
from typing import List

from PySide2 import QtWidgets
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QMenuBar, QMenu, QAction, QFileDialog
import numpy as np

from store import State
from widgets.image_view import MivImageView, ViewMode
from utils import dicom


class MainWindow(QWidget):
    def __init__(self, files: List[str] = []):
        super().__init__()
        self.state = State()
        self.ui = UiForm(self)

        # pg.show(np.random.random([4, 5, 6]))
        self.ui.file_action.triggered.connect(self.open_files)
        self.ui.btn_seed_select.clicked.connect(self._select_seed)
        self.ui.image_viewer.pixelSelected.connect(self._pixel_selected)

        if files:
            self._load_dcm_files(files)

    def _select_seed(self):
        self.ui.image_viewer.set_view_mode(ViewMode.PIXEL_SELECTION)

    def _pixel_selected(self, index, x, y, value):
        self.ui.input_seed.setText(f'({index}, {x}, {y}), {value}')
        # self.disconnect(MivImageView.pixel, self)

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

        self.root_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QFormLayout()
        self.left_layout.addRow(self.btn_seed_select, self.input_seed)
        self.left_layout.addRow(QPushButton('生长阈值'), QLineEdit())

        self.image_viewer = MivImageView(form.state)

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.image_viewer)

        self.root_layout.addWidget(self.menu_bar)
        self.main_layout.addLayout(self.left_layout, 2)
        self.main_layout.addLayout(self.right_layout, 6)
        self.root_layout.addLayout(self.main_layout)
        form.setLayout(self.root_layout)


if __name__ == '__main__':
    import sys
    import os

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
