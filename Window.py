from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QElapsedTimer, QPointF, QRectF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsPathItem
import qdarkstyle

from Animation import Animation

class Window(QWidget):
  
  def __init__(self, N):
   
    # Qapplication
    self.app = QApplication([])

    # Widget constructor
    super().__init__()

    # --- GUI parameters ---------------------------------------------------

    self.language = 'fr'

    # --- Animation --------------------------------------------------------

    self.animation = Animation(N)

    # --- Layout -----------------------------------------------------------

    hLay = QHBoxLayout()

    hLay.addWidget(QPushButton('ok'), 0)
    hLay.addWidget(self.animation.view, 1)

    hLay.setStretch(0, 78)
    hLay.setStretch(1, 100)

    self.setLayout(hLay)

    # --- Settings ---------------------------------------------------------

    self.setLanguage()

    # Background color
    self.app.setStyleSheet(qdarkstyle.load_stylesheet())
    # self.setStyleSheet("background-color: #222;")

    # --- Fullscreen
    
    # Check screen size
    screen = self.app.primaryScreen()
    if screen.size().width()>=3840:
      self.setGeometry(0,0,3840,2160)
    else:
      self.setWindowState(Qt.WindowFullScreen)

    # --- Shortcuts

    self.shortcut = {}

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self)
    self.shortcut['esc'].activated.connect(self.app.quit)

    self.show()
    self.animation.startAnimation()       
    
    self.app.exec()

  def setLanguage(self):

    match self.language:

      case 'fr':

        # Window title
        self.setWindowTitle('Comportement Collectif Artificiel')
        

      case 'en':
        
        # Window title
        self.setWindowTitle('Artificial Collective Behavior')