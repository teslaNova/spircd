from ircd.commands.command import Command

from ircd.config import Config

from ircd.numeric import Response

from ircd.user import User, UserMode
from ircd.server import Server
from ircd.channel import Channel, ChanMode

from ircd.connection import Client 

import re

class JOINCommand(Command):
  name = "JOIN"
  token = "J"
  desc = "Joins (and creates) a Channel"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
      
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    channel_names = param[0].split(',')
    
    if len(param) > 1:
      channel_keys = param[1].split(',')
    else:
      channel_keys = []
      
    if len(channel_names) > Config().misc['limits']['targets']:
      Response.send_user(sender, 'ERR_TOOMANYTARGETS', sender.nick, len(channel_names), "Maximum amount of targets is %s" % Config().misc['limits']['targets'])
      
    for channel_name in channel_names:
      if channel_name[0] not in Config().misc['channel-prefix']:
        Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
        continue
      
      if len(sender.channels) > Config().misc['limits']['channels-per-user']:
        Response.send_user(sender, 'ERR_TOOMANYCHANNELS', channel_name)
      
      channel = Channel.find_channel(channel_name)
      
      if channel == None: # NEW CHANNEL
        channel = Channel(channel_name)
        channel.register()
        
      else:
        try:
          channel_key = channel_keys.pop(0)

        except:
          channel_key = ""
          
        if channel.limit != 0 and channel.limit == (len(channel.get_users()) + 1):
          Response.send_user(sender, 'ERR_CHANNELISFULL', channel_name)
          continue
        
        if channel.has_banned_user(sender):
          Response.send_user(sender, 'ERR_BANNEDFROMCHAN', channel_name)
          continue
        
        if channel.password != '':
          if channel.password != channel_key:
            Response.send_user(sender, 'ERR_BADCHANNELKEY', channel_name)
            continue
        
        if channel.mode.is_active(ChanMode.InviteOnly) and channel.has_invite(sender) == False:
          Response.send_user(sender, 'ERR_INVITEONLYCHAN', channel_name)
          continue
          
      sender.join(channel)

      self.broadcast(sender, [channel_name], (channel.get_users()), ignore_sender=False)
      
      TOPICCommand().evaluate_local(sender, [channel.name])
      #Response.send_user(sender, 'RPL_TOPIC', channel.name, channel.topic)
      NAMESCommand().evaluate_local(sender, [channel.name])
			
class PARTCommand(Command):
  name = "PART"
  token = "P"
  desc = "Leaves (and destroys) a Channel"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
      
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return
      
    channel_names = param[0].split(',')
    
    for channel_name in channel_names:
      if channel_name[0] not in Config().misc['channel-prefix']:
        Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
        continue
      
      channel = Channel.find_channel(channel_name)
      
      if channel is None or channel.has_user(sender) == False:
        Response.send_user(sender, 'ERR_NOTONCHANNEL', channel_name)
        continue
      
      sender.leave(channel)
      self.broadcast(sender, [channel_name] + param[1:], (channel.get_users()))


class TOPICCommand(Command):
  name = "TOPIC"
  token = ""
  desc = "Shows / Sets a Channel topic"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 1:
      Response.send_user(sender, 'ERR_NEEDMOREPARAMS', self.name)
      return

    if len(param) >= 1:
      channel_name = param[0]
      
      if channel_name[0] not in Config().misc['channel-prefix']:
        Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
        return
    
      channel = Channel.find_channel(channel_name)
    
      if channel is None:
        Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
        return

      if channel.has_user(sender) == False:
        Response.send_user(sender, 'ERR_NOTONCHANNEL', channel_name)
        return

      if len(param) > 1:
        if channel.has_operator(sender) == False:
          Response.send_user(sender, 'RPL_CHANOPRIVSNEEDED', channel_name)
          return
          
        channel.topic = ' '.join(param[1:]).lstrip(':')
          
      else:
        if channel.topic == '':
          Response.send_user(sender, 'RPL_NOTOPIC', channel.name)
        else:
          Response.send_user(sender, 'RPL_TOPIC', channel.name, channel.topic)

class NAMESCommand(Command):
  name = "NAMES"
  token = ""
  desc = "Shows Users on Channel"
  
  def evaluate_local(self, sender, param):
    if not isinstance(sender, User):
      return
    
    if len(param) < 1:
      return # TODO: NAMES not supported yet
      
    if len(param) == 1:
      channel_names = param[0].split(',')
      
      for channel_name in channel_names:
        if channel_name[0] not in Config().misc['channel-prefix']:
          Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
          continue
      
        channel = Channel.find_channel(channel_name)
      
        if channel is None:
          Response.send_user(sender, 'ERR_NOSUCHCHANNEL', channel_name)
          continue
          
        user_str = ""
        
        for user in (channel.get_users()):
          if channel.has_voice(user):
            user_str += " +" + user.nick
            
          elif channel.has_operator(user):
            user_str += " @" + user.nick
            
          elif channel.has_user(user):
            user_str += " " + user.nick
          
        Response.send_user(sender, 'RPL_NAMREPLY', channel_name, user_str.lstrip())
        Response.send_user(sender, 'RPL_ENDOFNAMES', channel_name)
        
    
    if len(param) > 1: # ERR_TOOMANYMATCHES, ERR_NOSUCHSERVER
      return # TODO: NAMES <channel,channel,..> [target] not supported yet

# Init
for cmd_class in [JOINCommand, PARTCommand, TOPICCommand, NAMESCommand]:
  Command.add(cmd_class)