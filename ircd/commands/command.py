import os

from ircd.numeric import Response

from ircd.user import User
from ircd.server import Server

from ircd.connection import Client 

class Command:
  commands = []
  
  name = ""
  token = ""
  desc = ""
  
  def evaluate_local(self, sender, param):
    pass
    
  def evaluate_p10(self, sender, param):
    pass
    
  def broadcast(self, sender, param, to=None, ignore_sender=True):
    if to == None:
      to = User.users
      
    self.broadcast_p10(sender, param, to, ignore_sender)
    self.broadcast_local(sender, param, to, ignore_sender)
    
  def broadcast_p10(self, sender, param, to, ignore_sender):
    pass
  
  def broadcast_local(self, sender, param, to, ignore_sender):
    if not sender.is_registered():
      return
      
    for u in to:
      if not u.is_local() or not u.is_registered() or (u == sender and ignore_sender == True):
        continue
        
      u.client.send(":{0} {1} {2}".format(sender, self.name, ' '.join(param)))
      
  @staticmethod
  def execute(cmd, sender, param):
    local = [c for c in Command.commands if c.name == cmd and c.name != '']
    p10 = [c for c in Command.commands if c.token == cmd and c.token != '']
    
    for command in local:
        command().evaluate_local(sender, param)
        
    for command in p10:
        command().evaluate_p10(sender, param)
  
  @staticmethod
  def add(cmd):
    if not issubclass(cmd, Command):
      return
    
    if cmd in Command.commands:
      return
      
    Command.commands.append(cmd)
  
  
  @staticmethod
  def remove(cmd):
    if not issubclass(cmd, Command):
      return
    
    if cmd not in Command.commands:
      return
      
    Command.commands.remove(cmd)

  @staticmethod
  def load_all():
    mods = filter(lambda x: not x.endswith('.pyc') and not x.startswith('__'), os.listdir(os.path.dirname(__file__)))
    self = __file__.split(os.sep)[-1].split('.')[0]
    
    mods.remove('command.py')
    
    for x in mods:
      __import__("ircd.commands.{0}".format(x)[:-3])
      
  @staticmethod
  def exists(name):
    if [] == [cmd for cmd in Command.commands if cmd.name == name]:
      return False
      
    return True
