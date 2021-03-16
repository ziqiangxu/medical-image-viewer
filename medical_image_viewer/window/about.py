"""
@Author: Daryl Xu
The about window
"""
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QDialog


class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.setWindowTitle('关于')

        self._text = QTextBrowser()
        self._text.setText(
            # '本程序用于对淋巴血管瘤的分割\n'
            '软件版本：1.0.0-beta.1'
        )

        self._layout.addWidget(self._text)
        self.show()
