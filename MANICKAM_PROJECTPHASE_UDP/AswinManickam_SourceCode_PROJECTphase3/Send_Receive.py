from Globals import *
import Functions


'''This function is the basically the client's RDT function to send the file.'''
def RdtSendPkt(udp_sock,addr,seq_nmbr,data,E_Prob=0):
    send_successful = 0                                                     #send_sucessful is set to '0' initially
    packet = Functions.MakePkt(seq_nmbr,Functions.checksum(data),data)      #Packet is created with the sequence number,checksum,data

    while (not(send_successful)):                                           #loop goes on until condition becomes 'false'
        udp_sock.sendto(packet,addr)                                        #sending the packet to server

        Ack_pkt,addr = udp_sock.recvfrom(buffer_size)                       #Client receiving the Acknowledgement packet
        pkt_seq_nmbr,sender_chksum,ack_data=Functions.ExtractData(Ack_pkt)  #Extracts the sequence number, checksum value, data from a packet

        if (Functions.Error_Condition(E_Prob)):                             #If Data_bit_error is true, it starts to corrupt data intentionally
            ack_data = Functions.Data_Corrupt(ack_data)                     #Function to corrupt data
            print ("ACK CORRUPTED")

        refrenceAck ="ACK"+str(seq_nmbr)                                    #This is the referenced Acknowledgement with respect to the sequence number. (string "ACK" also added to the sequence number for user convention and to avoid confusion)
        Ack_checksum = Functions.checksum(ack_data)                         #Finds the checksum for received acknowledgement
        ack_data = ack_data.decode("UTF-8")                                 #Decodes from byte to integer for the comparison

        #Comparing Acknowledgement
        if (ack_data != refrenceAck) or (Ack_checksum != sender_chksum ):   #if packet is corrupted or has unexpected acknowledgement it resends the packet
            print ("Ack: {0}, sequence_number: {1}, Ack_checksum_Value: {2}, checksum_from_server: {3}".format(ack_data,seq_nmbr,Ack_checksum,sender_chksum))
            print("Resending the Packet\n")
            send_successful = 0                                             #Loop continues until satisfies condition, Basically resends the packet.

        elif (ack_data == refrenceAck) and (Ack_checksum == sender_chksum ): #if packet is not corrupted and has expected acknowledgement it does nothing. *updates sequence number for next loop
            print ("Ack: {0}, sequence_number: {1}, Ack_checksum_Value: {2}, checksum_from_server: {3}".format(ack_data,seq_nmbr,Ack_checksum,sender_chksum))
            seq_nmbr = 1-seq_nmbr                                           #updating sequence number
            send_successful = 1                                             #Comes out of while loop.
    return seq_nmbr                                                         #returns updated sequence number



'''This function is the basically the Server's RDT function to receive the file.'''
def RdtReceivePkt (sock,buffer_size,Rx_seq_num,E_Prob=0):
    receive_successful = 0                                                  #Receive_sucessful is set to '0' initially
    while (not(receive_successful)):                                        #loop goes on until condition becomes 'false'
        data, address = sock.recvfrom(buffer_size)                          #Packet is received from client
        seq_num,checksum,Img_Pkt=Functions.ExtractData(data)                #Extracts the sequence number, checksum value, data from a packet

        if (Functions.Error_Condition(E_Prob)):                             #If Data_bit_error is true, it starts to corrupt packet intentionally
            Img_Pkt = Functions.Data_Corrupt(Img_Pkt)                       #Function to corrupt data
            print ("\nData Corrupted")

        Rx_checksum = Functions.checksum(Img_Pkt)                           #Receiver Checksum in integer

        if ((Rx_checksum == checksum) and (seq_num == Rx_seq_num)):         #if packet is not corrupted and has expected sequence number, sends Acknowledgement with sequence number  *updates sequence number for next loop
            Ack = Rx_seq_num                                                #sends sequence number
            Ack = b'ACK' + str(Ack).encode("UTF-8")                         #Converting (Ack) from int to string and then encoding to bytes
            Sender_Ack = Functions.MakePkt(seq_num,Functions.checksum(Ack),Ack) #Server sends Ack with Seq_num, checksum, Ack
            print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
            Rx_seq_num = 1-seq_num                                          #update sequence number to the next expected seqNum
            receive_successful = 1                                          #Comes out of while loop

        elif ((Rx_checksum != checksum) or (seq_num != Rx_seq_num)):        #if packet is corrupted or has unexpected sequence number, sends Acknowledgement with previous Ackowledged sequence number. Requests client to resend the data.
            Ack = 1 - Rx_seq_num                                            #last acked sequence numvber
            Ack = b'ACK' + str(Ack).encode("UTF-8")                         #Converting (Ack) from int to string and then encoding to bytes
            Sender_Ack = Functions.MakePkt(1 - Rx_seq_num,Functions.checksum(Ack),Ack) #Server sends Ack with Seq_num, checksum, Ack
            print("Server Requested to Resend the Packet")
            print("Sequence Number: {0},Receiver_sequence: {1}, Checksum from Client: {2}, Checksum for Received File: {3}\n".format(seq_num,Rx_seq_num,checksum,Rx_checksum))
            receive_successful = 0                                          #Loop continues until satisfies condition
        sock.sendto(Sender_Ack,address)                                     #sending the Acknowledgement packet to the client

    return Img_Pkt,address,Rx_seq_num                                       #returns data,address,updated sequence number
