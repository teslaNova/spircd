import json

class Config:
  file = 'localhost.conf' # default
  data = ""
  
  VERSION = "foobar-ircd-v1"
  CREATED = "10.10.10"
  
  def __init__(self):
    try:
      if(Config.data == ''):
        Config.reload()
    except:
      return#raise ConfigFileError('Could not load configuration file {0}', Config.file)
        
    self.config = Config.data
  
  def __getattr__(self, name): # TODO: recursion problem
    if name in ['general', 'servers', 'blacklist', 'operators', 'misc', 'modules']:
      return self.config[name]
    
    return object.__getattribute__(self, name)
    
  @staticmethod
  def reload():
    Config.data = json.loads(open(Config.file).read())