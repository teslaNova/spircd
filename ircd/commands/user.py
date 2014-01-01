from ircd.commands.command import Command

from ircd.config import Config

from ircd.numeric import Response

from ircd.user import User, UserMode
from ircd.server import Server
from ircd.channel import Channel

from ircd.connection import Client 

import re

class MODECommand(Command):
  name = "MODE"
  token = ""
  desc = "Sets / Unsets modes"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    target = sender
    
    if param[0] != sender.nick:
      target = User.find_user(param[0])
      
      if target == None:
        return # Must be a Channel, don't handle it here
      
      if not target.is_registered():
        return
      
    if len(param) == 1:
      Response.send_user(sender, 'RPL_UMODEIS', "%s" % target.mode)
      return
      
    if len(param) > 1: # TODO: '-Oo' wird derzeit nicht akzeptiert
      new_mode = param[2].strip(UserMode.Operator).strip(UserMode.LocalOperator)
      
      if target.nick != sender.nick:
        Response.send_user(sender, 'ERR_USERSDONTMATCH')
        return
      
      unknown = new_mode.strip(UserMode.Modes).strip(UserMode.Set).strip(UserMode.Unset)
      
      if unknown != '':
        Response.send_user(sender, 'ERR_UMODEUNKNOWNFLAG')
        return
      
      target.mode.evaluate(new_mode)


class PRIVMSGCommand(Command):
  name = "PRIVMSG"
  token = "P"
  desc = "Sends a Message to a Target"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 2:
      if len(param) == 1:
        Response.send_user(sender, 'ERR_NOTEXTTOSEND')
      
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    trgt_msks = param[0].split(',')
    message = param[1:]
    
    if len(trgt_msks) > Config().misc['limits']['targets']:
      Response.send_user(sender, 'ERR_TOOMANYTARGETS', sender.nick, len(trgt_msks), "Maximum amount of targets is %s" % Config().misc['limits']['targets'])
      return
      
    for trgt_msk in trgt_msks: # TODO: Currently using mask as nick. Not well solved, sir.
      if trgt_msk[0] in Config().misc['channel-prefix']:
        channel = Channel.find_channel(trgt_msk)

        if channel == None:
          Response.send_user(sender, 'ERR_CANNOTSENDTOCHAN', trgt_msk)
          continue # TODO: Channel not implemented yet
        
        self.broadcast(sender, [channel.name] + message, channel.users)
        
      else:  
        target = User.find_user(trgt_msk) # TODO: Check Mask for wildcards and implement missing ERR_WILDTOPLEVEL, ERR_NOTOPLEVEL
        
        if target == None:
          Response.send_user(sender, 'ERR_NOSUCHNICK', trgt_msk)
          continue
          
        if target.mode.is_active(UserMode.Away):
          msg = target.away
          
          if msg == '':
            msg = "No awaytext set."
            
          Response.send_user(sender, 'RPL_AWAY', target.nick, msg)
          
        self.broadcast(sender, [target.nick] + message, [target]) # TODO: Implement variable broadcasts (param "$to.nick" or something like that to call this method once and directly spread this command to everyone)


class AWAYCommand(Command):
  name = "AWAY"
  token = ""
  desc = "(Un-)Sets Away Mode and Message"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) == 0:
      if sender.mode.is_active(UserMode.Away):
        Response.send_user(sender, 'RPL_UNAWAY')
        sender.mode.evaluate('-' + UserMode.Away)
        
      else:
        Response.send_user(sender, 'RPL_NOAWAY')

        sender.mode.evaluate('+' + UserMode.Away)
        sender.away = 'I\'m away'
      
    if len(param) == 1:
      Response.send_user(sender, 'RPL_NOAWAY')

      sender.mode.evaluate('+' + UserMode.Away)
      sender.away = ' '.join(param[0:]).lstrip(':')


class WHOCommand(Command):
  name = "WHO"
  token = ""
  desc = "Identifies someone"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return


class WHOISCommand(Command):
  name = "WHOIS"
  token = ""
  desc = "Identifies someone more detailed"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return

# Init
for cmd_class in [MODECommand, PRIVMSGCommand, AWAYCommand]: #WHOCommand, WHOISCommand
  Command.add(cmd_class)