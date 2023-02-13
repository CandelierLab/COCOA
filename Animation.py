import numpy as np
import colorsys

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QElapsedTimer, QPointF, QRectF
from PyQt5.QtGui import QKeySequence, QPalette, QColor, QPainter, QPen, QBrush, QPolygonF, QFont, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QGridLayout, QPushButton, QGraphicsScene, QGraphicsView, QAbstractGraphicsShapeItem, QGraphicsItem, QGraphicsItemGroup, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsPathItem

from Engine import Engine

# === ITEMS ================================================================

# --- Generic Item ---------------------------------------------------------

class item():
  
  def __init__(self, animation, name, **kwargs):
   
    # Call the other item's constructor, if any
    super().__init__()

    # --- Definitions

    # Reference animation
    self.animation = animation

    # Assign name
    self.name = name

    self._parent = None
    self._behindParent = None
    self._position = [0,0]
    self._shift = [0,0]
    self._orientation = None
    self._zvalue = None
    self._draggable = None
      
    # --- Initialization

    if 'parent' in kwargs: self.parent = kwargs['parent']
    if 'behindParent' in kwargs: self.behindParent = kwargs['behindParent']
    if 'position' in kwargs: self.position = kwargs['position']
    if 'orientation' in kwargs: self.orientation = kwargs['orientation']
    if 'zvalue' in kwargs: self.zvalue = kwargs['zvalue']
    if 'draggable' in kwargs: self.draggable = kwargs['draggable']

  def x2scene(self, x):
    """
    Convert the :math:`x` position in scene coordinates

    arg:
      x (float): The :math:`x` position.

    returns:
      The :math:`x` position in scene coordinates.
    """
    if self.parent is None:
      return (x-self.animation.boundaries['x'][0])*self.animation.factor
    else:
      return x*self.animation.factor

  def y2scene(self, y):
    """
    Convert the :math:`y` position in scene coordinates

    arg:
      y (float): The :math:`y` position.

    returns:
      The :math:`y` position in scene coordinates.
    """
    
    if self.parent is None:
      return (self.animation.boundaries['y'][0]-y)*self.animation.factor
    else:
      return -y*self.animation.factor

  def xy2scene(self, xy):
    """
    Convert the :math:`x` and :math:`y` positions in scene coordinates

    arg:
      xy ([float,float]): The :math:`x` and :math:`y` positions.

    returns:
      The :math:`x` and :math:`y` position in scene coordinates.
    """

    return self.x2scene(xy[0]), self.y2scene(xy[1])

  def d2scene(self, d):
    """
    Convert a distance in scene coordinates

    arg:
      d (float): Distance to convert.

    returns:
      The distance in scene coordinates.
    """

    return d*self.animation.factor

  def a2scene(self, a):
    """
    Convert an angle in scene coordinates (radian to degrees)

    arg:
      a (float): Angle to convert.

    returns:
      The angle in degrees.
    """

    return -a*180/np.pi
  
  def scene2x(self, u):
    """
    Convert horizontal scene coordinates into :math:`x` position

    arg:
      u (float): The horizontal coordinate.

    returns:
      The :math:`x` position.
    """

    if self._parent is None:
      return self.animation.boundaries['x'][0] + u/self.animation.factor
    else:
      return u/self.animation.factor

  def scene2y(self, v):
    """
    Convert vertical scene coordinates into :math:`y` position

    arg:
      v (float): The horizontal coordinate.

    returns:
      The :math:`y` position.
    """

    if self._parent is None:
      return self.animation.boundaries['y'][0] - v/self.animation.factor
    else:
      return - v/self.animation.factor

  def scene2xy(self, pos):
    """
    Convert scene coordinates into :math:`x` and :math:`y` positions

    arg:
      pos ([float,float]): The position in scene coordinates.

    returns:
      The :math:`x` and :math:`y` positions.
    """

    if isinstance(pos, QPointF):
      u = pos.x()
      v = pos.y()
    else:
      u = pos[0]
      v = pos[1]

    return self.scene2x(u), self.scene2y(v)

  def place(self):
    """
    Absolute positionning

    Places the item at an absolute position.
    
    Attributes:
      x (float): :math:`x`-coordinate of the new position. It can also be a 
        doublet [``x``,``y``], in this case the *y* argument is 
        overridden.
      y (float): :math:`y`-coordinate of the new position.
      z (float): A complex number :math:`z = x+jy`. Specifying ``z``
        overrides the ``x`` and ``y`` arguments.
    """

    # Set position
    self.setPos(self.x2scene(self._position[0])-self._shift[0], 
      self.y2scene(self._position[1])-self._shift[1])

  def move(self, dx=None, dy=None, z=None):
    """
    Relative displacement

    Displaces the item of relative amounts.
    
    Attributes:
      dx (float): :math:`x`-coordinate of the displacement. It can also be a 
        doublet [`dx`,`dy`], in this case the *dy* argument is overridden.
      dy (float): :math:`y`-coordinate of the displacement.
      z (float): A complex number :math:`z = dx+jdy`. Specifying ``z``
        overrides the ``x`` and ``y`` arguments.
    """

    # Doublet input
    if isinstance(dx, (tuple, list)):
      dy = dx[1]
      dx = dx[0]  

    # Convert from complex coordinates
    if z is not None:
      dx = np.real(z)
      dy = np.imag(z)

    # Store position
    if dx is not None: self._position[0] += dx
    if dy is not None: self._position[1] += dy

    self.place()

  def rotate(self, angle):
    """
    Relative rotation

    Rotates the item relatively to its current orientation.
    
    Attributes:
      angle (float): Orientational increment (rad)
    """

    self._orientation += angle
    self.setRotation(self.a2scene(self.orientation))

  def setStyle(self):
    """
    Item styling

    This function does not take any argument, instead it applies the changes
    defined by each item's styling attributes (*e.g.* color, stroke thickness).
    """

    # --- Fill

    if isinstance(self, QAbstractGraphicsShapeItem):

      if self._color['fill'] is not None:
        self.setBrush(QBrush(QColor(self._color['fill'])))

    # --- Stroke

    if isinstance(self, (QAbstractGraphicsShapeItem,QGraphicsLineItem)):

      Pen = QPen()

      #  Color
      if self._color['stroke'] is not None:
        Pen.setColor(QColor(self._color['stroke']))

      # Thickness
      if self._thickness is not None:
        Pen.setWidth(self._thickness)

      # Style
      match self._linestyle:
        case 'dash' | '--': Pen.setDashPattern([3,6])
        case 'dot' | ':' | '..': Pen.setStyle(Qt.DotLine)
        case 'dashdot' | '-.': Pen.setDashPattern([3,3,1,3])
      
      self.setPen(Pen)

  def mousePressEvent(self, event):
    """
    Simple click event

    For internal use only.

    args:
      event (QGraphicsSceneMouseEvent): The click event.
    """

    match event.button():
      case 1: type = 'leftclick'
      case 2: type = 'rightclick'
      case 4: type = 'middleclick'
      case 8: type = 'sideclick'

    self.animation.change(type, self)
    super().mousePressEvent(event)

  def mouseDoubleClickEvent(self, event):
    """
    Double click event

    For internal use only.

    args:
      event (QGraphicsSceneMouseEvent): The double click event.
    """

    self.animation.change('doubleclick', self)
    super().mousePressEvent(event)

  def itemChange(self, change, value):
    """
    Item change notification

    This method is triggered upon item change. The item's transformation
    matrix has changed either because setTransform is called, or one of the
    transformation properties is changed. This notification is sent if the 
    ``ItemSendsGeometryChanges`` flag is enabled (e.g. when an item is 
    :py:attr:`item.movable`), and after the item's local transformation 
    matrix has changed.

    args:

      change (QGraphicsItem constant): 

    """
    # -- Define type

    type = None

    match change:
      case QGraphicsItem.ItemPositionHasChanged:
        type = 'move'

    # Report to animation
    if type is not None:
      self.animation.change(type, self)

    # Propagate change
    return super().itemChange(change, value)

  # --- Parent -------------------------------------------------------------

  @property
  def parent(self): return self._parent

  @parent.setter
  def parent(self, pName):
    self._parent = pName
    self.setParentItem(self.animation.item[self._parent])

  # --- belowParent --------------------------------------------------------

  @property
  def behindParent(self): return self._behindParent

  @behindParent.setter
  def behindParent(self, b):
    self._behindParent = b
    self.setFlag(QGraphicsItem.ItemStacksBehindParent, b)

  # --- Position -------------------------------------------------------------

  @property
  def position(self): return self._position

  @position.setter
  def position(self, pos):
    
    if isinstance(pos, complex):

      # Convert from complex coordinates
      x = np.real(pos)
      y = np.imag(pos)

    else:

      # Doublet input
      x = pos[0]  
      y = pos[1]      

    # Store position
    self._position = [x,y]

    # Set position
    self.place()    

  # --- Orientation --------------------------------------------------------

  @property
  def orientation(self): return self._orientation

  @orientation.setter
  def orientation(self, angle):
    
    self._orientation = angle
    self.setRotation(self.a2scene(angle))

  # --- Z-value ------------------------------------------------------------

  @property
  def zvalue(self): return self._zvalue

  @zvalue.setter
  def zvalue(self, z):
    self._zvalue = z
    self.setZValue(self._zvalue)

  # --- Draggability -------------------------------------------------------

  @property
  def draggable(self): return self._draggable

  @draggable.setter
  def draggable(self, z):
    
    self._draggable = z
    
    self.setFlag(QGraphicsItem.ItemIsMovable, self._draggable)
    self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, self._draggable)
    if self._draggable:
      self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
    
class polygon(item, QGraphicsPolygonItem):
  
  def __init__(self, animation, name, **kwargs):
   
    # Generic item constructor
    super().__init__(animation, name, **kwargs)
    
    # --- Definitions

    self._points = None
    self._color = (None, None)
    self._thickness = None
    self._linestyle = None

    # --- Initialization

    if 'points' not in kwargs:
      raise AttributeError("'points' must be specified for polygon items.")
    else:
      self.points = kwargs['points']

    self.colors = kwargs['colors'] if 'colors' in kwargs else ['gray','white']
    self.linestyle = kwargs['linestyle'] if 'linestyle' in kwargs else None
    self.thickness = kwargs['thickness'] if 'thickness' in kwargs else 0   

  # --- Points -------------------------------------------------------------

  @property
  def points(self): return self._points

  @points.setter
  def points(self, points):

    self._points = points

    poly = []
    for p in self._points:
      poly.append(QPointF(self.x2scene(p[0]), self.y2scene(p[1])))
    self.setPolygon(QPolygonF(poly))
  
  # --- Color --------------------------------------------------------------

  @property
  def colors(self): return self._color

  @colors.setter
  def colors(self, C):
    self._color = {'fill': C[0], 'stroke': C[1]}
    self.setStyle()

  # --- Thickness ----------------------------------------------------------

  @property
  def thickness(self): return self._thickness

  @thickness.setter
  def thickness(self, t):
    self._thickness = t
    self.setStyle()

  # --- Linestyle ----------------------------------------------------------

  @property
  def linestyle(self): return self._linestyle

  @linestyle.setter
  def linestyle(self, s):
    self._linestyle = s
    self.setStyle()      

# === ANIMATION ============================================================

class view(QGraphicsView):
  
  def __init__(self, scene, *args, **kwargs):

    super().__init__(*args, *kwargs)
    self.setScene(scene)

  def showEvent(self, E):
    
    self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
    super().showEvent(E)

  def resizeEvent(self, E):
    
    self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
    super().resizeEvent(E)

class Animation2d():
  
  def __init__(self, parent=None, size=None, boundaries=None, disp_boundaries=True, disp_time=False, dt=None):
  
    # --- Parent

    self.parent = None

    # --- Scene & view

    # Scene
    self.scene = QGraphicsScene()
    self.view = view(self.scene)
    self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # Items and composite elements
    self.item = {}

    # --- Layout

    # self.layout.addWidget(self.view, 0,0)

    # --- Time

    self.t = 0
    self.dt = dt
    self.disp_time = disp_time
    self.disp_boundaries = disp_boundaries

    # Framerate
    self.fps = 25

    # -- Size settings

    self.size = size if size is not None else QApplication.desktop().screenGeometry().height()*0.6
    self.margin = 0
    self.timeHeight = QApplication.desktop().screenGeometry().height()*0.02

    # Scene limits
    
    self.boundaries = {'x':[0,1], 'y':[0,1], 'width':None, 'height':None}
    if boundaries is not None:
      self.boundaries['x'] = list(boundaries[0])
      self.boundaries['y'] = list(boundaries[1])
    self.boundaries['width'] = self.boundaries['x'][1]-self.boundaries['x'][0]
    self.boundaries['height'] = self.boundaries['y'][1]-self.boundaries['y'][0]

    # Scale factor
    self.factor = self.size/self.boundaries['height']

    self.scene.setSceneRect(0, 0, self.factor, -self.factor)

    # --- Display

    # Dark background
    self.view.setBackgroundBrush(Qt.black)
    pal = self.view.palette()
    pal.setColor(QPalette.Window, Qt.black)
    self.view.setPalette(pal)

    # Antialiasing
    self.view.setRenderHints(QPainter.Antialiasing)

    # --- Animation
  
    self.qtimer = QTimer(self.view)
    self.qtimer.timeout.connect(self.update)
    self.timer = QElapsedTimer()
    
    # Scene boundaries
    if self.disp_boundaries:
      self.box = QGraphicsRectItem(0,0,
        self.factor*self.boundaries['width'],
        -self.factor*self.boundaries['height'])
      # self.box.setPen(QPen(Qt.lightGray, 0)) 
      self.scene.addItem((self.box))

    # Time display
    if self.disp_time:
      self.timeDisp = self.scene.addText("---")
      self.timeDisp.setDefaultTextColor(QColor('white'))
      self.timeDisp.setPos(0, -self.timeHeight-self.factor*self.boundaries['height'])

  def add(self, type, name, **kwargs):
    """
    Add an item to the scene.

    args:
      item (:class:`item` *subclass*): The item to add.
    """

    # Create item
    self.item[name] = type(self, name, **kwargs)

    # Add item to the scene
    if self.item[name].parent is None:
      self.scene.addItem(self.item[name])
    
  def startAnimation(self):
    
    self.qtimer.setSingleShot(False)
    self.qtimer.setInterval(int(1000/self.fps))
    self.qtimer.start()
    self.timer.start()
      
  def update(self):
    
    # Update time
    if self.dt is None:
      self.t = self.timer.elapsed()/1000 
    else: 
      self.t += self.dt

    # Timer display
    if self.disp_time:
      self.timeDisp.setPlainText('{:06.02f} sec'.format(self.t))

# --- Animation ------------------------------------------------------------

class Animation(Animation2d):

  def __init__(self, window, N):

    # Superclass constructor
    super().__init__()

    # Associated window
    self.window = window

    # Associated enine
    self.engine = Engine()

    # --- Items ------------------------------------------------------------

    self.N = N

    # --- Engine

    self.engine.agents.add(N, 'Blind')

    # --- Animation

    s = 0.01

    for i in range(N):

      self.add(polygon, i, 
        position = [self.engine.agents.list[i].x, self.engine.agents.list[i].y],
        orientation = self.engine.agents.list[i].a,
        points = [[s,0],[-s/2,s/2],[-s/2,-s/2]],
        colors = ['red', 'red']
      )

  def update(self):

    # Superclass method
    super().update()

    self.engine.step()

    for i in range(self.N):

      # Position
      x = self.engine.agents.list[i].x
      y = self.engine.agents.list[i].y
      self.item[i].position = [x, y]

      # Orientation
      self.item[i].orientation = self.engine.agents.list[i].a
 
  def changeAgent(self):

    match self.window.tType.currentIndex():

      case 0: self.engine.mode = 'Blind'
      case 1: self.engine.mode = 'Vicsek'
      case 2: self.engine.mode = 'Perceptron'

  def shuffle(self):

    for i in range(self.N):

      # Position
      self.engine.agents.list[i].x = np.random.rand()
      self.engine.agents.list[i].y = np.random.rand()

      # Orientation
      self.engine.agents.list[i].a = np.random.rand()*2*np.pi

      # Colors
      c = colorsys.hsv_to_rgb(self.engine.agents.list[i].x, 1, 1)
      self.item[i].colors = [QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255)), QColor(int(c[0]*255), int(c[1]*255), int(c[2]*255))]


  def setSpeed(self):

    for i in range(self.N):
      self.engine.agents.list[i].v = self.window.sSpeed.value()*0.0002

  def setSigma(self):

    for i in range(self.N):
      self.engine.agents.list[i].sigma = self.window.sSigma.value()*0.005

  def setRadius(self):

    for i in range(self.N):
      self.engine.agents.list[i].r = self.window.sRadius.value()*0.002

  def symmetrize(self):

    if self.window.cSym.isChecked():
      
      # Symmetrize values
      self.window.sw4.setValue(100-self.window.sw1.value())
      self.window.sw3.setValue(100-self.window.sw2.value())

      # Disable weigth
      self.window.lw3.setDisabled(True)
      self.window.sw3.setDisabled(True)
      self.window.lw4.setDisabled(True)
      self.window.sw4.setDisabled(True)

    else :

      # Enable slide bars
      self.window.sw3.setDisabled(False)
      self.window.lw3.setDisabled(False)
      self.window.sw4.setDisabled(False)
      self.window.lw4.setDisabled(False)


  def resetWeights(self):

    # Sliders
    self.window.sw1.setValue(50)
    self.window.sw2.setValue(50)
    self.window.sw3.setValue(50)
    self.window.sw4.setValue(50)

    # Text
    self.window.lw1.setText('0.00')
    self.window.lw2.setText('0.00')
    self.window.lw3.setText('0.00')
    self.window.lw4.setText('0.00')

    for i in range(self.N):
      self.engine.agents.list[i].w1 = 0
      self.engine.agents.list[i].w2 = 0
      self.engine.agents.list[i].w3 = 0
      self.engine.agents.list[i].w4 = 0

  def setW1(self):

    w1 = (self.window.sw1.value()-50)*0.0001
    self.window.lw1.setText('{:.02f}'.format(w1*200))

    for i in range(self.N):
      self.engine.agents.list[i].w1 = w1

    # Symmetrize values
    if self.window.cSym.isChecked():
      self.window.sw4.setValue(100-self.window.sw1.value())

  def setW2(self):

    w2 = (self.window.sw2.value()-50)*0.0001
    self.window.lw2.setText('{:.02f}'.format(w2*200))

    for i in range(self.N):
      self.engine.agents.list[i].w2 = w2

    # Symmetrize values
    if self.window.cSym.isChecked():
      self.window.sw3.setValue(100-self.window.sw2.value())

  def setW3(self):

    w3 = (self.window.sw3.value()-50)*0.0001
    self.window.lw3.setText('{:.02f}'.format(w3*200))

    for i in range(self.N):
      self.engine.agents.list[i].w3 = w3

  def setW4(self):

    w4 = (self.window.sw4.value()-50)*0.0001
    self.window.lw4.setText('{:.02f}'.format(w4*200))

    for i in range(self.N):
      self.engine.agents.list[i].w4 = w4