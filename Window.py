from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider, QTabWidget, QCheckBox
import qdarkstyle

from Animation import Animation

class Window(QWidget):
  
  def __init__(self, N):
   
    # Qapplication
    self.app = QApplication([])

    # Widget constructor
    super().__init__()

    # --- GUI parameters ---------------------------------------------------

    # Default language
    self.language = 'fr'

    # Style
    self.app.setStyleSheet(qdarkstyle.load_stylesheet())

    # --- Fullscreen
    
    # Check screen size
    screen = self.app.primaryScreen()
    if screen.size().width()>=3840:
      f = 2
      self.setGeometry(0,0,1920*f, 1080*f)      
    else:
      f = 1
      self.setWindowState(Qt.WindowFullScreen)

    # --- Animation --------------------------------------------------------

    self.animation = Animation(N)

    # --- Layouts & Widgets ------------------------------------------------

    # --- Shuffle
         
    lShuffle = QHBoxLayout()

    self.bShuffle = QPushButton()
    self.bShuffle.setFixedHeight(100)

    self.bRandom = QPushButton()
    self.bRandom.setFixedHeight(100)

    lShuffle.addStretch(5)
    lShuffle.addWidget(self.bShuffle, 10)
    lShuffle.addWidget(self.bRandom, 10)
    lShuffle.addStretch(1)

    # --- General parameters

    lParam = QGridLayout()

    # Speed
    self.tSpeed = QLabel()
    self.tSpeed.setFixedHeight(100)
    lParam.addWidget(self.tSpeed, 0, 0)

    self.sSpeed = QSlider(Qt.Horizontal)
    self.sSpeed.setMinimum(0)
    self.sSpeed.setMaximum(100)
    self.sSpeed.setSingleStep(1)
    self.sSpeed.setValue(20)
    lParam.addWidget(self.sSpeed, 0, 1)

    # Orientational noise
    self.tSigma = QLabel()
    self.tSigma.setFixedHeight(100)
    lParam.addWidget(self.tSigma, 1, 0)

    self.sSigma = QSlider(Qt.Horizontal)
    self.sSigma.setMinimum(0)
    self.sSigma.setMaximum(100)
    self.sSigma.setSingleStep(1)
    self.sSigma.setValue(20)
    lParam.addWidget(self.sSigma, 1, 1)
    
    # --- Agents type

    self.tType = QTabWidget()
    self.tType.setStyleSheet("QTabBar::tab { padding: 30px 50px;}")

    tVicsek = QWidget(self.tType)
    tANN = QWidget()
   
    self.tType.addTab(tVicsek, '')
    self.tType.addTab(tANN, '')

    # self.tType.setCurrentIndex(1)

    # --- Vicsek agents

    lVicsek = QVBoxLayout()
    lVicsek.addSpacing(50)

    iVicsek = QLabel()
    iVicsek.setPixmap(QPixmap('Images/Vicsek.png').scaledToHeight(400))
    iVicsek.setAlignment(Qt.AlignCenter)
    lVicsek.addWidget(iVicsek)
    lVicsek.addSpacing(50)

    self.tVicsek = QLabel()
    lVicsek.addWidget(self.tVicsek)
    lVicsek.addSpacing(50)

    lVicsekParam = QGridLayout()
    
    # Radius of interaction
    self.tRadius = QLabel()
    self.tRadius.setFixedHeight(100)
    lVicsekParam.addWidget(self.tRadius, 0, 0)

    self.sRadius = QSlider(Qt.Horizontal)
    self.sRadius.setMinimum(0)
    self.sRadius.setMaximum(100)
    self.sRadius.setSingleStep(1)
    self.sRadius.setValue(20)
    lVicsekParam.addWidget(self.sRadius, 0, 1)

    # Alignment
    self.tAlign = QLabel()
    self.tAlign.setFixedHeight(100)
    lVicsekParam.addWidget(self.tAlign, 1, 0)

    self.sAlign = QSlider(Qt.Horizontal)
    self.sAlign.setMinimum(0)
    self.sAlign.setMaximum(100)
    self.sAlign.setSingleStep(1)
    self.sAlign.setValue(20)
    lVicsekParam.addWidget(self.sAlign, 1, 1)

    lVicsek.addLayout(lVicsekParam)

    tVicsek.setLayout(lVicsek)

    # --- ANN agents

    lANN = QVBoxLayout()
    lANN.addSpacing(20)

    iANN = QLabel()
    iANN.setPixmap(QPixmap('Images/fr.png'))
    lANN.addWidget(iANN)
    lANN.addSpacing(20)

    self.tANN = QLabel()
    lANN.addWidget(self.tANN)
    lANN.addSpacing(50)

    lANNSettings = QHBoxLayout()

    self.cSym = QCheckBox()
    self.cSym.setChecked(True)
    self.cSym.setStyleSheet("QCheckBox::indicator { width: 50px; height: 50px;}")
    lANNSettings.addWidget(self.cSym)

    self.bReset = QPushButton()
    self.bReset.setFixedSize(QSize(500,50))
    lANNSettings.addWidget(self.bReset)

    lANN.addLayout(lANNSettings)
    lANN.addSpacing(20)

    lANNParam = QGridLayout()
    
    # W1
    tw1 = QLabel("<span style='font-family: Serif'><i>w<sub>1</sub></i></span> =")
    tw1.setFixedHeight(100)
    lANNParam.addWidget(tw1, 0, 0)

    self.lw1 = QLabel('0.00')
    lANNParam.addWidget(self.lw1, 0, 1)

    self.sw1 = QSlider(Qt.Horizontal)
    self.sw1.setMinimum(0)
    self.sw1.setMaximum(100)
    self.sw1.setSingleStep(1)
    self.sw1.setValue(50)
    lANNParam.addWidget(self.sw1, 0, 2)

    # W2
    tw2 = QLabel("<span style='font-family: Serif'><i>w<sub>2</sub></i></span> =")
    tw2.setFixedHeight(100)
    lANNParam.addWidget(tw2, 1, 0)

    self.lw2 = QLabel('0.00')
    lANNParam.addWidget(self.lw2, 1, 1)

    self.sw2 = QSlider(Qt.Horizontal)
    self.sw2.setMinimum(0)
    self.sw2.setMaximum(100)
    self.sw2.setSingleStep(1)
    self.sw2.setValue(50)
    lANNParam.addWidget(self.sw2, 1, 2)

    # W3
    tw3 = QLabel("<span style='font-family: Serif'><i>w<sub>3</sub></i></span> =")
    tw3.setFixedHeight(100)
    lANNParam.addWidget(tw3, 2, 0)

    self.lw3 = QLabel('0.00')
    lANNParam.addWidget(self.lw3, 2, 1)

    self.sw3 = QSlider(Qt.Horizontal)
    self.sw3.setMinimum(0)
    self.sw3.setMaximum(100)
    self.sw3.setSingleStep(1)
    self.sw3.setValue(50)
    lANNParam.addWidget(self.sw3, 2, 2)

    # W4
    tw4 = QLabel("<span style='font-family: Serif'><i>w<sub>4</sub></i></span> =")
    tw4.setFixedHeight(100)
    lANNParam.addWidget(tw4, 3, 0)

    self.lw4 = QLabel('0.00')
    lANNParam.addWidget(self.lw4, 3, 1)

    self.sw4 = QSlider(Qt.Horizontal)
    self.sw4.setMinimum(0)
    self.sw4.setMaximum(100)
    self.sw4.setSingleStep(1)
    self.sw4.setValue(50)
    lANNParam.addWidget(self.sw4, 3, 2)

    lANN.addLayout(lANNParam)

    tANN.setLayout(lANN)

    # --- Left Menu

    lMenu = QVBoxLayout()

    lMenu.addLayout(lShuffle)
    lMenu.addSpacing(100)
    lMenu.addLayout(lParam)
    lMenu.addSpacing(100)
    lMenu.addWidget(self.tType)
    lMenu.addStretch(1)
    

    # --- Main layout

    lMain = QHBoxLayout()

    lMain.addLayout(lMenu, 0)
    lMain.addWidget(self.animation.view, 1)

    lMain.setStretch(0, 78)
    lMain.setStretch(1, 100)
    self.setLayout(lMain)

    # --- Language buttons
    
    bEn = QPushButton('', self)
    bEn.setStyleSheet("background-image : url('Images/en.png')")
    bEn.setGeometry(20, 20, 70, 47)   
    bEn.clicked.connect(lambda: self.setLanguage('en'))

    bFr = QPushButton('', self)    
    bFr.setStyleSheet("background-image : url('Images/fr.png')")
    bFr.setGeometry(110, 20, 70, 47)
    bFr.clicked.connect(lambda: self.setLanguage('fr'))

    # --- Settings ---------------------------------------------------------

    # --- Shortcuts

    self.shortcut = {}

    # Quit
    self.shortcut['esc'] = QShortcut(QKeySequence('Esc'), self)
    self.shortcut['esc'].activated.connect(self.app.quit)

    # --- Language

    self.setLanguage()

    # --- Display

    self.show()
    self.animation.startAnimation()
    self.app.exec()

  def setLanguage(self, language=None):

    if language is not None:
      self.language = language

    match self.language:

      case 'fr':

        # Window title
        self.setWindowTitle('Comportement Collectif Artificiel')

        # Randomization
        self.bShuffle.setText('Mélanger')
        self.bRandom.setText('Répartir aléatoirement')

        # Speed
        self.tSpeed.setText('Vitesse')

        # Orientational noise
        self.tSigma.setText("Bruit de réorientation")

        # Agents
        self.tType.setTabText(0, 'Agents de Vicsek')
        self.tType.setTabText(1, 'Réseaux de neurones artificiel')

        # --- Vicsek Agents

        self.tVicsek.setText("Les agents de Viscek s'alignent par rapport à leurs voisins.")

        self.tRadius.setText("Rayon d'interaction")
        self.tAlign.setText("Facteur d'alignement")

        # --- ANN agents

        self.tANN.setText("Les réseaux de neurones ont un champs perceptif radial.")

        self.cSym.setText('Symétrisation')
        self.bReset.setText('Réinitialiser les poids')

      case 'en':
        
        # Window title
        self.setWindowTitle('Artificial Collective Behavior')

        # Randomization
        self.bShuffle.setText('Shuffle')
        self.bRandom.setText('Randomize')

        # Speed
        self.tSpeed.setText('Speed')

        # Orientational noise
        self.tSigma.setText("Reorientation noise")

        # Agents
        self.tType.setTabText(0, 'Vicsek agents')
        self.tType.setTabText(1, 'Artificial neural networks')

        # --- Vicsek Agents

        self.tVicsek.setText("Les agents de Viscek s'alignent par rapport à leurs voisins.")

        self.tRadius.setText('Interaction radius')
        self.tAlign.setText('Alignment factor')

        # --- ANN agents

        self.tANN.setText("Les réseaux de neurones ont un champs perceptif radial.")

        self.cSym.setText('Symmetrization')
        self.bReset.setText('Reset weights')