from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QElapsedTimer, QPointF, QRectF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsPathItem

class Window(QWidget):
  
  def __init__(self):
   
    # Qapplication
    self.app = QApplication([])

    # Widget constructor
    super().__init__()

    # --- GUI parameters ---------------------------------------------------

    self.language = 'fr'

    # --- Layout -----------------------------------------------------------

    hLay = QHBoxLayout()

    hLay.addWidget(QPushButton('ok'),0)
    hLay.addWidget(QPushButton('2'),1)

    hLay.setStretch(0, 78)
    hLay.setStretch(1, 100)

    self.setLayout(hLay)

    # --- Settings ---------------------------------------------------------

    self.setLanguage()

    # Background color
    # self.setStyleSheet("background-color: black;")

    # --- Fullscreen
    
    # Check screen size
    screen = self.app.primaryScreen()
    if screen.size().width()>=3840:
      self.setGeometry(0,0,3840,2160)
    else:
      self.showMaximized()

    # --- Shortcuts

    self.shortcut = {}

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self)
    self.shortcut['esc'].activated.connect(self.app.quit)

    self.show()    
    self.app.exec()

  def setLanguage(self):

    match self.language:

      case 'fr':

        # Window title
        self.setWindowTitle('Comportement Collectif Artificiel')
        

      case 'en':
        
        # Window title
        self.setWindowTitle('Artificial Collective Behavior')