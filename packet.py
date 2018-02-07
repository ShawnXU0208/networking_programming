
# define the Packet Structure
class Packet:
    def __init__(self, magicno, the_type, seqno, dataLen, data):
        self.magicno = magicno      #value should be 0x497E
        self.the_type = the_type    #integer to distinguish dataPacket(0) and acknowledgementPacket(1)
        self.seqno = seqno          #integer, 0 or 1
        self.dataLen = dataLen      #integer, between 0 and 512
        self.data = data            #actual user data
        
        

    
    
        