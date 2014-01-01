from ircd.config import Config
from ircd.channel import Channel

from ircd import mode

class UserModeHandler(mode.Handler): # Check for privileged modes like +O or +o
  def handle(self, state, mode, args):
    if not self.expect_argument(mode):
      self.set_switch(state, mode)
      
    else:
      pass # TODO: ERROR: Unknown Mode
    
class UserMode(mode.Mode):
  Away = 'a'
  Invisible = 'i'
  Wallops = 'w'  
  Restricted = 'r'  
  Operator = 'o'  
  LocalOperator = 'O'  
  ServerNotices = 's'
  
  Modes = Config().misc['modes']['user']

class User: # TODO: Client (Socket) stuff to be added
  users = []

  StateAuth = 1
  StateWelcome = 2
  StateNormal = 3

  def __init__(self, client, server, nick='*', user='', host='', real='', mode='', hop=0, id=0):
    self.id = id # for later use: token generation
    self.hop = hop
    self.nick = nick
    self.user = user
    self.host = host
    self.real = real
    self.password = ''
    self.channels = []
    self.mode = UserMode(UserModeHandler(self), mode)
    self.server = server
    self.state = [User.StateAuth, 0]
    self.ping = ''
    self.away = ''
    self.client = client
    
  def __str__(self):
    return "{0}!{1}@{2}".format(self.nick, self.user, self.host)

  def get_token(self):
    return "" #b64 self.id
    
  def get_abs_token(self):
    return "{0}{1}".format(self.server.get_token(), self.get_token())
  
  def is_local(self):
    if self.server.get_local() == self.server:
      return True
    
    return False  
  
  def join(self, channel):
    if not isinstance(channel, Channel):
      return
      
    if channel not in self.channels:
      self.channels.append(channel)
    
    if channel.users == []:
      channel.operator.append(self)
      
    channel.users.append(self)
      
  def leave(self, channel):
    if not isinstance(channel, Channel):
      return
      
    if channel in self.channels:
      self.channels.remove(channel)
  
    if self in channel.operator:
      channel.operator.remove(self)
      
    if self in channel.voice:
      channel.voice.remove(self)
      
    if self in channel.users:
      channel.users.remove(self)
      
    if channel.users == []:
      channel.unregister()
  
  @staticmethod
  def get_user(client):
    for user in User.users:
      if user.client == client:
        return user
        
    return None
    
  @staticmethod
  def find_user(nick):
    if nick == '*':
      return None
      
    for user in User.users:
      if user.nick == nick:
        return user
        
    return None
    
  @staticmethod
  def add(user): # TODO: Passenden Vergleich finden oder strengere (wenn schon mehrere * dann auch hostcheck!)
    if user.nick in [u.nick for u in User.users if user.nick != '*']: # Already added
      return
    
    User.users.append(user)
  
  @staticmethod  
  def remove(user):
    try:
      User.users.remove(user)
    except:
      pass
  
  def is_registered(self):
    if self.nick == '*' or self.user == '':
      return False
      
    pwd = Config().general['password']
    
    if pwd['type'] != 'none':
      if pwd['type'] == 'plain':
        if pwd['data'] != self.password:
          return False
      
    return True
    
  @staticmethod
  def get_unregistered():
    return [user for user in User.users if user.is_registered() == False]
    
  @staticmethod
  def get_registered():
    return [user for user in User.users if user.is_registered()]