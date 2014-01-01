from ircd.user import User
from ircd.server import Server

from ircd.connection import Client

class Response:
  Error = 0
  Reply = 1
  
  replies = []
  errors = []
  
  # TODO: Error Checking
  def __init__(self, _type, num, key, ftxt):
    self.num = num
    self.key = key
    self.ftxt = ftxt
    self.type = _type
    
  def __str__(self):
    return 'Response: {0} {1}{2}'.format(self.num, self.type_str(), self.key)
  
  @staticmethod
  def type_str(_type):
    if _type == Response.Error:
      return "ERR"
    elif _type == Response.Reply:
      return "RPL"
      
    raise TypeError('Response type is not correct')
  
  @staticmethod
  def send_user(user, key, *param):
    if not isinstance(user.client, Client):
      return

    server = Server.get_local()
    
    _type = key.split('_')[0]
    _key = key.split('_')[1]
    
    if _type == Response.type_str(Response.Reply):
      reply = Response.get_reply(_key)
    elif _type == Response.type_str(Response.Error):
      reply = Response.get_error(_key)

    data = ":{0} {1} {2} {3}".format(server.host, reply.num, user.nick, reply.ftxt.format(*param))
    
    user.client.send(data)
  
  @staticmethod
  def set(_type, num, key, ftxt):
    if _type not in [Response.Error, Response.Reply]:
      raise TypeError('Response type is not correct')
      
    new_reply = Response(_type, num, key, ftxt)
    
    if _type == Response.Error:
      Response.errors.append(new_reply)
    elif _type == Response.Reply:
      Response.replies.append(new_reply)
    
    return Response
  
  @staticmethod
  def get_error(key):
    return [err for err in Response.errors if err.key == key][0]
    
  @staticmethod
  def get_reply(key):
    return [reply for reply in Response.replies if reply.key == key][0]
    
    
Response.set(Response.Reply, '001', 'WELCOME', 'Welcome to the Internet Relay Network {0}!{1}@{2}')\
      .set(Response.Reply, '002', 'YOURHOST', 'Your host is {0}, running version {1}')\
      .set(Response.Reply, '003', 'CREATED', 'This server was created {0}')\
      .set(Response.Reply, '004', 'MYINFO', '{0} {1} {2} {3}')\
      .set(Response.Reply, '005', 'BOUNCE', 'Try server {0}, port {1}')
      
Response.set(Response.Reply, '301', 'AWAY', '{0} :{1}')\
      .set(Response.Reply, '302', 'USERHOST', ':{0}')\
      .set(Response.Reply, '303', 'ISON', ':{0}')\
      .set(Response.Reply, '305', 'UNAWAY', ':You are no longer marked as being away')\
      .set(Response.Reply, '306', 'NOAWAY', ':You have been marked as being away')\
      .set(Response.Reply, '311', 'WHOISUSER', '{0} {1} {2} * :{3}')\
      .set(Response.Reply, '312', 'WHOISSERVER', '{0} {1} :{3}')\
      .set(Response.Reply, '313', 'WHOISOPERATOR', '{0} :is an IRC operator')\
      .set(Response.Reply, '314', 'WHOWASUSER', '{0} {1} {2} *:{3}')\
      .set(Response.Reply, '315', 'ENDOFWHO', '{0} :End of WHO list')\
      .set(Response.Reply, '317', 'WHOISIDLE', '{0} {1} :seconds idle')\
      .set(Response.Reply, '318', 'ENDOFWHOIS', '{0} :End of WHOIS list')\
      .set(Response.Reply, '319', 'WHOISCHANNELS', '{0} :{1}')\
      .set(Response.Reply, '369', 'ENDOFWHOWAS', '{0} :End of WHOWAS')
      
Response.set(Response.Reply, '321', 'LISTSTART', '')\
      .set(Response.Reply, '322', 'LIST', '{0} {1} :{2}')\
      .set(Response.Reply, '323', 'LISTEND', ':End of LIST')\
      .set(Response.Reply, '324', 'CHANNELMODEIS', '{0} {1} {2}')\
      .set(Response.Reply, '325', 'UNIQOPIS', '{0} {1}')\
      .set(Response.Reply, '331', 'NOTOPIC', '{0} :No topic is set')\
      .set(Response.Reply, '332', 'TOPIC', '{0} :{1}')\
      .set(Response.Reply, '341', 'INVITING', '{0} {1}')\
      .set(Response.Reply, '342', 'SUMMONING', '{0} :Summoning user to IRC')\
      .set(Response.Reply, '346', 'INVITELIST', '{0} {1}')\
      .set(Response.Reply, '347', 'ENDOFINVITELIST', '{0} :End of channel invite list')\
      .set(Response.Reply, '348', 'EXCEPTLIST', '{0} {1}')\
      .set(Response.Reply, '349', 'ENDOFEXCEPTLIST', '{0} :End of channel exception list')\
      .set(Response.Reply, '351', 'VERSION', '{0} {1} :{2}')\
      .set(Response.Reply, '352', 'WHOREPLY', '{0} {1} {2} {3} {4} {5} :{6} {7}')\
      .set(Response.Reply, '353', 'NAMREPLY', '= {0} :{1}')\
      .set(Response.Reply, '364', 'LINKS', '{0} {1} :{2} {3}')\
      .set(Response.Reply, '365', 'ENDOFLINKS', '{0} :End of LINKS list')\
      .set(Response.Reply, '366', 'ENDOFNAMES', '{0} :End of NAMES list')\
      .set(Response.Reply, '367', 'BANLIST', '{0} {1}')\
      .set(Response.Reply, '368', 'ENDOFBANLIST', '{0} :End of channel ban list')\
      .set(Response.Reply, '371', 'INFO', ':{0}')\
      .set(Response.Reply, '372', 'MOTD', ':- {0}')\
      .set(Response.Reply, '374', 'ENDOFINFO', ':End of INFO list')\
      .set(Response.Reply, '375', 'MOTDSTART', ':- {0} Message of the day - ')\
      .set(Response.Reply, '376', 'ENDOFMOTD', ':End of MOTD command')\
      .set(Response.Reply, '381', 'YOUREOPER', ':You are now an IRC operator')\
      .set(Response.Reply, '382', 'REHASHING', '{0} :Rehashing')\
      .set(Response.Reply, '383', 'YOURESERVICE', 'You are service {0}')\
      .set(Response.Reply, '391', 'TIME', '{0} :{1}')\
      .set(Response.Reply, '392', 'USERSSTART', ':UserID   Terminal  Host')\
      .set(Response.Reply, '393', 'USERS', ':{0} {1} {2}')\
      .set(Response.Reply, '394', 'ENDOFUSERS', ':End of users')\
      .set(Response.Reply, '395', 'NOUSERS', ':Nobody logged in')

Response.set(Response.Reply, '200', 'TRACELINK', 'Link {0} {1} {2} V{3} {4} {5} {6}')\
      .set(Response.Reply, '201', 'TRACECONNECTING', 'Try. {0} {1}')\
      .set(Response.Reply, '202', 'TRACEHANDSHAKE', 'H.S. {0} {1}')\
      .set(Response.Reply, '203', 'TRACEUNKNOWN', '???? {0} {1}')\
      .set(Response.Reply, '204', 'TRACEOPERATOR', 'Oper {0} {1}')\
      .set(Response.Reply, '205', 'TRACEUSER', 'User {0} {1}')\
      .set(Response.Reply, '206', 'TRACESERVER', 'Serv {0} {1}S {2}C {3} {4}@{5} V{6}')\
      .set(Response.Reply, '207', 'TRACESERVICE', 'Service {0} {1} {2} {3}')\
      .set(Response.Reply, '208', 'TRACENEWTYPE', '{0} 0 {1}')\
      .set(Response.Reply, '209', 'TRACECLASS', 'Class {0} {1}')\
      .set(Response.Reply, '210', 'TRACERECONNECT', '')\
      .set(Response.Reply, '211', 'STATSLINKINFO', '{0} {1} {2} {3} {4} {5} {6}')\
      .set(Response.Reply, '212', 'STATSCOMMANDS', '{0} {1} {2} {3}')\
      .set(Response.Reply, '219', 'ENDOFSTATS', '{0} :End of STATS report')\
      .set(Response.Reply, '221', 'UMODEIS', '{0}')\
      .set(Response.Reply, '234', 'SERVLIST', '{0} {1} {2} {3} {4} {5}')\
      .set(Response.Reply, '235', 'SERVLISTEND', '{0} {1} :End of service listing')\
      .set(Response.Reply, '242', 'STATSUPTIME', ':Server up {0} days {1}')\
      .set(Response.Reply, '243', 'STATSOLINE', 'O {0} * {1}')\
      .set(Response.Reply, '251', 'LUSERCLIENT', ':There are {0} users and {1} service on {2} servers')\
      .set(Response.Reply, '252', 'LUSEROP', '{0} :operator(s) online')\
      .set(Response.Reply, '253', 'LUSERUNKNOWN', '{0} :unknown connection(s)')\
      .set(Response.Reply, '254', 'LUSERCHANNELS', '{0} :channels formed')\
      .set(Response.Reply, '255', 'LUSERME', ':I have {0} clients and {1} servers')\
      .set(Response.Reply, '256', 'ADMINME', '{0} :Administrative info')\
      .set(Response.Reply, '257', 'ADMINLOC1', ':{0}')\
      .set(Response.Reply, '258', 'ADMINLOC2', ':{0}')\
      .set(Response.Reply, '259', 'ADMINEMAIL', ':{0}')\
      .set(Response.Reply, '261', 'TRACELOG', 'File {0} {1}')\
      .set(Response.Reply, '262', 'TRACEEND', '{0} {1 :End of TRACE}')\
      .set(Response.Reply, '263', 'TRYAGAIN', '{0} :Please wait a while and try again.')\

Response.set(Response.Error, '401', 'NOSUCHNICK', '{0} :No such nick/channel')\
      .set(Response.Error, '402', 'NOSUCHSERVER', '{0} :No such server')\
      .set(Response.Error, '403', 'NOSUCHCHANNEL', '{0} :No such channel')\
      .set(Response.Error, '404', 'CANNOTSENDTOCHAN', '{0} :Cannot send to channel')\
      .set(Response.Error, '405', 'TOOMANYCHANNELS', '{0} :You have joined too many channels')\
      .set(Response.Error, '406', 'WASNOSUCHNICK', '{0} :There was no such nickname')\
      .set(Response.Error, '407', 'TOOMANYTARGETS', '{0} :{1} recipients. {2}')\
      .set(Response.Error, '408', 'NOSUCHSERVICE', '{0} :No such service')\
      .set(Response.Error, '409', 'NOORIGIN', ':No origin specified')\
      .set(Response.Error, '411', 'NORECIPIENT', ':No recipient given ({0})')\
      .set(Response.Error, '412', 'NOTEXTTOSEND', ':No text to send')\
      .set(Response.Error, '413', 'NOTOPLEVEL', '{0} :No toplevel domain specified')\
      .set(Response.Error, '414', 'WILDTOPLEVEL', '{0} :Wildcard in  toplevel domain')\
      .set(Response.Error, '415', 'BADMASK', '{0} :Bad Server/host mask')\
      .set(Response.Error, '421', 'UNKNOWNCOMMAND', '{0} :Unknown command')\
      .set(Response.Error, '422', 'NOMOTD', ':MOTD File is missing')\
      .set(Response.Error, '423', 'NOADMININFO', '{0} :No administrative info available')\
      .set(Response.Error, '424', 'FILEERROR', ':File error doing {0} on {1}')\
      .set(Response.Error, '431', 'NONICKNAMEGIVEN', ':No nickname given')\
      .set(Response.Error, '432', 'ERRONEUSNICKNAME', '{0} :Erroneous nickname')\
      .set(Response.Error, '433', 'NICKNAMEINUSE', '{0} :Nickname is already in use')\
      .set(Response.Error, '436', 'NICKCOLLISION', '{0} :Nickname collision KILL from {1}')\
      .set(Response.Error, '437', 'UNAVAILRESOURCE', '{0} :Nick/channel is temporarily unavailable')\
      .set(Response.Error, '441', 'USERNOTINCHANNEL', '{0} {1} :They aren\'t on that channel')\
      .set(Response.Error, '442', 'NOTONCHANNEL', '{0} :You\'re not on that channel')\
      .set(Response.Error, '443', 'USERONCHANNEL', '{0} {1} :is already on channel')\
      .set(Response.Error, '444', 'NOLOGIN', '{0} :User not logged in')\
      .set(Response.Error, '445', 'SUMMONDISABLED', ':SUMMON has been disabled')\
      .set(Response.Error, '446', 'USERSDISABLED', ':USERS has been disabled')\
      .set(Response.Error, '451', 'NOTREGISTERED', ':You have not registered')\
      .set(Response.Error, '461', 'NEEDMOREPARAMS', '{0} :Not enough parameters')\
      .set(Response.Error, '462', 'ALREADYREGISTRED', ':Unauthorized command (already registered)')\
      .set(Response.Error, '463', 'NOPERMFORHOST', ':Your host isn\'t among the privileged')\
      .set(Response.Error, '464', 'PASSWDMISMATCH', ':Password incorrect')\
      .set(Response.Error, '465', 'YOUREBANNEDCREEP', ':You are banned from this server')\
      .set(Response.Error, '466', 'YOUWILLBEBANNED', ':You\'ll be banned from this server')\
      .set(Response.Error, '467', 'KEYSET', '{0} :Channel key already set')\
      .set(Response.Error, '471', 'CHANNELISFULL', '{0} :Cannot join channel (+l)')\
      .set(Response.Error, '472', 'UNKNOWNMODE', '{0} :is unknown mode char to me for {1}')\
      .set(Response.Error, '473', 'INVITEONLYCHAN', '{0} :Cannot join channel (+i)')\
      .set(Response.Error, '474', 'BANNEDFROMCHAN', '{0} :Cannot join channel (+b)')\
      .set(Response.Error, '475', 'BADCHANNELKEY', '{0} :Cannot join channel (+k)')\
      .set(Response.Error, '476', 'BADCHANMASK', '{0} :Bad Channel Mask')\
      .set(Response.Error, '477', 'NOCHANMODES', '{0} :Channel doesn\'t support modes')\
      .set(Response.Error, '478', 'BANLISTFULL', '{0} {1} :Channel list is full')\
      .set(Response.Error, '481', 'NOPRIVILEGES', ':Permission Denied- You\'re not an IRC operator')\
      .set(Response.Error, '482', 'CHANOPRIVSNEEDED', '{0} :You\'re not channel operator')\
      .set(Response.Error, '483', 'CANTKILLSERVER', ':You can\'t kill a server')\
      .set(Response.Error, '484', 'RESTRICTED', ':Your connection is restricted')\
      .set(Response.Error, '485', 'UNIQOPPRIVSNEEDED', 'You\'re not the original channel operator')\
      .set(Response.Error, '491', 'NOOPERHOST', ':No O-lines for your host')\
      .set(Response.Error, '501', 'UMODEUNKNOWNFLAG', 'Unknown MODE flag')\
      .set(Response.Error, '502', 'USERSDONTMATCH', ':Cannot change mode for other users')