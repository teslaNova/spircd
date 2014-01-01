from ircd.commands.command import Command

from ircd.config import Config

from ircd.numeric import Response

from ircd.user import User, UserMode
from ircd.server import Server
from ircd.channel import Channel

from ircd.connection import Client 

import re

class PASSCommand(Command):
  name = "PASS"
  token = "P"
  desc = "Sets a connection password"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) != 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    if sender.is_registered():
      Response.send_user(sender, 'ERR_ALREADYREGISTRED')
      return
      
    pwd = param[0].lstrip(':')

    sender.password = pwd
    
  
class NICKCommand(Command):
  name = "NICK"
  token = "N"
  desc = "Sets a nickname"
  
  def evaluate_local(self, sender, param):
    re_nickname = "^([a-zA-Z\[\]\\`_\^\{\}|])([a-zA-Z\[\]\\`_^\{\}|0-9-]{0,})"

    if not isinstance(sender, User):
      return
      
    if len(param) != 1:
      Response.send_user(sender, 'ERR_NONICKNAMEGIVEN')
      return
    
    if param[0][0] == ':': # last param is always allowed to use ':'
      new_nick = param[0][1:]
    else:
      new_nick = param[0]
      
    if len(new_nick) < Config().misc['length']['nick-min'] or len(new_nick) > Config().misc['length']['nick-max']:
      Response.send_user(sender, 'ERR_ERRONEUSNICKNAME', new_nick)
      return
      
    if None == re.match(re_nickname, new_nick):
      Response.send_user(sender, 'ERR_ERRONEUSNICKNAME', new_nick)
      return
  
    if [] != [user for user in User.users if user.nick == new_nick]:
      Response.send_user(sender, 'ERR_NICKNAMEINUSE', new_nick)
      return
    
    self.broadcast(sender, param)    
    sender.nick = new_nick
    
  def broadcast_net(user, param):
    pass
  
class USERCommand(Command):
  name = "USER"
  token = "U"
  desc = "Registers a User"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
      
    if len(param) < 4:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
    
    if sender.is_registered():
      Response.send_user(sender, 'ERR_ALREADYREGISTRED')
      return
      
    sender.user = param[0]
#    sender.mode.evaluate(param[1]) # do not set mode, we are lazy and don't want to verify them here
    sender.real = ' '.join(param[2:]).lstrip(':')
      
class OPERCommand(Command):
  name = "OPER"
  token = "O"
  desc = "Registers a User as IRC Operator"

  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(Config().operators) == 0:
      Response.send_user(sender, 'ERR_NOOPERHOST')
      return
    
    if not sender.is_registered():
      return
    
    if sender.mode.is_active(UserMode.Operator):
      return
      
    if len(param) != 2:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
    
    for oper in Config().operators:
      if param[0] == oper['name']:
        if oper['password']['type'] == 'plain':
          if oper['password']['data'] == param[1]:
            sender.mode.evaluate('+{0}'.format(UserMode.Operator))
            break

          else:
            Response.send_user(sender, 'ERR_PASSWDMISMATCH')
    
    if sender.mode.is_active(UserMode.Operator):
      Response.send_user(sender, 'RPL_YOUREOPER')

class SERVICECommand(Command):
  name = "SERVICE"
  token = "S"
  desc = "Registers a Service"
  
  def evaluate_local(self, sender, param):
    pass
    
class QUITCommand(Command):
  name = "QUIT"
  token = "Q"
  desc = "Says goodbye to client"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
      
    if len(param) > 0:
      reason = ' '.join(param[0:]).lstrip(':')
    else:
      reason = 'Leaving'
    
    self.broadcast(sender, [self.name, ':'+reason])
    
    sender.client.send("ERROR :" + reason) # Set alternative QUIT-Response
    sender.client.disconnect()  
    
class PONGCommand(Command): # TODO: Implement correctly
  name = "PONG"
  token = ""
  desc = "Response to PING"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
      
    if len(param) > 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    pong_str = param[0].lstrip(':')
      
    if sender.ping == pong_str:
      sender.ping = ''
      sender.state[1] = 10 # 10 ticks no requests

# Init
for cmd_class in [PASSCommand, USERCommand, NICKCommand, OPERCommand, SERVICECommand, QUITCommand, PONGCommand]:
  Command.add(cmd_class)