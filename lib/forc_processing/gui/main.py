import tempfile

import typer

from importlib import resources

from forc_processing.qt.mainwin import Ui_MainWindow

from PyQt6 import QtCore

from PyQt6 import QtGui

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import QUrl

from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QLabel

from PyQt6 import uic

from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

from PIL import Image, ImageQt, ImageEnhance

app = typer.Typer()

class Histogram(QLabel):

    def __init__(self, parent):
        #super().__init__()
        super(Histogram, self).__init__(parent)
        pixmap = QtGui.QPixmap(600, 300)
        self.setPixmap(pixmap)

        self.last_x, self.last_y = None, None
        self.pen_color = QtGui.QColor('#000000')

    def set_pen_color(self, c):
        self.pen_color = QtGui.QColor(c)

    def mouseMoveEvent(self, e):
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.

        painter = QtGui.QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, db_file):

        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)

        self.db_file = db_file

        self.setupUi(self)

        print(self.db_file)

        self.btn_generate.clicked.connect(self.btn_generate_action)

        self.forc_scene = QGraphicsScene(self)
        self.graphics_forcs.setScene(self.forc_scene)
        self.forc_pixmap = self.forc_scene.addPixmap(QPixmap())

        self.set_graphics_size_distribution()

        #self.size_histogram = Histogram(self.frm_size_histogram)
        #self.size_histogram.setParent(self.frm_size_histogram)
        #self.frm_size_histogram.layout().addWidget(self.size_histogram)

    def btn_generate_action(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Generate FORCd

            image = Image.open("/Users/lnagy2/Projects/forc-processing/test_data/00000_20C_1p00pc_045nm.png")
            width, height = image.size
            image = image.crop((1300, 0, width-150, height))

            qimage = ImageQt.ImageQt(image)
            self.forc_pixmap.setPixmap(QtGui.QPixmap.fromImage(qimage))
            self.graphics_forcs.resetTransform()
            self.graphics_forcs.scale(0.2, 0.2)
            print("ho")

    def set_graphics_size_distribution(self):
        shape = int(self.txt_size_distr_shape.text())
        loc = int(self.txt_size_distr_location.text())
        scale = int(self.txt_size_distr_scale.text())

        print(f"{shape} {loc} {scale}")


@app.command()
def begin(forc_file: str):

    import sys

    app = QApplication(sys.argv)
    win = MainWindow(forc_file)
    win.show()
    sys.exit(app.exec())


def main():
    app()


if __name__ == "__main__":
    app()
