"""
Include customized widgets used in HandyView.
"""

import os
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, \
    QFormLayout, QLineEdit, QSpinBox, QWidget

from handyview.utils import ROOT_DIR


def show_msg(icon='Information', title='Title', text='Message', timeout=None):
    """
    QMessageBox::NoIcon
    QMessageBox::Question
    QMessageBox::Information
    QMessageBox::Warning
    QMessageBox::Critical
    """
    if icon == 'NoIcon':
        icon = QMessageBox.NoIcon
    elif icon == 'Question':
        icon = QMessageBox.Question
    elif icon == 'Information':
        icon = QMessageBox.Information
    elif icon == 'Warning':
        icon = QMessageBox.Warning
    elif icon == 'Critical':
        icon = QMessageBox.Critical

    msg = QMessageBox()
    msg.setWindowIcon(QIcon(os.path.join(ROOT_DIR, 'icon.ico')))
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)

    if timeout is not None:
        timer = QtCore.QTimer(msg)
        timer.singleShot(timeout * 1000, msg.close)
        timer.start()

    msg.exec_()


class ColorLabel(QLabel):
    """Show color in QLabel.

    Args:
        text (str): Shown text. Default: None.
        color (tuple): RGBA value. Default: None.
    """

    def __init__(self, text=None, color=None, parent=None):
        super(ColorLabel, self).__init__(parent)
        self.parent = parent
        # self.setStyleSheet('border: 2px solid gray;')
        self.pixmap = QPixmap(40, 20)
        self.setPixmap(self.pixmap)
        if text is not None:
            self.setText(text)
        if color is not None:
            self.fill(color)

    def fill(self, color):
        if isinstance(color, (list, tuple)):
            self.pixmap.fill(QColor(*color))
        else:
            self.pixmap.fill(color)
        self.setPixmap(self.pixmap)


class HLine(QFrame):
    """Horizontal separation line used in dock window."""

    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class HVLable(QLabel):
    """QLabel with customized initializations."""

    def __init__(self, text, parent, color='black', font='Times', font_size=12):
        super(HVLable, self).__init__(text, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        if isinstance(color, str):
            self.setStyleSheet('QLabel {color : ' + color + ';}')
        else:
            # example: (0, 255, 0, 100)
            r, g, b, a = color
            rgba_str = f'{r}, {g}, {b}, {a}'
            self.setStyleSheet('QLabel {color : rgba(' + rgba_str + ');}')
        self.setFont(QFont(font, font_size))


class MessageDialog(QDialog):
    """Message dialog for showing both English and Chinese text."""

    def __init__(self, parent, text_en, text_cn):
        super(MessageDialog, self).__init__(parent)
        self.text_en = text_en
        self.text_cn = text_cn

        # buttons
        self.btn_close = QPushButton('Close', self)
        self.btn_close.clicked.connect(self.button_press)
        self.btn_cn = QPushButton('简体中文', self)
        self.btn_cn.clicked.connect(self.button_press)
        self.btn_en = QPushButton('English', self)
        self.btn_en.clicked.connect(self.button_press)
        self.layout_btn = QHBoxLayout()
        self.layout_btn.setSpacing(10)
        self.layout_btn.addWidget(self.btn_cn)
        self.layout_btn.addWidget(self.btn_en)
        self.layout_btn.addWidget(self.btn_close)

        self.text_label = HVLable(text_en, self, 'black', 'Times', 12)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.addWidget(self.text_label)
        self.layout.addLayout(self.layout_btn)
        self.setLayout(self.layout)

    def button_press(self):
        if self.sender() == self.btn_cn:
            self.setText(self.text_cn)
        elif self.sender() == self.btn_en:
            self.setText(self.text_en)
        else:
            self.close()

    def setText(self, text):
        self.text_label.setText(text)


# QLineEdit: https://blog.csdn.net/jia666666/article/details/81510502
class CompareSettingEdit(QDialog):
    def __init__(self, config) -> None:
        super(CompareSettingEdit, self).__init__()
        self.setWindowTitle("Compare setting")
        self.setMinimumWidth(600)

        self.config = config

        num_view = self.config.get("num_view", 0)  # default view number is 0
        zoom_factor = self.config.get("zoom_factor", 1.0)  # default zoom factor is 1.0
        folder_paths = []
        for idx in range(num_view):
            folder_paths.append(self.config["view%d_folder" % idx])
        self.num_view = num_view

        self.num_view_line, self.zoom_factor_line = QSpinBox(), QLineEdit()
        int_validator, double_validator = QIntValidator(self), QDoubleValidator(self)
        # int_validator.setRange(1,4)
        self.num_view_line.setRange(1,4)
        double_validator.setRange(0,10)
        double_validator.setDecimals(2)
        # self.num_view_line.setValidator(int_validator)
        self.zoom_factor_line.setValidator(double_validator)

        for idx in range(num_view):
            setattr(self, "view%d_folder_line"%idx, QLineEdit())

        ### set init value
        self.num_view_line.setValue(num_view)
        for idx in range(num_view):
            getattr(self, "view%d_folder_line"%idx).setText(folder_paths[idx])
        self.zoom_factor_line.setText(str(zoom_factor))

        ### set layout for visualize
        self.flo = QFormLayout()
        self.flo.addRow("Number of view", self.num_view_line)
        for idx in range(num_view):
            self.flo.addRow("view%d folder"%idx, getattr(self, "view%d_folder_line"%idx))
        self.flo.addRow("zoom factor", self.zoom_factor_line)

        ### add save/cancel button
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        bt_layout = QHBoxLayout()
        bt_layout.addWidget(self.save_button)
        bt_layout.addWidget(self.cancel_button)

        box_layout = QVBoxLayout()
        box_layout.addLayout(self.flo)  # addChildLayout is not working
        box_layout.addLayout(bt_layout)
        self.setLayout(box_layout)

        ### dynamic change the num view
        self.num_view_line.valueChanged.connect(self.adjustLayout)

        self.cancel_button.clicked.connect(self.accept)

    def adjustLayout(self):
        """
            adjust the number of folder path as num_view changes
        """
        num_view = self.num_view_line.value()
        if num_view > self.num_view:
            for idx in range(self.num_view, num_view):
                folder_line = QLineEdit()
                setattr(self, "view%d_folder_line"%idx, folder_line)
                self.flo.insertRow(idx+1, "view%d folder"%idx, folder_line)
        else:
            for idx in range(self.num_view, num_view, -1):
                # self.flo.takeRow(idx)  # this function has bug !
                self.flo.removeRow(idx)
        self.flo.update()
        self.num_view = num_view

    def exportConfig(self):
        config = {"num_view": self.num_view}
        for idx in range(self.num_view):
            config["view%d_folder" % idx] = getattr(self, "view%d_folder_line"%idx).text()
        config["zoom_factor"] = float(self.zoom_factor_line.text())
        return config
