import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
import pickle
 
class FramelessMainWindow(QWidget):
	def __init__(self, title = "Python", show_title = False):
		QWidget.__init__(self)
		self.init_layout()
		self.init_frameless()
		self.load_stylesheet()

	def init_layout(self):
		self.main_layout    = QVBoxLayout()
		self.main_window    = QMainWindow()
		self.headerbar = FramelessTitleBar()
		self.header_menubar = self.headerbar.menubar

		self.main_layout.setSpacing(0)
		self.main_layout.addWidget(self.headerbar)
		self.main_layout.addWidget(self.main_window)
		self.main_window.setCentralWidget(QMdiArea())
		self.main_window.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		self.setLayout(self.main_layout)

		self.headerbar.minimize_signal.connect(self.showMinimized)
		self.headerbar.maximize_signal.connect(lambda : self.showNormal() if self.isMaximized() else self.showMaximized())
		self.headerbar.close_signal.connect(self.close)
		self.headerbar.move_signal.connect(lambda pos : None if self.isMaximized() else self.move(pos) )
		self.headerbar.aero_resize_signal.connect(self.a)

		self.setWindowTitle("Python")
		self.showTitle(False)
		self.init_menu()

	def init_menu(self):
		exitAction = QAction( '&Exit', self)
		exitAction.triggered.connect(self.close)
				
		m = self.header_menubar.addMenu ("File")
		m.addAction(exitAction)
		self.header_menubar.addMenu ("Edit")
		self.header_menubar.addMenu ("View")
		self.header_menubar.addMenu ("Layer")
		self.header_menubar.addMenu ("Text")
		self.header_menubar.addMenu ("Select")
		self.header_menubar.addMenu ("Window")
		self.header_menubar.addMenu ("Help")

		


	def setWindowTitle(self, title):
		QWidget.setWindowTitle(self,title)
		self.headerbar.setWindowTitle(title)

	def showTitle(self, show):
		self.headerbar.showTitle(show)


	def titleVisible(self):
		return self.headerbar.titleVisible()
	
	def a(self, x, y, w, h):
		screen = QDesktopWidget().screenGeometry() 
		self.move(x, y)
		self.resize(w, h)



	def init_frameless(self):
		self.edge_sense_dist  = 3
		self.resize_activated = False
		self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setMouseTracking(True)


	def showMaximized(self):
		QWidget.show(self)
		QWidget.showMaximized(self)

	def resizeEvent(self, event):
		self.eliminate_border(self.isMaximized())

	def eliminate_border(self, state):

		border_width = (not state) * (self.edge_sense_dist)
		self.main_layout.setContentsMargins(QMargins(border_width, border_width, border_width, border_width))
		self.setCursor(Qt.ArrowCursor)

	def mouseMoveEvent(self, event):
		if not self.isMaximized():
			event_to_left_border   = (event.globalPos()-self.frameGeometry().topLeft()).x()
			event_to_right_border  = (event.globalPos()-self.frameGeometry().bottomRight()).x()
			event_to_top_border    = (event.globalPos()-self.frameGeometry().topLeft()).y()
			event_to_bottom_border = (event.globalPos()-self.frameGeometry().bottomRight()).y()

			at_left_border         = abs(event_to_left_border)    < self.edge_sense_dist
			at_right_border        = abs(event_to_right_border)   < self.edge_sense_dist
			at_top_border          = abs(event_to_top_border)     < self.edge_sense_dist
			at_bottom_border       = abs(event_to_bottom_border)  < self.edge_sense_dist

			sense_array            = [      at_left_border,       at_right_border,       at_top_border,       at_bottom_border]
			dist_array             = [event_to_left_border, event_to_right_border, event_to_top_border, event_to_bottom_border]

			# print (sense_array)
			if not self.resize_activated == True:
				self.previous_sense = sense_array
				self.previous_dist  = dist_array
				if   sense_array in ([1, 0, 1, 0], [0, 1, 0, 1]):
					self.setCursor(Qt.SizeFDiagCursor)
				elif sense_array in ([1, 1, 0, 0], [0, 0, 1, 1]):
					self.setCursor(Qt.SizeBDiagCursor)
				elif sense_array in ([1, 0, 0, 0], [0, 1, 0, 0]):
					self.setCursor(Qt.SizeHorCursor)
				elif sense_array in ([0, 0, 1, 0], [0, 0, 0, 1]):
					self.setCursor(Qt.SizeVerCursor)
				else:
					self.setCursor(Qt.ArrowCursor)

			if self.resize_activated == True:
				n = [dist * sense for sense, dist in zip(self.previous_sense, self.previous_dist)]
				m = [dist * sense for sense, dist in zip(self.previous_sense,         dist_array)]
				delta_left, delta_right, delta_top, delta_bottom = [dist - predist  for dist, predist in zip(m, n)]
				if (self.width() - delta_left >= self.minimumWidth() and self.height()- delta_top >= self.minimumHeight()):
					self.setGeometry(self.x()+delta_left, self.y()+delta_top, self.width()-delta_left+delta_right, self.height()-delta_top+delta_bottom)
					self.update()


	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton and sum(self.previous_sense)>0:
			self.resize_activated = True

			
	def mouseReleaseEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.resize_activated = False

	def paintEvent(self, event):
		self.backgroundColor = QColor(0, 0, 0, 1);#hex2QColor("efefef")
		self.foregroundColor = QColor(0, 0, 0, 1);#hex2QColor("333333")
		self.borderRadius = 5    	
		# get current window size
		s = self.size()
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing, True)
		qp.setPen(self.foregroundColor)
		qp.setBrush(self.backgroundColor)
		qp.drawRoundedRect(0, 0, s.width(), s.height(),
						   self.borderRadius, self.borderRadius)
		qp.end()

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

	def load_stylesheet(self):
		f = QFile("./style.qss")
		if not f.exists():
			return ""
		else:
			f.open(QFile.ReadOnly | QFile.Text)
			ts = QTextStream(f)
			stylesheet = ts.readAll()
			self.setStyleSheet(stylesheet)

class FramelessTitleBar(QWidget):
	test_signal        = pyqtSignal()
	minimize_signal    = pyqtSignal()
	maximize_signal    = pyqtSignal()
	close_signal       = pyqtSignal()
	move_signal        = pyqtSignal(QPoint)
	aero_resize_signal = pyqtSignal(int, int, int, int)
	def __init__(self):
		super().__init__()
		self._title_text          = "Python"
		self._show_title          = False
		self.old_sense_array      = [0,0,0,0]
		self.aero_resize_geometry = []
		self.aero_snap_triggered  = False
		self.aero_snap_window     = Aero_snap_indicator()
		
		self.ori_pos              = None
		self.title_icon           = QLabel()
		self.tab_bar              = Title_tabbar()
		pixmap                    = QPixmap("./src/default_icon.png")
		pixmap                    = pixmap.scaledToHeight(20)
		
		self.title_icon.setPixmap(pixmap)
		self.title_label     = QLabel()
		self.title_label.setObjectName("TitleLabel")
		self.menubar         = Title_menubar()
		self.minimize_button = Title_button(w = 20, h = 20, button_type = "minimize")
		self.maximize_button = Title_button(w = 20, h = 20, button_type = "maximize")
		self.close_button    = Title_button(w = 20, h = 20, button_type = "close")
		
		self.minimize_button.clicked.connect(lambda : self.minimize_signal.emit())
		self.maximize_button.clicked.connect(lambda : self.maximize_signal.emit())
		self.close_button.clicked.connect(   lambda : self.close_signal.emit())

		self.main_Hlayout = HBox(5, self.title_icon, self.title_label ,self.menubar, self.tab_bar, -1, self.minimize_button, self.maximize_button, self.close_button, 5)
		self.main_Hlayout.setSpacing(5)
		self.main_Hlayout.setContentsMargins(QMargins(0,0,0,0))
		self.setLayout(self.main_Hlayout)
		self.setFixedHeight(25)
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setMouseTracking(True)
		self.tab_bar.addTab("Python")
		self.tab_bar.addTab("Python")
		self.tab_bar.addTab("Python")
		self.tab_bar.addTab("Python")
		self.tab_bar.addTab("Python")


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


	def showTitle(self, show):
		self._show_title = show
		self.setWindowTitle(self._title_text)

	def titleVisible(self):
		return self._show_title

	def setWindowTitle(self, title):
		self._title_text = title
		self.title_label.setText( title if self._show_title else "")

	def windowTitle(self):
		return self._title_text


	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.ori_pos = event.pos()

	def mouseReleaseEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.ori_pos = None
			if self.aero_snap_triggered == True:
				self.aero_resize_signal.emit(*self.aero_resize_geometry)

			if self.aero_snap_window.isVisible():
				self.aero_snap_triggered = False
				self.aero_snap_window.hide()


	def mouseMoveEvent(self, event):
		self.setCursor(Qt.ArrowCursor)
		if self.ori_pos:

			self.move_signal.emit(event.globalPos()-self.ori_pos)

			aero_sense    = 15
			screen_res    = QDesktopWidget().availableGeometry(event.globalPos())
			screen_x0     = screen_res.x()
			screen_y0     = screen_res.y()
			screen_width  = screen_res.width()
			screen_height = screen_res.height()
			cursor_x      = event.globalPos().x()
			cursor_y      = event.globalPos().y()
			dist_array    = [(screen_x0 - cursor_x), (screen_x0 + screen_width - cursor_x), (screen_y0 - cursor_y), (screen_y0 + screen_height - cursor_y)] 
			sense_array   = [abs(dist) < aero_sense for dist in dist_array]

			if not(self.old_sense_array == sense_array):
				if sum(sense_array) > 0:

					self.aero_snap_triggered = True
					if   sense_array == [1, 0, 1, 0]:
						self.aero_resize_geometry = [screen_x0 + 1, screen_y0 + 1, screen_width/2, screen_height/2]

					elif sense_array == [0, 1, 1, 0]:
						self.aero_resize_geometry = [screen_x0 + (screen_width/2), screen_y0 + 1, screen_width/2, screen_height/2]

					elif sense_array == [0, 1, 0, 1]:
						self.aero_resize_geometry = [screen_x0 + (screen_width/2), screen_y0 + (screen_height/2), screen_width/2, screen_height/2]

					elif sense_array == [1, 0, 0, 1]:
						self.aero_resize_geometry = [screen_x0, screen_y0 + (screen_height/2), screen_width/2, screen_height/2]

					elif sense_array == [1, 0, 0, 0]:
						self.aero_resize_geometry = [screen_x0 + 1, screen_y0 + 1, screen_width/2, screen_height]

					elif sense_array == [0, 1, 0, 0]:
						self.aero_resize_geometry = [screen_x0 + (screen_width/2), screen_y0 + 1, screen_width/2, screen_height]

					elif sense_array == [0, 0, 1, 0]:
						self.aero_resize_geometry = [screen_x0 + 1, screen_y0 + 1, screen_width, screen_height/2]

					elif sense_array == [0, 0, 0, 1]:
						self.aero_resize_geometry = [screen_x0 + 1, screen_y0 + (screen_height/2), screen_width, screen_height/2]					

					self.aero_snap_window.show_at(*self.aero_resize_geometry)

				else:
					if self.aero_snap_window.isVisible():
						self.aero_snap_triggered = False
						self.aero_snap_window.hide()

				self.old_sense_array = sense_array

		event.accept()

	def mouseDoubleClickEvent (self, event):
		self.maximize_signal.emit()

class Title_menubar(QMenuBar):
	def __init__(self):
		super().__init__()

class Title_tabbar(QTabBar):
	def __init__(self):
		super().__init__()
		self.setTabsClosable(True)
		# self.setContentsMargins(QMargins(0,0,0,0))

class Aero_snap_indicator(QWidget):
	def __init__(self, parent = None):
		super().__init__()
		if not parent:
			indicator   = Aero_snap_indicator(self)
			main_layout = QHBoxLayout()
			main_layout.addWidget(indicator)
			main_layout.setContentsMargins(QMargins(5,5,5,5))
			self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.SubWindow )
			self.setAttribute(Qt.WA_TranslucentBackground, True)
			self.setLayout(main_layout)
		else:
			self.setAttribute(Qt.WA_StyledBackground, True)

	def show_at(self, x, y, w, h):
		mouse_pos      = QCursor.pos()
		self.animation = QPropertyAnimation(self, b"geometry")
		self.animation.setDuration(150)
		self.animation.setStartValue(self.geometry() if self.isVisible() else QRect(mouse_pos.x(), mouse_pos.y(), 0, 0))
		self.animation.setEndValue(QRect(x, y, w, h))
		self.load_stylesheet()
		QMainWindow.show(self)
		self.animation.start()


	def load_stylesheet(self):
		f = QFile("./style.qss")
		if not f.exists():
			return ""
		else:
			f.open(QFile.ReadOnly | QFile.Text)
			ts = QTextStream(f)
			stylesheet = ts.readAll()
			self.setStyleSheet(stylesheet)

class Title_button(QPushButton):
	def __init__(self, w=10, h=10, button_type = None):
		super().__init__()
		self._svg_icon_color = ""
		self._svg_icon       = ""
		self._button_type    = button_type
		self.setProperty('hovered', False)
		self.setProperty('button_type', button_type)
		self.setFixedSize(w,h)
		
	@pyqtProperty(str)
	def svg_icon(self):
		return self._svg_icon
		
	@svg_icon.setter
	def svg_icon(self, value):
		self._svg_icon  = value

	@pyqtProperty(str)
	def svg_icon_color(self):
		return self._svg_icon_color
		
	@svg_icon_color.setter
	def svg_icon_color(self, value):
		self._svg_icon_color  = value

	def update_style(self):
		self.style().unpolish(self)
		self.style().polish(self)
		self.update()
		self.svg = open(self.svg_icon, 'r').read()
		self.render_svg(self.svg.replace("#000000", str(self.property("svg_icon_color")) ))
		
	def enterEvent(self, event):
		self.setProperty('hovered', True)
		self.update_style()

	def leaveEvent(self, event):
		self.setProperty('hovered', False)
		self.update_style()

	def showEvent(self, event):
		self.update_style()

	def render_svg(self, svg_stream):
		renderer = QSvgRenderer(QXmlStreamReader(svg_stream))
		image    = QImage(32, 32, QImage.Format_ARGB32)
		image.fill(0x00000000)
		renderer.render(QPainter(image))
		pixmap   = QPixmap.fromImage(image)
		icon     = QIcon(pixmap)
		self.setIcon(icon)





class BoxLayout(QBoxLayout):
	def __init__(self, direction, ui_list):
		super().__init__(direction)

		if ui_list:
			for item in ui_list:
				if isinstance(item, int):
					if item >= 0:
						self.addSpacing(item)
					else:
						self.addStretch()
				elif issubclass(type(item), QWidget):
					self.addWidget(item)
				elif issubclass(type(item), QLayout):
					self.addLayout(item)
				else:
					raise TypeError("item %s with object type %s is not supported) " % (item, type(item)))


class HBox(BoxLayout):
	def __init__(self, *ui_list):
		super().__init__(QBoxLayout.LeftToRight, ui_list)
		

class VBox(BoxLayout):
	def __init__(self, *ui_list):
		super().__init__(QBoxLayout.TopToBottom, ui_list)		




if __name__ == '__main__':
	app = QApplication(sys.argv)
	frame = FramelessMainWindow()
	frame.show()    
	app.exec_()
	sys.exit