from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, pyqtSlot, QStandardPaths
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QPaintEvent, QMouseEvent, QFont
from PyQt5.QtWidgets import QApplication, QGridLayout, QSplitter, QWidget, QSlider, \
    QRadioButton, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QDoubleSpinBox, QPushButton, QFileDialog

import imageio, cv2
from PIL import Image
from matplotlib import image
import numpy as np

class MaskWidget(QWidget):
    def __init__(self, parent, img_path, alpha=0.5) -> None:
        super(MaskWidget, self).__init__()
        self.parent = parent
        self.img_path = img_path
        self.image = imageio.imread(img_path)
        self.ori_image = imageio.imread(img_path)
        self.blend_alpha = alpha
        h, w = self.image.shape[:2]
        ### set the larger edge length to RESOLUTION
        self.resize_ratio = self.parent.RESOLUTION / max(h, w)
        self.image = cv2.resize(self.image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))
        self.ori_image = cv2.resize(self.ori_image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))

        self.setFixedSize(self.parent.RESOLUTION, self.parent.RESOLUTION)


    def load(self, img_path):
        img = imageio.imread(img_path)
        h, w = img.shape[:2]
        # self.setFixedSize(w, h)
        self.pixmap = QPixmap(img_path)
        if h > w:
            self.pixmap = self.pixmap.scaledToHeight(self.parent.RESOLUTION)
        else:
            self.pixmap = self.pixmap.scaledToWidth(self.parent.RESOLUTION)
        self.resize_ratio = max(h, w) / self.parent.RESOLUTION
        self.update()


    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        self.image = self.ori_image * self.blend_alpha + np.one_like(self.ori_image) * (1 - self.blend_alpha)
        pixmap = Image.fromarray(self.image).toqpixmap()
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
