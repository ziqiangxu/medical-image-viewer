"""
Author: Daryl.Xu
E-mail: ziqiang_xu@qq.com
"""
from pyqtgraph import HistogramLUTItem, GraphicsView


class MivHistogramLUTWidget(GraphicsView):
    def __init__(self, image_item):
        super().__init__()
        self.item = HistogramLUTItem(image_item)
        self.setCentralItem(self.item)
