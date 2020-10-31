"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
from typing import List

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QSlider, QMenuBar, QMenu, QAction, QFileDialog
import pyqtgraph as pg
import numpy as np

import public
from store import State
from widgets.image_view import MivImageView


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.state = State()
        self.menu_bar = QMenuBar(self)
        # pg.show(np.random.random([4, 5, 6]))

        self.menu_file = QMenu('文件')
        self.menu_bar.addMenu(self.menu_file)
        self.file_action = QAction('打开')
        self.file_action.triggered.connect(self.open_files)
        # menu = QMenu('文件')
        self.menu_file.addAction(self.file_action)

        self.root_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QFormLayout()
        self.left_layout.addRow(QPushButton('选择种子点'), QLineEdit())
        self.left_layout.addRow(QPushButton('生长阈值'), QLineEdit())

        self.image_viewer = MivImageView(self.state)

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.addWidget(self.image_viewer)

        self.root_layout.addWidget(self.menu_bar)
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)
        self.root_layout.addLayout(self.main_layout)
        self.setLayout(self.root_layout)

    def _display_images(self, volume: np.ndarray, files: List[str]):
        self.state.set_volume(volume, files)
        self.image_viewer.refresh()

    def open_files(self):
        """
        This is the test function,
        :return:
        """
        files, _ = QFileDialog.getOpenFileNames()
        if files:
            try:
                files, volume = public.load_dcm_series(files)
                self._display_images(volume, files)
                # TODO display the image in the image view

            except public.DcmLoadingException:
                # TODO show error box
                pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
