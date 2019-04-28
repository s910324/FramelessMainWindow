import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MyWindow(QWidget) :
    def __init__(self):
        QWidget.__init__(self)
        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tabs.addTab(tab1, "Tab 1")
        tabs.addTab(tab2, "Tab 2")
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.setMouseTracking(True)

    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)
        QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    def mouseMoveEvent(self, event):
        print ('mouseMoveEvent: x=%d, y=%d' % (event.x(), event.y()))


app = QApplication(sys.argv)
window = MyWindow()
window.setFixedSize(640, 480)
window.show()
sys.exit(app.exec_())