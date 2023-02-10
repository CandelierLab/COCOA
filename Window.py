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

    self.animation = Animation(self, N)
    self.animation.randomize()

    # --- Layouts & Widgets ------------------------------------------------

    # --- Shuffle
         
    lShuffle = QHBoxLayout()

    self.bShuffle = QPushButton()
    self.bShuffle.setFixedHeight(50*f)
    self.bShuffle.setCheckable(True)
    self.bShuffle.setChecked(True)
    self.bShuffle.toggled.connect(self.animation.shuffle)
    
    self.bRandom = QPushButton()
    self.bRandom.setFixedHeight(50*f)
    self.bRandom.clicked.connect(self.animation.randomize)

    lShuffle.addStretch(6)
    lShuffle.addWidget(self.bShuffle, 10)
    lShuffle.addWidget(self.bRandom, 10)
    lShuffle.addStretch(1)

    # --- General parameters

    lParam = QGridLayout()

    # Speed
    self.tSpeed = QLabel()
    self.tSpeed.setFixedHeight(50*f)
    lParam.addWidget(self.tSpeed, 0, 0)

    self.sSpeed = QSlider(Qt.Horizontal)
    self.sSpeed.setMinimum(0)
    self.sSpeed.setMaximum(50*f)
    self.sSpeed.setSingleStep(1)
    self.sSpeed.setValue(50)
    self.sSpeed.valueChanged.connect(self.animation.setSpeed)
    lParam.addWidget(self.sSpeed, 0, 1)

    # Orientational noise
    self.tSigma = QLabel()
    self.tSigma.setFixedHeight(50*f)
    lParam.addWidget(self.tSigma, 1, 0)

    self.sSigma = QSlider(Qt.Horizontal)
    self.sSigma.setMinimum(0)
    self.sSigma.setMaximum(100)
    self.sSigma.setSingleStep(1)
    self.sSigma.setValue(20)
    self.sSigma.valueChanged.connect(self.animation.setSigma)
    lParam.addWidget(self.sSigma, 1, 1)
    
    # --- Agents type

    self.tType = QTabWidget()
    self.tType.setStyleSheet("QTabBar::tab { padding: 15px 25px;}")

    tVicsek = QWidget(self.tType)
    tANN = QWidget()
   
    self.tType.addTab(tVicsek, '')
    self.tType.addTab(tANN, '')

    # self.tType.setCurrentIndex(1)

    # --- Vicsek agents

    lVicsek = QVBoxLayout()
    lVicsek.addSpacing(25*f)

    iVicsek = QLabel()
    iVicsek.setPixmap(QPixmap('Images/Vicsek.png').scaledToHeight(200*f))
    iVicsek.setAlignment(Qt.AlignCenter)
    lVicsek.addWidget(iVicsek)
    lVicsek.addSpacing(25*f)

    self.tVicsek = QLabel()
    lVicsek.addWidget(self.tVicsek)
    lVicsek.addSpacing(25*f)

    lVicsekParam = QGridLayout()
    
    # Radius of interaction
    self.tRadius = QLabel()
    self.tRadius.setFixedHeight(50*f)
    lVicsekParam.addWidget(self.tRadius, 0, 0)

    self.sRadius = QSlider(Qt.Horizontal)
    self.sRadius.setMinimum(0)
    self.sRadius.setMaximum(50*f)
    self.sRadius.setSingleStep(1)
    self.sRadius.setValue(20)
    self.sRadius.valueChanged.connect(self.animation.setRadius)
    lVicsekParam.addWidget(self.sRadius, 0, 1)

    lVicsek.addLayout(lVicsekParam)

    tVicsek.setLayout(lVicsek)

    # --- ANN agents

    lANN = QVBoxLayout()
    lANN.addSpacing(10*f)

    iANN = QLabel()
    iANN.setPixmap(QPixmap('Images/fr.png'))
    lANN.addWidget(iANN)
    lANN.addSpacing(10*f)

    self.tANN = QLabel()
    lANN.addWidget(self.tANN)
    lANN.addSpacing(25*f)

    lANNSettings = QHBoxLayout()

    self.cSym = QCheckBox()
    self.cSym.setChecked(True)
    self.cSym.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px;}")
    lANNSettings.addWidget(self.cSym)

    self.bReset = QPushButton()
    self.bReset.setFixedSize(QSize(250*f, 25*f))
    lANNSettings.addWidget(self.bReset)

    lANN.addLayout(lANNSettings)
    lANN.addSpacing(10*f)

    lANNParam = QGridLayout()
    
    # W1
    tw1 = QLabel("<span style='font-family: Serif'><i>w<sub>1</sub></i></span> =")
    tw1.setFixedHeight(50*f)
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
    tw2.setFixedHeight(50*f)
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
    tw3.setFixedHeight(50*f)
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
    tw4.setFixedHeight(50*f)
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
    lMenu.addSpacing(50*f)
    lMenu.addLayout(lParam)
    lMenu.addSpacing(50*f)
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
    bEn.setGeometry(10*f, 10*f, 70, 47)   
    bEn.clicked.connect(lambda: self.setLanguage('en'))

    bFr = QPushButton('', self)    
    bFr.setStyleSheet("background-image : url('Images/fr.png')")
    bFr.setGeometry(70+20*f, 10*f, 70, 47)
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

        # --- ANN agents

        self.tANN.setText("Les réseaux de neurones ont un champs perceptif radial.")

        self.cSym.setText('Symmetrization')
        self.bReset.setText('Reset weights')