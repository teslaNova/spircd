class Handler:
  def __init__(self, target):
    self.target = target
    self.active = []
    
  def handle(self, state, mode, args):
    pass
    
  def set_switch(self, state, mode):
    if state == Mode.Set:
      if mode not in self.active:
        self.active.append(mode)
    elif state == Mode.Unset:
      if mode in self.active:
          self.active.remove(mode)
    else:
      pass # TODO: ERROR: unknown mode
      
  def get_switch(self, mode):
    if [] != [mode for mode in self.active]:
      return True
    else:
      return False
      
  def expect_argument(self, mode):
    return False

class Mode:
  Set = '+'
  Unset = '-'
  
  Modes = "" # Modes allowed
  
  def __init__(self, handler, mode=''):
    if not isinstance(handler, Handler):
      raise TypeError('handler must be ircd.mode.Handler')
    
    self.handler = handler
    self.evaluate(mode)
    
  def __str__(self):
    active_modes = ''.join(self.handler.active)
    
    if active_modes == '':
      return ''
      
    return "+{0}".format(active_modes)
    
  def is_active(self, mode):
    if mode in self.handler.active: # TODO: Also check lists, etc.
      return True
      
    return False
  
  def evaluate(self, mode):
    if type(mode) is not str:
      raise TypeError("argument needs to be a string")
    
    state = None
    cur_mode = None

    try:
      args = mode.split(' ')[1:].reverse()
    except:
      args = []
    
    mode = mode.split(' ')[0]
    
    while mode != "":
      c = mode[0]
      mode = mode[1:]

      # STATE
      if c in [Mode.Set, Mode.Unset]: 
        state = c
        continue
      
      # MODE SET
      if c in self.Modes:
        if state is None:
          return # TODO: ERROR: Invalid mode
        
        cur_mode = c
        
      # SWITCH
      if cur_mode is not None:
        if self.handler.expect_argument(mode):
          if args == []:
            continue # TODO: ERROR: Argument needed, no argument found
            
          self.handler.handle(state, cur_mode, args.pop())
        else:
          self.handler.handle(state, cur_mode, '')
          
        cur_mode = None
    