import sys
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ClickableLabel(QLabel):
    def __init__(self, name):
        super().__init__()
        self.setObjectName(name)

    def mousePressEvent(self, event):
        print(f"点击了: {self.objectName()}")
        print(f"相对位置: ({event.position().x()}, {event.position().y()})")


app = QApplication(sys.argv)
window = QWidget()
layout = QHBoxLayout()

pixMapLeft = QPixmap("1.JPG")
pixMapRight = QPixmap("35.JPG")

pixMapLeftShow = pixMapLeft.scaledToHeight(800, Qt.SmoothTransformation)
pixMapLeftShow = pixMapLeft.scaledToWidth(800, Qt.SmoothTransformation)
pixMapRightShow = pixMapRight.scaledToHeight(800, Qt.SmoothTransformation)
pixMapLeftShow = pixMapLeft.scaledToWidth(800, Qt.SmoothTransformation)

# 使用自定义 Label
img1 = ClickableLabel("left_image")
img1.setPixmap(pixMapLeftShow)
layout.addWidget(img1)

img2 = ClickableLabel("right_image")
img2.setPixmap(pixMapRightShow)
layout.addWidget(img2)

window.setLayout(layout)
window.show()
app.exec()