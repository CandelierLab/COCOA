import random
from math import *
import numpy as np
import time

# === Geometry =============================================================

class foop:
  '''
  Field of orientated points
  '''
  def __init__(self, X, Y, A):
    self.X = X
    self.Y = Y
    self.A = A

  def center(self, tx, ty, ta=0):
    '''
    (tx,ty) is the target position, which will be at (0,0) after translation
    ta is the target angle, which will be at 0 after rotation
    '''

    # Translation (with boundary conditions)
    X = (self.X - tx + 1/2) % 1 - 1/2
    Y = (self.Y - ty + 1/2) % 1 - 1/2

    # Rotation
    if ta!=0:
      Z = X+Y*1j
      Z = np.abs(Z)*np.exp(1j*(np.angle(Z)-ta))
      X = np.real(Z)
      Y = np.imag(Z)

    return foop(X, Y, self.A-ta)

  def near(self, r, include_self=False, blindlist=None):
    '''
    List of points within a given radius around the origin
    '''
    
    # Find nearest
    if include_self:
      I = np.argwhere(np.abs(self.X + 1j*self.Y)<=r).flatten()
    else:
      I = np.argwhere((np.abs(self.X + 1j*self.Y)>0) & (np.abs(self.X + 1j*self.Y)<=r)).flatten()

    # Remove blindlist
    if blindlist is not None:
      I = np.setdiff1d(I, blindlist)

    return I

  def save(self, file, step):
    '''
    Save data points
    '''

    file.pos[step,:,0] = self.X
    file.pos[step,:,1] = self.Y
    file.pos[step,:,2] = self.A

# === Generic mobile agents ================================================

class agent:
  '''
  Generic mobile agent (parent class)  
  '''

  def __init__(self, engine, v=0.006, sigma=0.1, r=0.05, damax=None, initial_position=None):

    # Definitions

    self.engine = engine
    self.v = v
    self.sigma = sigma
    self.damax = damax if damax is not None else np.pi/2

    # Viscek
    self.r = r

    # Percepton
    self.ns = 4
    self.w1 = 0
    self.w2 = 0
    self.w3 = 0
    self.w4 = 0

    # Initial position
    if initial_position is None:
      self.x = random.random()
      self.y = random.random()
      self.a = random.random()*2*np.pi
    else:
      self.x = initial_position[0]
      self.y = initial_position[1]
      self.a = initial_position[2]

    # Polar coordinates
    self.rho = None
    self.theta = None

    # Density
    self.density = {'pos':[], 'ang':[]}
    self.kde_sigma = {'pos':None, 'ang':None}

    # Blind list
    self.blindlist = None

  def __str__(self):

    if self.__class__.__name__ == 'agent':
      s = '--- agent ---'
    else:
      s = '--- ' + str(self.__class__.__name__) + ' agent ---'

    for key,val in self.__dict__.items():
      s+= '\n' + key + ': ' + str(val)

    return s

  def perceive(self, i, F, r=0.5, reorient=True, include_self=False):
    '''
    Updating perception of the surroundings

    - Sets density field in polar coordinates around the agent
    - Computes the local density, used for the fitness
    '''

    # Center around agent
    if reorient:
      C = F.center(self.x, self.y, self.a)
    else:
      C = F.center(self.x, self.y)

    # Polar coordinates
    Z = C.X + C.Y*1j

    # --- Density

    # Find nearest neighbors
    I = C.near(0.5, blindlist=self.blindlist, include_self=include_self)

    # --- Polar coordinates

    # Find nearest neighbors
    if r!=0.5:
      I = C.near(r, blindlist=self.blindlist, include_self=include_self)

    self.rho = np.abs(Z[I])
    self.theta = np.mod(np.angle(Z[I]), 2*np.pi)

    return I

  def move(self):
    '''
    Move the agent (with bounday conditions)
    '''

    # Angular noise
    self.a += self.sigma*np.random.randn(1)

    # Position
    self.x = ((self.x + self.v*np.cos(self.a)) % 1)[0]
    self.y = ((self.y + self.v*np.sin(self.a)) % 1)[0]

  def update(self, i, F):
    
    match self.engine.mode:

      case 'Blind':

        # Update perception
        I = self.perceive(i, F, reorient=False)

        # Add angular noise and move
        self.move()

      case 'Vicsek':

        # Update perception
        I = self.perceive(i, F, r=self.r, reorient=False, include_self=True)
        
        # Update angle
        self.a = np.angle(np.exp(1j*F.A[I]).sum())

        # Add angular noise and move
        self.move()

      case 'Perceptron':

         # Update perception
        self.perceive(i, F)

        # Values
        v = []
        for k in range(self.ns):

          # Indices
          I = np.where((self.theta>=2*k*np.pi/self.ns) & (self.theta<=2*(k+1)*np.pi/self.ns))

          if len(self.rho[I]):
            v.append(np.sum((self.rho[I])**-1))
          else:
            v.append(0)

        # Update angle
        self.a += np.tanh(self.w1*v[0] + self.w2*v[1] + self.w3*v[2] + self.w4*v[3])*self.damax

        # Add angular noise and move    
        self.move()

# === List of agents =======================================================

class Agents:
  '''
  Collection of agents
  '''

  def __init__(self, engine):
    self.N = 0
    self.list = []
        
    # Engine
    self.engine = engine

  def __str__(self):
    s = '--- Agents ---\n'
    s += 'N: ' + str(self.N)
    return s

  def add(self, n, type):
    '''
    Add one or many agents
    '''
        
    # Add agents
    for i in range(n):
      self.list.append(agent(self.engine))

    # Update agent count
    self.N = n
    
  def compile(self):
    '''
    Compile all positions and orientations
    '''

    return foop(
      np.array([A.x for A in self.list],dtype=object).flatten().astype(float),
      np.array([A.y for A in self.list],dtype=object).flatten().astype(float),
      np.array([A.a for A in self.list],dtype=object).flatten().astype(float))

# === Engine ===============================================================

class Engine:
  '''
  Engine 
  '''

  # Contructor
  def __init__(self, steps=None, data_in=None, data_out=None):

    # Mode
    self.mode = 'Blind'

    # Agents
    self.agents = Agents(self)

    # --- Iterations

    self.iteration = 0

    # Number of steps
    self.steps = steps

    self.verbose = None
    self.tref = None

    # --- I/O files

    # Input file
    self.data_in = data_in

    # Output file
    self.data_out = data_out

    # --- Density estimation

    # Density estimation lengths
    self.kde_sigma = {'pos': 0.1, 'ang':np.pi/10}

  def step(self):
    '''
    One step of the simulation
    '''

    if self.verbose is not None and (self.iteration % self.verbose)==0:
      print('→ Iteration {:d} ({:.2f} s) ...'.format(self.iteration, time.time()-self.tref))

    # Prepare data
    F = self.agents.compile()

    # --- Update

    for i, agent in enumerate(self.agents.list):
      agent.update(self.iteration, F)

    # --- End of simulation

    if self.steps is not None and self.iteration==self.steps-1:

      # End of simulation
      if self.verbose:
        print('→ End of simulation @ {:d} steps ({:.2f} s)'.format(self.steps, time.time()-self.tref))

      # End display
      if self.display is not None:
        self.display.stop()

    self.iteration += 1

  def run(self):
    '''
    Run the simulation
    '''

    # Check default number of frames in case of export
    if self.data_out is not None and self.steps is None:
      self.steps = 250
      if self.verbose:
        print('Number of steps set to the default value ({}).'.format(self.steps))

    # Reference time
    self.tref = time.time()

    # --- Main loop --------------------------------------------------------

    if self.display is None:
      i = 0
      while self.steps is None or i<self.steps:
        self.step(i)
        i += 1

    else:
      self.display.animate()

    
