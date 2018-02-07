import sys
import socket
import select
import socket
import select
import random
import packet
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

# a function receive a list of number, return True if they are all distinct
# otherwise, return False
def are_different(number_list):
    new_list = []
    new_list.append(number_list[0])
    length = len(number_list)
    current = 1
    stop = False

    while (current < length and not stop):
        if number_list[current] not in new_list:
            new_list.append(number_list[current])
            current += 1
        else:
            stop = True

    if stop == True:
        return False
    else:
        return True

def main(argv):
    #check the seven parameters from command line
    try:
        cs_in_portnum = int(argv[1])
        cs_out_portnum = int(argv[2])
        cr_in_portnum = int(argv[3])
        cr_out_portnum = int(argv[4])

        #check their range valid or not
        for portnum in [cs_in_portnum, cs_out_portnum, cr_in_portnum, cs_out_portnum]:
            if not ((portnum <= 64000 and portnum >= 1024) or type(portnum) == int):
                raise Exception ("Error on port number - out of range")

        s_in_portnum = int(argv[5])
        r_in_portnum = int(argv[6])

        packet_loss_rate = float(argv[7])

        #check the rate
        if not (packet_loss_rate >= 0 and packet_loss_rate < 1):
            raise Exception ("Error on packet loss rate")

    except:
        print("-------------------------------------------------------------------------------------------------------------")
        print("Please Enter 7 arguments in the order following:")
        print("python3 channel.py CS_IN_portnumber CS_OUT_portnumber CR_IN_portnumber CR_OUT_portnumber S_IN_portnumber R_IN_portnumber LOSS_RATE")
        print("-------------------------------------------------------------------------------------------------------------")

        raise Exception ("Error on accepting command line parameters")


    #create its four sockets
    try:
        cs_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket cs_out")
        sys.exit()

    try:
        cs_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket cs_in")
        sys.exit()

    try:
        cr_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket cr_out")
        sys.exit()

    try:
        cr_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error:
        print ("Failed to create socket cr_in")
        sys.exit()

    #bind all sockets
    try:
        cs_out.connect(("localhost", s_in_portnum))
        cr_out.connect(("localhost", r_in_portnum))
    except:
        raise Exception ("Error on binding sockets")

    try:
        cs_in.bind(("localhost", cs_in_portnum))
    except (socket.error , msg):
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    try:
        cr_in.bind(("localhost", cr_in_portnum))
    except (socket.error , msg):
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    #check the port numbers used are all dinstinct
    if not are_different([cs_out_portnum, cs_in_portnum, cr_in_portnum, cr_out_portnum]):
        raise Exception ("Error on port numbers, they should be distinct")

    input_list = [cs_in, cr_in]   # this is a list for select() function
    #Now, enter an infinite loop
    while True:

        #use the select() function to process all packets
        inputready, outputready, exceptready = select.select(input_list, [], [])

        for s in inputready:

            if s == cs_in:
                #handle the cs_in socket
                try:
                    rcvd = cs_in.recv(600)
                except:
                    raise Exception ("Error on receiving data at cs_in socket")

                the_packet = recover_from_buffer(rcvd)
                print("the size of cs_in packet is: ", sys.getsizeof(the_packet))

                if the_packet.magicno != 0x497E:
                    break

                u = random.random()
                if u < packet_loss_rate:
                    #drop this packet
                    break
                else:
                    #keep this packet
                    packet_buffer = store_in_buffer(the_packet)
                    print("the size of cs_in packet_buffer is: ", sys.getsizeof(packet_buffer))

                    try:
                        cr_out.send(packet_buffer)
                    except:
                        raise Exception ("Error on sending data from cr_out socket")


            elif s == cr_in:
                #handle the sr_in socket
                try:
                    rcvd = cr_in.recv(600)
                except:
                    raise Exception ("Error on receiving data at cr_in socket")

                the_packet = recover_from_buffer(rcvd)

                print("the size of cr_in packet is: ", sys.getsizeof(the_packet))

                if the_packet.magicno != 0x497E:
                    break

                u = random.random()
                if u < packet_loss_rate:
                    #drop the packet
                    break
                else:
                    #keep the packet
                    packet_buffer = store_in_buffer(the_packet)
                    print("the size of cr_in packet_buffer is: ", sys.getsizeof(packet_buffer))

                    try:
                        cs_out.send(packet_buffer)
                    except:
                        raise Exception ("Error on sending data from cs_out socket")

            else:
                print ("Unknown socket.")


main(sys.argv)