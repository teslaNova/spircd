from ircd.config import Config

from ircd.handler import ServerHandler, UserHandler
from ircd.connection import Listener

from ircd.commands.command import Command

if __name__ == '__main__':
  listeners = []
  host = Config().general['host']

  Command.load_all()

  for cp in Config().general['ports']['clients']['unsecured']:
    listeners.append(Listener(host, cp, UserHandler))
    
#  for cp in Config().general['ports']['servers']['unsecured']:
#    listeners.append(Listener(host, cp, ServerHandler))
  
  try:
    while 1:
      for listener in listeners:
        listener.run_once()
        
      UserHandler().handle()
      
  except KeyboardInterrupt:
    for listener in listeners:
      listener.close()