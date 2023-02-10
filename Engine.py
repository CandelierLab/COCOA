import random
from math import *
import numpy as np
from collections import defaultdict
import time

# === Geometry =============================================================

class foop:
  '''
  Field of orientated points
  '''
  def __init__(self, X, Y, A, box):
    self.X = X
    self.Y = Y
    self.A = A
    self.box = box

  def center(self, tx, ty, ta=0):
    '''
    (tx,ty) is the target position, which will be at (0,0) after translation
    ta is the target angle, which will be at 0 after rotation
    '''

    # Translation (with boundary conditions)
    X = (self.X - tx + self.box/2) % self.box - self.box/2
    Y = (self.Y - ty + self.box/2) % self.box - self.box/2

    # Rotation
    if ta!=0:
      Z = X+Y*1j
      Z = np.abs(Z)*np.exp(1j*(np.angle(Z)-ta))
      X = np.real(Z)
      Y = np.imag(Z)

    return foop(X, Y, self.A-ta, self.box)

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

  def __init__(self, v, sigma, box, damax=None, initial_position=None):

    # Definitions
    self.v = v
    self.damax = damax if damax is not None else np.pi/2
    self.sigma = sigma
    self.box = box

    # Initial position
    if initial_position is None:
      self.x = random.random()*self.box
      self.y = random.random()*self.box
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

    # Positional density
    # self.density['pos'].append(np.sum(np.exp(-(np.abs(Z[I])/self.box/self.kde_sigma['pos'])**2/2)))
    self.density['pos'].append(np.sum(np.exp(-(np.abs(Z[I])/self.kde_sigma['pos'])**2/2)))

    # Angular density
    self.density['ang'].append(np.sum(np.exp(-(np.angle(Z[I])/self.kde_sigma['ang'])**2/2)))

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
    self.x = ((self.x + self.v*np.cos(self.a)) % self.box)[0]
    self.y = ((self.y + self.v*np.sin(self.a)) % self.box)[0]

# === Blind agents =========================================================

class Blind(agent):
  '''
  Blind agent, i.e. not taking the other agents into account 
  '''

  def __init__(self, v, sigma, box=1, initial_position=None):    
    super().__init__(v, sigma, box, initial_position)
    
  def update(self, i, F):
    '''
    Update angles and move
    '''

    # Update perception
    I = self.perceive(i, F, reorient=False)

    # Add angular noise and move
    self.move()

# === Vicsek agents ========================================================

class Vicsek(agent):
  '''
  Vicsek agent
  '''

  def __init__(self, v, sigma, r, box=1, initial_position=None):    
    super().__init__(v, sigma, box, initial_position)
    self.r = r
    
  def update(self, i, F):
    '''
    Update angles and move
    '''

    # Update perception
    I = self.perceive(i, F, r=self.r, reorient=False, include_self=True)
    
    # Update angle
    self.a = np.angle(np.exp(1j*F.A[I]).sum())

    # Add angular noise and move
    self.move()

    return self

# === HENN-driven agents ====================================================

class HENN(agent):
  '''
  Hard-encoded neral network agent
  '''

  def __init__(self, v, damax=None, aW=None, aWs=None, vW=None, vWs=None, sigma=0, box=1, initial_position=None):
    super().__init__(v, sigma, box, damax, initial_position)
    self.v0 = v

    # --- Angular weights

    if aW is None:
      if aWs is not None:
        self.aW = aWs + [-x for x in reversed(aWs)]
      else:
        raise AttributeError('Weights aW must be specified.')
    else:
      self.aW = aW

      # --- Velocity weights
    
    if vW is None:
      if vWs is not None:
        self.vW = vWs + list(reversed(vWs))
      else:
        self.vW = [0]*len(self.aW)
    else:
      self.vW = vW

    # Number of slices
    if len(self.aW)==len(self.vW):
      self.ns = len(self.aW)
    else:
      raise AttributeError('Non-corresponding number of weights')

  def update(self, i, F):
    '''
    Update angles and move
    '''

    # Update perception
    self.perceive(i, F)

    # Values
    v = []
    for k in range(self.ns):

      # Indices
      I = np.where((self.theta>=2*k*np.pi/self.ns) & (self.theta<=2*(k+1)*np.pi/self.ns))

      # Values
      if len(self.rho):
        v.append(np.sum((self.rho[I])**-1))
        # v.append(np.sum(np.exp(-self.rho[I]/0.5)))
      else:
        v.append(0)

    # Update angle
    self.a += np.tanh(np.sum(np.multiply(self.aW, v)))*self.damax
    
    # Update speed
    self.v = self.v0*(1 + np.tanh(np.sum(np.multiply(self.vW, v))))

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
    self.groups = defaultdict(list)
        
    # Engine
    self.engine = engine

  def __str__(self):
    s = '--- Agents ---\n'
    s += 'N: ' + str(self.N)
    return s

  def add(self, n, type, name=None, blinding=False, initial_disposition=None, damax_range=None, **kwargs):
    '''
    Add one or many agents
    '''

    # Default name
    if name is None:
      name = type

    # Update groups
    alist = [*range(self.N,self.N+n)]
    self.groups[name].extend(alist)

    # --- Initial positions

    if initial_disposition is None:
      init_pos = [None]*n
    else:
      init_pos = []
      a = ceil(sqrt(n))
      d = 1/a
      for k in range(n):
        i = k // a
        j = k % a
        init_pos.append(((i+1/2)*d, (j+1/2)*d, 0))
        
    # Add agents
    for i,k in enumerate(alist):

      if damax_range is not None:
        kwargs['damax'] = damax_range[0] + np.random.rand(1)*(damax_range[1]-damax_range[0])
        
      # Add the agent based on class name
      AgentClass = globals()[type]
      self.list.append(AgentClass(**kwargs, box=self.engine.box, initial_position=init_pos[i]))

      self.list[k].kde_sigma = self.engine.kde_sigma

      if blinding:
        self.list[k].blindlist = alist

    # Update agent count
    self.N =  len(self.list)
    
    if self.engine.verbose is not None:
      print('→ Added {:d} {:s} agents ({:s}).'.format(n, type, name))

  def compile(self):
    '''
    Compile all positions and orientations
    '''

    return foop(
      np.array([A.x for A in self.list],dtype=object).flatten().astype(float),
      np.array([A.y for A in self.list],dtype=object).flatten().astype(float),
      np.array([A.a for A in self.list],dtype=object).flatten().astype(float),
      self.engine.box)

# === Engine ===============================================================

class Engine:
  '''
  Engine 
  '''

  # Contructor
  def __init__(self, steps=None, data_in=None, data_out=None):

    # Arena
    self.box = 1

    # Agents
    self.agents = Agents(self)
    
    # Display
    self.display = None

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

  def input(self, dfile):

    # Data source
    self.data_in = dfile

    # Add agents
    self.agents.add(self.data_in.Nagents, 'Data_in', dataFile = self.data_in)

  def setup_display(self):
    '''
    Define a display object
    '''

    self.display = simulation.display.visu(self, box=self.box)

  def step(self):
    '''
    One step of the simulation
    '''

    if self.verbose is not None and (self.iteration % self.verbose)==0:
      print('→ Iteration {:d} ({:.2f} s) ...'.format(self.iteration, time.time()-self.tref))

    # Prepare data
    F = self.agents.compile()

    # --- Save data
    
    if self.data_out is not None:
      F.save(self.data_out, step=self.iteration)

    if self.display is not None:
      self.display.update(self.iteration, F)

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

    
