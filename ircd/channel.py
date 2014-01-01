from ircd.config import Config

from ircd import mode

class ChanModeHandler(mode.Handler):
  def handle(self, state, mode, args):  
    if not self.expect_argument(mode):
      self.set_switch(state, mode)
      
    elif mode == ChanMode.Limit:
      target.limit = args
      
    elif mode == ChanMode.ChannelOperator:
      user_masks = args.split(',')
      
      for user_mask in user_masks:
        user = user.User.find_user(user_mask)
        
        if user is None:
          continue
          
        if self.target.is_operator(user) == False:
          self.target.operator.append(user)

    elif mode == ChanMode.Voice:
      user_masks = args.split(',')
      
      for user_mask in user_masks:
        user = Users.find_user(user_mask)
        
        if user is None:
          continue
          
        if self.target.has_voice(user) == False:
          self.target.voice.append(user)

    elif mode == ChanMode.Ban:
      masks = args.split(' ')
      # TODO: enumerate and validate masks, then add to the banlist

    elif mode == ChanMode.Password:
      target.password = args

    else:
      pass # TODO: ERROR: Unknown mode

  def expect_argument(self, mode):
    if mode in [ChanMode.Private, ChanMode.Secret, ChanMode.InviteOnly, ChanMode.TopicOnlyChanOp, ChanMode.OnlyLocalUsers, ChanMode.Modrated]:
      return False
      
    return True

    
class ChanMode(mode.Mode):
  ChannelOperator = 'o'
  Private = 'p'
  Secret = 's'
  InviteOnly = 'i'
  TopicOnlyChanOp = 't'
  OnlyLocalUsers = 'n'
  Modrated = 'm'
  Limit = 'l'
  Ban = 'b'
  Voice = 'v'
  Password = 'k'
  
  Modes = Config().misc['modes']['channel']
  
class Channel:
  channels = [] # #foobar
  local_channels = [] # &foobar
  
  def __init__(self, name, mode=''):
    self.name = name
    self.topic = ""
    self.password = ""
    self.limit = 0
    self.users = []
    self.banned = []
    self.voice = []
    self.operator = []
    self.invite = []
    self.mode = ChanMode(ChanModeHandler(self), mode)
    
  def is_banned(self, user):
    return False
    
  def is_user(self, user):
    return len([u for u in self.users if u.nick == user.nick]) != 0
  
  def has_voice(self, user):
    return len([u for u in self.voice if u.nick == user.nick]) != 0
    
  def is_operator(self, user):
    return len([u for u in self.operator if u.nick == user.nick]) != 0
    
  def has_invite(self, user):
    invitee = [i for i in self.invite if i.nick == user.nick]
    
    if invitee == []:
      return False
    
    self.invite.remove(invitee)
    return True
  
  def register(self):
    if self.name[0] == '#':
      Channel.channels.append(self)
    elif self.name[0] == '&':
      Channel.local_channels.append(self)
      
  def unregister(self):
    if self.name[0] == '#':
      Channel.channels.remove(self)
    elif self.name[0] == '&':
      Channel.local_channels.remove(self)
      
  @staticmethod
  def find_channel(name):
    if name[0] == '#':
      fchans = [c for c in Channel.channels if c.name == name]
      
    elif name[0] == '&':
      fchans = [c for c in Channel.local_channels if c.name == name]
      
    if fchans == []:
      return None
      
    return fchans[0]
