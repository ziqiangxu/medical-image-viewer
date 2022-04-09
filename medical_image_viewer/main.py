"""
@Author: Daryl Xu
"""
import logging
from typing import List, Tuple

from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QMenuBar, QMenu, QAction, QFileDialog, QTextBrowser, \
    QMessageBox, QLabel, QComboBox, QSlider
import numpy as np
from lymphangioma_segmentation import segmentation
from lymphangioma_segmentation.image import Pixel
from lymphangioma_segmentation import image

from constant import Algorithm
from store import State
from widgets.histogram_lut import MivHistogramLUTWidget
from widgets.image_view import MivImageView, ViewMode
from window.about import AboutWindow


class MainWindow(QWidget):
    def __init__(self, files: List[str] = []):
        super().__init__()
        self.state = State(self)
        self.ui = UiForm(self)

        # pg.show(np.random.random([4, 5, 6]))
        self.ui.action_file_open.triggered.connect(self.open_files)
        self.ui.action_help_about.triggered.connect(self._show_about)
        self.ui.btn_seed_select.clicked.connect(self._select_seed)
        self.ui.btn_run.clicked.connect(self._run)
        self.ui.btn_fine_tune.clicked.connect(self._fine_tune_clicked)
        self.ui.btn_erase.clicked.connect(self._btn_erase_clicked)
        self.ui.btn_fine_seg.clicked.connect(self._btn_fine_seg)
        self.ui.btn_test.clicked.connect(self._test_clicked)
        self.ui.combo_algorithm.currentTextChanged.connect(self._algorithm_changed)
        self.ui.threshold_slider.valueChanged.connect(self.threshold_slider_value_changed)
        self.state.overlayUpdated.connect(self._overlay_updated)

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

    @property
    def algorithm(self):
        return Algorithm(self.ui.combo_algorithm.currentText())

    @staticmethod
    def _create_seed_pixel(seed: Tuple[int, int, int]):
        return Pixel(seed[1], seed[2], seed[0])

    def _set_algorithm_ui_mode(self, algorithm: Algorithm):
        # About the switch mode, place the test value in the begin
        if Algorithm.GROW_EVERY_SLICE == algorithm:
            self.ui.input_threshold.setEnabled(False)
        elif Algorithm.BY_THRESHOLD == algorithm:
            self.ui.input_threshold.setEnabled(True)
        else:
            raise NotImplementedError

    @Slot()
    def _show_about(self):
        self._about = AboutWindow()

    @Slot()
    def _overlay_updated(self):
        """
        Overlay updated, update the statistic data in the window
        :return:
        """
        # Display the result in the text_result(QTextBrowser)
        num = self.state.overlay.sum()
        # TODO sure every slice has the same thickness and spacing
        voxel_size = float(self.ui.input_voxel_size.text())
        result_text = f'分割已结束\n' \
                      f'体素数目: {num / 1000:.2f}k\n' \
                      f'体积：{num * voxel_size / 1000 : .2f}cm3'
        self.ui.text_result.setText(result_text)

    @Slot()
    def _btn_fine_seg(self):
        self.ui.image_viewer.segment_roi(self.algorithm, self.threshold)

    @Slot()
    def _btn_erase_clicked(self):
        self.ui.image_viewer.erase_roi()

    @Slot(int)
    def threshold_slider_value_changed(self, value: int):
        self.ui.input_threshold.setText(str(value))

    @Slot()
    def _algorithm_changed(self):
        algorithm = Algorithm(self.ui.combo_algorithm.currentText())
        self._set_algorithm_ui_mode(algorithm)

    @Slot()
    def _test_clicked(self):
        # TODO need to be commented
        pass

    @Slot()
    def _fine_tune_clicked(self):
        # TODO get ROI in the image_viewer
        self.ui.image_viewer.set_view_mode(ViewMode.ROI_SELECTION)

    @Slot()
    def _run(self):
        try:
            seed_ = self.state.seed
            # convert the coordinate to a Pixel object
            seed = self._create_seed_pixel(seed_)
            volume = self.state.volume
            logging.info(f'{seed_}, volume shape: {volume.shape}')
        except AssertionError as e:
            QMessageBox.warning(self, '警告', f'请检查种子点、分割阈值以及是否成功加载图像。{e}')
            return

        # 注意seed和Pixel对象的坐标顺序

        algorithm = Algorithm(self.ui.combo_algorithm.currentText())
        if Algorithm.GROW_EVERY_SLICE == algorithm:
            overlay, _, _ = segmentation.grow_by_every_slice(seed, volume, ratio=3, min_iter=5)
            self.ui.text_result.setText(f'Running, seed: {seed_}, shape: {volume.shape}')
        elif Algorithm.BY_THRESHOLD == algorithm:
            threshold = self.threshold
            overlay = segmentation.region_grow_3d(volume, seed, threshold)
            self.ui.text_result.setText(f'Running, seed: {seed_}, threshold: {threshold}, shape: {volume.shape}')
        else:
            raise NotImplementedError

        self.state.set_overlay(overlay)

        self.ui.image_viewer.refresh()
        # QMessageBox.information(self, '完成', f'定量计算已完成')
        self._overlay_updated()

    @Slot()
    def _select_seed(self):
        self.ui.image_viewer.set_view_mode(ViewMode.PIXEL_SELECTION)
        self.ui.image_viewer.pixelSelected.connect(self._pixel_selected)

    @Slot(tuple, float)
    def _pixel_selected(self, pos: Tuple[int, int, int], value):
        index, x, y = pos

        self.state.set_seed(pos)
        self.ui.input_seed.setText(f'({index}, {x}, {y}), {value:.1f}')

        # compute the threshold
        seed_pixel = self._create_seed_pixel(self.state.seed)
        volume = self.state.volume

        def get_reference_intensity():
            neighbors = seed_pixel.get_26_neighborhood_3d(volume)
            value_arr = []
            for s in neighbors:
                value_arr.append(s.get_pixel_3d(volume))
            return np.array(value_arr).mean()

        algorithm = Algorithm(self.ui.combo_algorithm.currentText())
        if Algorithm.BY_THRESHOLD == algorithm:

            reference_intensity = get_reference_intensity()
            slice_ = seed_pixel.get_slice(volume)
            threshold, _ = segmentation.get_optimized_threshold(slice_, seed_pixel, reference_intensity, 1.1)

            _, mean, std = segmentation.grow_by_every_slice(seed_pixel, volume, 3)
            threshold = mean - std * 1.5

            # threshold = mean - std
            # threshold = mean
            self.ui.input_threshold.setText(f'{threshold:.1f}')
            self.ui.threshold_slider.setEnabled(True)
            self.ui.threshold_slider.setRange(mean - 3 * std, mean + 3 * std)
            self.ui.threshold_slider.setValue(threshold)
        elif algorithm == Algorithm.GROW_EVERY_SLICE:
            self.ui.threshold_slider.setEnabled(False)
            pass
        else:
            raise NotImplementedError

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

        test_file = files[0].lower()
        if test_file.endswith('.jpg'):
            # If jpg files got
            for file in files:
                assert file.endswith('.jpg')
            files, volume = image.load_jpg_series(files)
            voxel_size = 0
        elif test_file.endswith('.nii') or test_file.endswith('.nii.gz'):
           raise NotImplementedError
        else:
            # or DCM files
            try:
                files, volume = image.load_dcm_series(files)
                # np.save('test2.npy', volume)
                voxel_size = image.get_voxel_size(files[0])
            except image.DcmLoadingException:
                # TODO show error box
                return

        # state.set_voxel_size(voxel_size)
        self.ui.input_voxel_size.setText(str(voxel_size))
        state.set_volume(volume, files)
        state.set_overlay(np.zeros(volume.shape, np.int8))

        self._display_images(volume, files)

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
        self.menu_help = QMenu('帮助')
        self.menu_bar.addMenu(self.menu_file)
        self.menu_bar.addMenu(self.menu_help)
        self.action_file_open = QAction('打开')
        self.action_help_about = QAction('关于')
        # menu = QMenu('文件')
        self.menu_file.addAction(self.action_file_open)
        self.menu_help.addAction(self.action_help_about)

        #
        self.root_layout = QtWidgets.QVBoxLayout()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_form = QtWidgets.QFormLayout()
        self.left_result = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()
        self.fine_tune_layout = QtWidgets.QHBoxLayout()

        # 操作按钮
        self.btn_seed_select = QPushButton('选择种子点')
        self.input_seed = QLineEdit()
        self.input_seed.setDisabled(True)

        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems([item.value for item in Algorithm.__members__.values()])

        self.input_threshold = QLineEdit('0')
        self.input_threshold.setPlaceholderText('')
        self.input_voxel_size = QLineEdit('')
        self.threshold_slider = QSlider(QtCore.Qt.Horizontal)
        self.threshold_slider.setEnabled(False)

        self.btn_run = QPushButton('运行')
        self.btn_fine_tune = QPushButton('选择区域微调')
        self.btn_erase = QPushButton('擦除')
        self.btn_fine_seg = QPushButton('分割')
        self.btn_test = QPushButton('测试')
        self.text_result = QTextBrowser()

        #
        self.image_viewer = MivImageView(form.state)
        self.histogram_LUT = MivHistogramLUTWidget(self.image_viewer.ui.image_item)

        #
        self.left_form.addRow('显示模式', self.image_viewer.ui.view_mode_selector)
        self.left_form.addRow(self.btn_seed_select, self.input_seed)
        self.left_form.addRow('分割算法', self.combo_algorithm)
        self.left_form.addRow('体素尺寸(mm3)', self.input_voxel_size)
        self.left_form.addRow('生长阈值', self.input_threshold)

        self.root_layout.addWidget(self.menu_bar)
        self.right_layout.addWidget(self.image_viewer)
        self.left_result.addWidget(self.threshold_slider)
        self.left_result.addWidget(self.btn_run)
        self.left_result.addWidget(self.btn_fine_tune)

        self.left_result.addLayout(self.fine_tune_layout)
        self.fine_tune_layout.addWidget(self.btn_erase)
        self.fine_tune_layout.addWidget(self.btn_fine_seg)

        # 测试按钮
        # self.left_result.addWidget(self.btn_test)
        self.left_result.addWidget(QLabel('计算结果'))
        self.left_result.addWidget(self.text_result)

        self.main_layout.addLayout(self.left_layout, 2)
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

    widget.resize(1000, 600)
    widget.setWindowTitle('medical-image-viewer')
    widget.show()

    sys.exit(app.exec_())
