from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, pyqtSlot, QStandardPaths
from PyQt5.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QPaintEvent, QMouseEvent, QFont
from PyQt5.QtWidgets import QApplication, QGridLayout, QSplitter, QWidget, QSlider, \
    QRadioButton, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QDoubleSpinBox, QPushButton, QFileDialog

import imageio, cv2
from PIL import Image
from handyview.utils import draw_line

class EditWidget(QWidget):
    # clicked = Signal()
    clicked = pyqtSignal()
    def __init__(self, parent, img_path) -> None:
        super(EditWidget, self).__init__()
        self.parent = parent
        img = imageio.imread(img_path)
        self.setFixedSize(self.parent.RESOLUTION, self.parent.RESOLUTION)
        self.pixmap = QPixmap(img_path)
        ### set the larger edge length to RESOLUTION
        h, w = img.shape[:2]
        if h > w:
            self.pixmap = self.pixmap.scaledToHeight(self.parent.RESOLUTION)
        else:
            self.pixmap = self.pixmap.scaledToWidth(self.parent.RESOLUTION)
        self.resize_ratio = self.parent.RESOLUTION / max(h, w)
        # self.pixmap.fill(Qt.red)

        self.previous_pos = QPoint()
        self.current_pos = QPoint()
        self.painter = QPainter()
        self.pen = QPen()
        self.pen.setWidth(10)
        self.pen.setCapStyle(Qt.RoundCap)
        self.pen.setJoinStyle(Qt.RoundJoin)

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
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QColor("red"))
        painter.drawPixmap(0, 0, self.pixmap)
        painter.drawRect(QRect(self.previous_pos, self.current_pos))
        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        """Override from QWidget

        Called when user clicks on the mouse

        """
        self.previous_pos = event.pos()
        self.parent.previous_pos = self.previous_pos
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user moves and clicks on the mouse

        """
        self.current_pos = event.pos()
        self.update()

        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user releases the mouse

        """
        # self.previous_pos = self.current_pos
        self.parent.current_pos = self.current_pos
        self.clicked.emit()
        QWidget.mouseReleaseEvent(self, event)

    def updateRect(self):
        # global previous_pos, current_pos
        self.previous_pos, self.current_pos = self.parent.previous_pos, self.parent.current_pos
        self.update()


class ShowWidget(QWidget):

    def __init__(self, parent, img_path) -> None:
        super(ShowWidget, self).__init__()
        self.parent = parent
        self.img_path = img_path
        self.image = imageio.imread(img_path)
        self.ori_image = imageio.imread(img_path)
        h, w = self.image.shape[:2]
        ### set the larger edge length to RESOLUTION
        h, w = self.image.shape[:2]
        self.resize_ratio = self.parent.RESOLUTION / max(h, w)
        self.image = cv2.resize(self.image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))
        self.ori_image = cv2.resize(self.ori_image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))

        self.setFixedSize(self.parent.RESOLUTION, self.parent.RESOLUTION)
        self.ratio = 2
        self.margin = 5  # draw

    def reset(self):
        self.image = self.ori_image.copy()
        self.update()

    def load(self, img_path):
        self.image = imageio.imread(img_path)
        self.ori_image = imageio.imread(img_path)
        h, w = self.image.shape[:2]
        # self.setFixedSize(w, h)
        ### set the larger edge length to RESOLUTION
        h, w = self.image.shape[:2]
        self.resize_ratio = self.parent.RESOLUTION / max(h, w)
        self.image = cv2.resize(self.image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))
        self.ori_image = cv2.resize(self.ori_image, (int(w*self.resize_ratio), int(h*self.resize_ratio)))
        self.update()

    def save(self, img_path):
        h, w = self.image.shape[:2]
        image = cv2.resize(self.image, (int(w/self.resize_ratio), int(h/self.resize_ratio)))
        imageio.imwrite(img_path, image)

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        # logging.debug("update show widget")
        pixmap = Image.fromarray(self.image).toqpixmap()
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user releases the mouse

        """
        self.updateImage(self.ratio)

        QWidget.mouseReleaseEvent(self, event)

    def updateImage(self, ratio):
        self.image = self.ori_image.copy()
        # global previous_pos, current_pos, corner_pos
        if self.parent.previous_pos == self.parent.current_pos:
            print("The same start and end value, pass.")
            return
        pos = self.parent.corner_pos
        x1, y1 = self.parent.previous_pos.x(), self.parent.previous_pos.y()
        x2, y2 = self.parent.current_pos.x(), self.parent.current_pos.y()
        ### highlight original rectangle
        highlight_color = (255,0,0) if self.image.shape[-1] == 3 else (255,0,0,255)
        self.image = cv2.rectangle(self.image, (x1,y1), (x2,y2), highlight_color, self.margin//2)

        h, w = y2-y1, x2-x1

        ### resize and move to left-down corner
        select_im = self.ori_image[y1:y2, x1:x2]
        ratio = ratio/25 + 1
        h_, w_ = int(ratio * h), int(ratio * w)  # size of select image
        select_im = cv2.resize(select_im, (w_, h_))
        select_im = cv2.copyMakeBorder(select_im, self.margin, self.margin, self.margin, self.margin, \
            cv2.BORDER_CONSTANT, value=highlight_color)  # add border for select image
        mode = self.parent.mode
        if pos == "LB":
            self.image[-(h_+self.margin*2):,:w_+self.margin*2] = select_im
            if mode == 0:  # diag
                s0 = (x1, y1)
                s1 = (x2, y2)
                e0 = (0, self.image.shape[0] - select_im.shape[0])
                e1 = (select_im.shape[1], self.image.shape[0])
            elif mode == 1:  # bottom line
                s0 = (x1, y2)
                s1 = (x2, y2)
                e0 = (0, self.image.shape[0] - select_im.shape[0])
                e1 = (select_im.shape[1], self.image.shape[0] - select_im.shape[0])
            else:  # left line
                s0 = (x1, y1)
                s1 = (x1, y2)
                e0 = (select_im.shape[1], self.image.shape[0] - select_im.shape[0])
                e1 = (select_im.shape[1], self.image.shape[0])
        elif pos == "LU":
            self.image[:h_+self.margin*2,:w_+self.margin*2] = select_im
            s0 = (x1, y2)
            s1 = (x2, y1)
            e0 = (0, select_im.shape[0])
            e1 = (select_im.shape[1], 0)
        elif pos == "RU":
            self.image[:h_+self.margin*2,-(w_+self.margin*2):] = select_im
            s0 = (x1, y1)
            s1 = (x2, y2)
            e0 = (self.image.shape[1] - select_im.shape[1], 0)
            e1 = (self.image.shape[1], select_im.shape[0])
        elif pos == "RB":
            self.image[-(h_+self.margin*2):,-(w_+self.margin*2):] = select_im
            if mode == 0:  # diag
                s0 = (x1, y2)
                s1 = (x2, y1)
                e0 = (self.image.shape[1] - select_im.shape[1], self.image.shape[0])
                e1 = (self.image.shape[1], self.image.shape[0] - select_im.shape[0])
            elif mode == 1:  # bottom line
                s0 = (x1, y2)
                s1 = (x2, y2)
                e0 = (self.image.shape[1] - select_im.shape[1], self.image.shape[0] - select_im.shape[0])
                e1 = (self.image.shape[1], self.image.shape[0] - select_im.shape[0])
            else:  # right line
                s0 = (x2, y2)
                s1 = (x2, y1)
                e0 = (self.image.shape[1] - select_im.shape[1], self.image.shape[0])
                e1 = (self.image.shape[1] - select_im.shape[1], self.image.shape[0] - select_im.shape[0])
        else:
            raise NotImplementedError("The position %s is not available" % (pos))

        ### connect original rectangle and select_im

        draw_line(self.image, s0, e0, highlight_color, thickness=self.margin//2, gap=10, style='rectangled')
        draw_line(self.image, s1, e1, highlight_color, thickness=self.margin//2, gap=10, style='rectangled')

        self.update()


class ControlWidget(QWidget):
    def __init__(self, parent) -> None:
        super(ControlWidget, self).__init__()
        self.parent = parent

        # self.sld = QSlider(Qt.Vertical, self)
        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setRange(0, 100)
        # self.label = QLabel('1.00', self)

        io_group = self.create_IObox()
        corner_group = self.create_cornerbox()
        mode_group = self.create_modebox()
        control_group = self.create_coordbox()  # define some control widget
        slider_group = self.create_sliderbox()

        self.sld.valueChanged.connect(self.updateLabel)
        self.push_button_ratio.clicked.connect(self.updateSlider)
        self.push_button_coord.clicked.connect(self.update_rect_coord)
        self.push_button_coord.clicked.connect(self.update_width_height)

        sldLayout = QVBoxLayout()
        sldLayout.addWidget(io_group)
        sldLayout.addWidget(corner_group)
        sldLayout.addWidget(mode_group)
        sldLayout.addWidget(control_group)
        sldLayout.addWidget(slider_group)

        sldLayout.addWidget(self.slider_spin)
        sldLayout.addWidget(self.sld)

        ### set spatial ratio for corner group and control group
        sldLayout.setStretch(0,1)
        sldLayout.setStretch(1,1)
        sldLayout.setStretch(2,2)
        sldLayout.setStretch(3,1)
        sldLayout.setStretch(4,1)
        sldLayout.setStretch(5,1)

        self.setLayout(sldLayout)

    def updateLabel(self, value):

        # self.label.setText("%.2f" % (value/25+1))  # set scale to [1,5]
        self.slider_spin.setValue(value/25+1)  # set scale to [1,5]

    def updateSlider(self):
        self.sld.setValue(int((self.slider_spin.value()-1) * 25))

    def create_IObox(self):
        sub_widget = QWidget()
        self.load_button = QPushButton("load")
        self.save_button = QPushButton("save")
        self.clear_button = QPushButton("clear")
        layout = QHBoxLayout(sub_widget)
        layout.addWidget(self.load_button, 0)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.save_button, 0)
        return sub_widget

    def create_cornerbox(self):
        sub_widget = QWidget()
        self.rblu = QRadioButton("Left Up")
        self.rbru = QRadioButton("Right Up")
        self.rblb = QRadioButton("Left Bottom")
        self.rbrb = QRadioButton("Right Bottom")

        self.rblb.setChecked(True)

        layout = QGridLayout(sub_widget)
        layout.addWidget(self.rblu, 0, 0)
        layout.addWidget(self.rbru, 0, 1)
        layout.addWidget(self.rblb, 1, 0)
        layout.addWidget(self.rbrb, 1, 1)

        return sub_widget

    def create_modebox(self):
        sub_widget = QWidget()
        self.mode1 = QRadioButton("mode1")
        self.mode2 = QRadioButton("mode2")
        self.mode3 = QRadioButton("mode3")

        self.mode1.setChecked(True)

        layout = QHBoxLayout(sub_widget)
        layout.addWidget(self.mode1, 0)
        layout.addWidget(self.mode2, 1)
        layout.addWidget(self.mode3, 2)

        return sub_widget

    def create_coordbox(self):
        sub_widget = QWidget()
        global previous_pos, current_pos
        self.spin_box_LUX = QSpinBox()
        self.spin_box_LUX.setMaximum(2048)
        self.spin_box_LUY = QSpinBox()
        self.spin_box_LUY.setMaximum(2048)

        self.spin_box_RBX = QSpinBox()
        self.spin_box_RBX.setMaximum(2048)
        self.spin_box_RBY = QSpinBox()
        self.spin_box_RBY.setMaximum(2048)

        layout = QGridLayout(sub_widget)
        LU_lable = QLabel('Left Up Coord')
        LU_lable.setFont(QFont('Arial', 10))
        layout.addWidget(LU_lable, 0, 0)
        layout.addWidget(QLabel('x'), 1, 0)
        layout.addWidget(QLabel('y'), 1, 1)
        layout.addWidget(self.spin_box_LUX, 2, 0)
        layout.addWidget(self.spin_box_LUY, 2, 1)

        RB_label = QLabel('Right Bottom Coord')
        RB_label.setFont(QFont('Arial', 10))
        layout.addWidget(RB_label, 3, 0)
        layout.addWidget(QLabel('x'), 4, 0)
        layout.addWidget(QLabel('y'), 4, 1)
        layout.addWidget(self.spin_box_RBX, 5, 0)
        layout.addWidget(self.spin_box_RBY, 5, 1)

        self.width_label = QLabel('width: %d' % 0)
        self.width_label.setFont(QFont('Arial', 10))
        self.height_label = QLabel('height: %d' % 0)
        self.height_label.setFont(QFont('Arial', 10))

        layout.addWidget(self.width_label, 6, 0)
        layout.addWidget(self.height_label, 6, 1)

        return sub_widget

    def create_sliderbox(self):
        sub_widget = QWidget()
        layout = QGridLayout(sub_widget)

        ### for slider
        self.slider_spin = QDoubleSpinBox()
        self.push_button_ratio = QPushButton("Set ratio")
        self.push_button_coord = QPushButton("Set coordinate")

        # layout.addWidget(QLabel('Set current status'), 4, 0)
        layout.addWidget(self.push_button_coord, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.push_button_ratio, 0, 1, Qt.AlignRight)
        layout.addWidget(self.slider_spin, 1, 0, Qt.AlignLeft)
        return sub_widget


    def update_width_height(self):
        self.width_label.setText('width: %d' % (self.spin_box_RBX.value() - self.spin_box_LUX.value()))
        self.height_label.setText('height: %d' % (self.spin_box_RBY.value() - self.spin_box_LUY.value()))

    @pyqtSlot()
    def load_rect_coord(self):
        # global previous_pos, current_pos
        self.spin_box_LUX.setValue(self.parent.previous_pos.x())
        self.spin_box_LUY.setValue(self.parent.previous_pos.y())
        self.spin_box_RBX.setValue(self.parent.current_pos.x())
        self.spin_box_RBY.setValue(self.parent.current_pos.y())

    @pyqtSlot()
    def update_rect_coord(self):
        # global previous_pos, current_pos
        self.parent.previous_pos.setX(self.spin_box_LUX.value())
        self.parent.previous_pos.setY(self.spin_box_LUY.value())
        self.parent.current_pos.setX(self.spin_box_RBX.value())
        self.parent.current_pos.setY(self.spin_box_RBY.value())


class MagCanvas(QWidget):
    def __init__(self, parent, db) -> None:
        super(MagCanvas, self).__init__()
        self.parent = parent
        self.db = db  # database
        img_path = self.db.get_path()[0]

        ### init value
        self.previous_pos = QPoint()
        self.current_pos = QPoint()
        self.corner_pos = "LB"
        self.mode = 0
        self.RESOLUTION = 720

        self.edit_widget = EditWidget(self, img_path)
        self.show_widget = ShowWidget(self, img_path)
        con_widget = ControlWidget(self)
        self.con_widget = con_widget

        ### connect edit rect to show widget
        self.edit_widget.clicked.connect(lambda: self.show_widget.updateImage(con_widget.sld.value()))
        ### connect slider valut to image resize ratio
        self.con_widget.sld.valueChanged.connect(self.show_widget.updateImage)
        ### connect rect coordinate to control widget
        self.edit_widget.clicked.connect(con_widget.load_rect_coord)
        self.edit_widget.clicked.connect(con_widget.update_width_height)
        ### connect control widget to rect coordinate
        con_widget.push_button_coord.clicked.connect(self.edit_widget.updateRect)
        con_widget.push_button_coord.clicked.connect(lambda: self.show_widget.updateImage(con_widget.sld.value()))

        ### connect radio button to corner position
        con_widget.rblb.toggled.connect(self.update_corner_pos)
        con_widget.rblu.toggled.connect(self.update_corner_pos)
        con_widget.rbrb.toggled.connect(self.update_corner_pos)
        con_widget.rbru.toggled.connect(self.update_corner_pos)

        ### connect mode button to dashline mode
        con_widget.mode1.toggled.connect(self.update_mode)
        con_widget.mode2.toggled.connect(self.update_mode)
        con_widget.mode3.toggled.connect(self.update_mode)

        layout = QHBoxLayout()
        layout.addWidget(self.edit_widget)
        layout.addWidget(self.show_widget)
        layout.addWidget(con_widget)
        self.setLayout(layout)

        ### file filter
        self.mime_type_filters = ["image/jpeg", "image/png"]

        ### connect signal to slot
        con_widget.load_button.clicked.connect(self.on_open)
        con_widget.save_button.clicked.connect(self.on_save)
        con_widget.clear_button.clicked.connect(self.show_widget.reset)

    def update_corner_pos(self, value):
        # global corner_pos
        rbtn = self.sender()
        if rbtn.isChecked() == True:
            self.corner_pos = "".join([x[0] for x in rbtn.text().split(" ")])
        self.show_widget.updateImage(self.con_widget.sld.value())

    def update_mode(self):
        # global mode
        rbtn = self.sender()
        if rbtn.isChecked() == True:
            self.mode = int(rbtn.text()[-1]) - 1
        self.show_widget.updateImage(self.con_widget.sld.value())

    def load(self, img_path):
        self.edit_widget.load(img_path)
        self.show_widget.load(img_path)

    def save(self, img_path):
        self.show_widget.save(img_path)

    @pyqtSlot()
    def on_open(self):
        dialog = QFileDialog(self, "Open File")
        # dialog.setMimeTypeFilters(self.mime_type_filters)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        )

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                print(dialog.selectedFiles()[0])
                self.edit_widget.load(dialog.selectedFiles()[0])
                self.show_widget.load(dialog.selectedFiles()[0])

    @pyqtSlot()
    def on_save(self):
        dialog = QFileDialog(self, "Save File")
        # dialog.setMimeTypeFilters(self.mime_type_filters)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        )

        if dialog.exec() == QFileDialog.Accepted:
            if dialog.selectedFiles():
                self.show_widget.save(dialog.selectedFiles()[0])




