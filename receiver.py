import packet
import sys
import socket
import os.path
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
        r_in_portnum = int(argv[1])
        r_out_portnum = int(argv[2])
        
        #check their range valid or not
        for portnum in [r_in_portnum, r_out_portnum]:
            if not ((portnum <= 64000 and portnum >= 1024) or type(portnum) == int):
                raise Exception ("Error on port number - out of range")   
            
        cr_in_portnum = int(argv[3])
        
        filename = argv[4]
        
    except:
        print("-------------------------------------------------------------------------------------------------------------")
        print("Please Enter 4 arguments in the order following:")
        print("python3 channel.py R_IN_portnumber R_OUT_portnumber CR_IN_portnumber FILENAME")
        print("-------------------------------------------------------------------------------------------------------------")
        
        raise Exception ("Error on accepting command line parameters")   
    
    #create sockets
    try:
        r_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket r_out")
        sys.exit()

    try:
        r_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket r_in")
        sys.exit()    
        
    #bind all sockets
    try:
        r_out.connect(("localhost", cr_in_portnum))
        r_in.bind(("localhost", r_in_portnum))
    except:
        raise Exception ("Error on binding sockets")
    
    #open the file 
    if os.path.exists(filename):
        raise Exception ("Error on making the file - The file has existed")    
    else:
        the_file = open(filename, 'wb')
    
    expected = 0 
    
    #now enter a loop
    while True:
        
        try:
            rcvd = r_in.recv(10000)
        except:
            raise Exception ("Error on receiving data at r_in socket")

        the_packet = recover_from_buffer(rcvd)

        # process the packet received
        if the_packet.magicno != 0x497E:
            continue
        
        if the_packet.the_type != 0:
            continue
        
        if the_packet.seqno != expected:
            
            #prepare an acknowledgement packet
            new_packet = packet.Packet(0x497E, 1, the_packet.seqno, 0, '')
            packet_buffer = store_in_buffer(new_packet)
            
            try:
                r_out.send(packet_buffer)
            except:
                raise Exception ("Error on sending data form r_out socket")
            
            continue
        
        else:
            #prepare an acknowledgement packet
            new_packet = packet.Packet(0x497E, 1, the_packet.seqno, 0, '')
            packet_buffer = store_in_buffer(new_packet)
            
            try:
                r_out.send(packet_buffer)   
            except:
                raise Exception ("Error on sending data from r_out socket")
            
            expected = 1 - expected
            
            if the_packet.dataLen > 0:
                the_file.write(the_packet.data)
                continue
            else:
                #close the file and sockets
                the_file.close()
                r_in.close()
                r_out.close()
                break

main(sys.argv) 