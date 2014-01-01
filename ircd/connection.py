from ircd.config import Config

import socket
import select

class Handler:
  def on_accept(self, listener, client):
#    print "{0} accepted {1}".format(listener, client)
    pass
    
  def on_listen(self, listener):
    print "{0} listening now".format(listener)
    pass
  
  def on_read(self, client, data):
#    print "{0} wrote '{1}'".format(client, data.strip())
    pass
  
  def on_send(self, client, data):
#    print "sending {0}: {1}".format(client, data.strip())
    pass
  
  def on_connect(self, client):
#    print "{0} connecting".format(client)
    pass  
    
  def on_disconnect(self, client):
#    print "{0} disconnected".format(client)
    pass

  def on_timeout(self, client):
    pass

class Listener:
  def __str__(self):
    return "<listener: {0}:{1}>".format(self.addr[0], self.addr[1])
  
  def __init__(self, host, port, handler=Handler):
    self.handler = handler
    self.addr = (host, port)
    self.clients = []
    

    self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.con.bind((host, port))
    self.con.listen(1)
      
    self.handler().on_listen(self)
    
  def run_once(self):
    sc = [self.con] + [c.con for c in self.clients]
    
    rs, [], [] = select.select(sc, [], [], Config().general['timeout'])
    
    for s in rs:
      # LISTENER readable
      if self.con == s:
        cs, ca = self.con.accept()
        c = Client(cs, ca, self)
        
        self.clients.append(c)
        
        self.handler().on_accept(self, c)
        self.handler().on_connect(c)
        
      # CLIENT readable
      elif s in sc[1:]:
        for c in self.clients:
          if c.con in sc[1:]:
            line = c.readline()
            
            if line == '':
              self.drop(c)
              
            else:
              self.handler().on_read(c, line)
              
  def run(self):
    while True:
      self.run_once()
    
  def drop(self, client):
    self.handler().on_disconnect(client)
    
    self.clients.remove(client)
    client.con.close()
    
  def close(self):
    self.con.close()
    
class Client:
  def __str__(self):
    return "<client: {0}:{1}>".format(self.addr[0], self.addr[1])
  
  def __init__(self, con, addr, listener):
    self.con = con
    self.addr = addr
    self.listener = listener
    self.buffer = ""
    
  def get_host(self):
    return self.addr[0]  
    
  def disconnect(self):
    self.listener.drop(self)
    
  def send(self, data):
    packet = "{0}\r\n".format(data)
    
    print "{0} <- {1}".format(self, packet).strip()
    
    self.listener.handler().on_send(self, packet)
    self.con.send(packet)
    
  def read(self, n):
    if len(self.buffer) >= n:
      tmp = self.buffer[:n]
      self.buffer = self.buffer[n:]
      
      return tmp
      
    self.buffer += self.con.recv(1)
    
    return self.read(n)
    
  def readline(self):
    line = ""

    while False == line.endswith("\r\n"):
      line += self.read(1)
      
    return line