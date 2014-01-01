from ircd.config import Config

class Server:
  servers = []
  
  def __init__(self, client, host, info='', id=0, hop=0, ):
    self.id = id # for later use: token generation
    self.hop = hop
    self.host = host
    self.info = info

    self.client = client
#    self.listeners = {'servers': [], 'clients': []}
  
  @staticmethod
  def add(server):
    if server.host in [s.host for s in Server.servers]: # Already added
      return
      
    Server.servers.append(server)
  
  @staticmethod  
  def remove(server):
    Server.servers.remove(server)

  def get_token(self):
    return "" #b64 self.id
    
  @staticmethod
  def get_local():
    for server in Server.servers:
      if server.host == Config().general['host']:
        return server
      
    return None
    
  @staticmethod
  def get_server(client):
    for server in Server.servers:
      if server.client == client:
        return server
        
    return None
    
Server.add(Server(None, Config().general['host'], Config().general['info'])) # Local