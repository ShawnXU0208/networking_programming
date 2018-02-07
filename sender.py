import sys
import socket
import packet
import os.path
import select
import pickle

def store_in_buffer(packet):
    #this is a function that receive a packet and then put the data into a buffer to send
    the_tuple = (packet.magicno, packet.the_type, packet.seqno, packet.dataLen, packet.data)
    packet_buffer = pickle.dumps(the_tuple)
    return packet_buffer

def recover_from_buffer(the_buffer):
    #this is a function that receive the buffer and then convert it into a packet
    the_tuple = pickle.loads(the_buffer)
    new_packet = packet.Packet(the_tuple[0], the_tuple[1], the_tuple[2], the_tuple[3], the_tuple[4])
    return new_packet

def main(argv):
    #check the parameters from command line
    try:
        s_in_portnum = int(argv[1])
        s_out_portnum = int(argv[2])
        
        #check their range valid or not
        for portnum in [s_in_portnum, s_out_portnum]:
            if not ((portnum <= 64000 and portnum >= 1024) or type(portnum) == int):
                raise Exception ("Error on port number - out of range")   
          
        cs_in_portnum = int(argv[3])
        filename = argv[4]

    except:
        print("-------------------------------------------------------------------------------------------------------------")
        print("Please Enter 4 arguments in the order following:")
        print("python3 channel.py R_IN_portnumber R_OUT_portnumber CR_IN_portnumber FILENAME")
        print("-------------------------------------------------------------------------------------------------------------")
        
        raise Exception ("Error on accepting command line parameters")     
    
    #create sockets
    try:
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket r_out")
        sys.exit()

    try:
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket r_in")
        sys.exit()     
        
    #bind all sockets
    try:
        s_out.connect(("localhost", cs_in_portnum))
        s_in.bind(("localhost", s_in_portnum))    
    except:
        raise Exception ("Error on binding sockets")
    
    #check the existence of the file supplied
    #exit the sender profram if not
    if not os.path.exists(filename):
        raise Exception ("Error on opening the file - File does not exist")
    else:
        the_file = open(filename, 'rb')
        
    #initialize two values
    the_next = 0
    exit_flag = False
    
    packet_total = 0 # to sount the number of packets send
    #enter a loop
    while True:
	
        read_data = the_file.read(512)
        
        n = len(read_data)  #get how many bytes of the data read from the file
        
        if n == 0:
            #prepare a data packet
            new_packet = packet.Packet(0x497E, 0, the_next, 0, '')
            exit_flag = True
            
        elif n > 0:
            #prepare the data packet with data
            new_packet = packet.Packet(0x497E, 0, the_next, n, read_data)
   
        packet_buffer = store_in_buffer(new_packet)

        print("the packet buffer size: ", sys.getsizeof(packet_buffer))    
        
        #now enter the inner loop
        while True:
            s_out.send(packet_buffer)
            packet_total += 1
            if(new_packet.dataLen != 0): 
                print ("the total number of the packets send so far: ", packet_total)
                print("-----------------------------------------------------------------------")
            #wait for response packet for at most 1 second
            inputready, outputready, exceptready = select.select([s_in], [], [], 1)
	    
            if len(inputready) == 0:
                continue
            else:
                try:
                    rcvd = s_in.recv(600)
                except:
                    raise Exception ("Error on receiving data")
                rcvd = recover_from_buffer(rcvd)
                
            #check the content of the responding packet
            if rcvd.magicno != 0x497E:
                continue
            
            if rcvd.the_type != 1:
                continue
            
            if rcvd.dataLen != 0:
                continue
            
            if rcvd.seqno != the_next:
                continue
            
            #when all the checks success
            the_next = 1 - the_next
            
            if exit_flag == True:
                
                the_file.close()
                sys.exit()
            else:
                break
            
    #close the sockets
    s_in.close()
    s_out.close()
        
main(sys.argv)
                
