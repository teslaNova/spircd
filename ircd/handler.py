from ircd.server import Server
from ircd.user import User
from ircd.numeric import Response
from ircd.commands.command import Command
from ircd.numeric import Response
from ircd.config import Config

from ircd import connection

from datetime import datetime, timedelta

import socket

class ServerHandler(connection.Handler):
  def on_read(self, client, data):
    server = Server.get_server(client)
    param = data.strip().split(' ')
    
    if param[0][0] != ':':
      pass # TODO: ERROR: Where does the data come from?
    else:
      user_info = param.pop(0)[1:]
      # parse rest and locate user
      # ...
      user = None
    
    command = param.pop(0)
    Command.execute(command, user, param)
  
  def on_connect(self, client):
    server = Server(client, server.get_host())
    Server.add(server)
    
  def on_disconnect(self, client):
    server = Server.get_server(client)
    Server.remove(server)
    
class UserHandler(connection.Handler):
  def on_read(self, client, data):
    user = User.get_user(client)
    param = data.strip().split(' ')
    
    print "{0} -> {1}".format(client, data).strip()
    
    try:
      if param[0][0] == ':':
        param.pop(0) # We know where the data comes from
    except:
      pass
    
    command = param.pop(0)
    
    if Command.exists(command) == False:
      Response.send_user(user, 'ERR_UNKNOWNCOMMAND', command)
      return
    
    if user.is_registered() == False and command not in ['QUIT', 'PONG', 'HELP', 'USER', 'SERVER', 'NICK', 'PASS', 'SERVICE']:
      Response.send_user(user, 'ERR_NOTREGISTERED')
      
    else:
      Command.execute(command, user, param)

  def on_connect(self, client):
    # Some messages for the clients out there. this is no rfc material
    client.send("NOTICE AUTH :*** Looking up your hostname...")
    client.send("NOTICE AUTH :*** Checking ident")
    client.send("NOTICE AUTH :*** Found your hostname")
    
#    client.send("NOTICE AUTH :*** No identd (auth) response") # send this after a while without conversation (not here!)
    try:
      user_host = socket.gethostbyaddr(client.get_host())[0]
    except:
      user_host = client.get_host()
      
    user = User(client, Server.get_local(), host=user_host, hop=0)
    User.add(user)
    
  def on_disconnect(self, client):
    user = User.get_user(client)
    
    for channel in user.channels:
      user.leave(channel)
    
    User.remove(user)
    
  # Specified
  def handle(self):
    for user in User.users:
      if user.state[0] == User.StateNormal: # PING, ..
        UserHandler().on_normal(user)
      
      elif user.state[0] == User.StateAuth: # Registering right now
        UserHandler().on_auth(user)
        
      if user.state[0] == User.StateWelcome: # Let him be welcome
        UserHandler().on_welcome(user)
  
  def on_welcome(self, user):
    # General Welcome
    Response.send_user(user, 'RPL_WELCOME', user.nick, user.user, user.host)
    Response.send_user(user, 'RPL_YOURHOST', Server.get_local().host, Config.VERSION)
    Response.send_user(user, 'RPL_CREATED', Config.CREATED)
    Response.send_user(user, 'RPL_MYINFO', Server.get_local().host, Config.VERSION, Config().misc['modes']['user'], Config().misc['modes']['channel'])
    Response.send_user(user, 'RPL_BOUNCE', Config().servers[0]['host'], Config().servers[0]['ports']['unsecured'][0])
    
    # Server Details (Users on server, network, whatever)
    
    # Message of the Day
    Response.send_user(user, 'RPL_MOTDSTART', Server.get_local().host)
    
    motd = open(Config().general['motd'])
    
    while 1:
      line = motd.readline().rstrip()
      
      if line == '':
        break
      
      Response.send_user(user, 'RPL_MOTD', line)
    
    Response.send_user(user, 'RPL_ENDOFMOTD')
    
    user.state = [User.StateNormal, 0]
    
  def on_auth(self, user):
    if user.is_registered():
      user.state = [User.StateWelcome, 0]
    
  def on_normal(self, user):
    if not user.is_registered():
      return # move bitch, get outta way
    
    #print "%s: ping = %s, state = %s" % (user, user.ping, user.state[1])
    
    if user.ping == '':
      if user.state[1] == 0.0:
        user.client.send("PING :%s" % Server.get_local().host)
        user.ping = Server.get_local().host
        user.state[1] = datetime.now() + timedelta(seconds=Config().misc['timeouts']['ping'])
    
      elif user.state[1] > 0: # pingless ticks
            user.state[1] -= 1

    elif user.ping != '':
      if (user.state[1] - datetime.now()) <= timedelta():
        self.on_read(user.client, "QUIT :Ping timeout")
    
      