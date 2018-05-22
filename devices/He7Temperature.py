# Basic interface to retrieve temperature measurement form BF computer
# Server must be running on BF computer (The server just checks temperature log and returns last logged value)
from .He7TemperatureServer.MySocket import MySocket

class He7Temperature:
    def __init__(self,addr="131.180.32.72",port=8472,reset=True,verb=True,**kwargs):
        self.verb = verb
        if reset:
            self.reset()
        self.addr = addr
        self.port = port
    def GetTemperature(self): #Get Temperature from BF computer.  Returns a float in K
        # create an INET, STREAMing socket
        try:    
            s = MySocket()
            s.sock.connect((self.addr, self.port))
            word = s.myreceive()
            word = word.decode('utf_8')
            temperature = float(word)
            s.sock.close()
            if self.verb:
                print('He7 Temperature received: %f K' % (temperature))
        except:
            # needs to be changed to proper ErrorType
            temperature = -1
            print('Error when reading temperature')
        return temperature #in K!!
    def reset(self):
        pass
    def setverbose(self,verb=True):
        self.verb = verb