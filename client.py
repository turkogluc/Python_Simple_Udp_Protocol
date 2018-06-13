# Cemal Turkoglu - 150140719
#
# Message Board Client Application
# UDP Communication

from socket import *

MBS_ADDRESS = "localhost"
MBS_PORT = 12345

clientSocket = socket(AF_INET,SOCK_DGRAM)   # Creating a UDP Socket

# first operation for client is to register the system, as explained in assignment description
username = raw_input('username:')
password = raw_input('password:')

regMes = "REG:"+username+":"+password       # first operation is by default registration
clientSocket.sendto(regMes,(MBS_ADDRESS,MBS_PORT))  # send REG command

response,serverAddress = clientSocket.recvfrom(2048)    # wait response
responseMes = response.split(':')           # split response elements into array

if responseMes[0] == 'ACCEPT':
    print 'Successful user registration: '+responseMes[1]   #Success
else:
    print 'Rejected user registration: '+responseMes[1]     #Failure


while True:
    # Defined Client operations
    print ""
    print """Operation:
            1) Create a message board
            2) List message boards
            3) Add a message to a message board
            4) List messages on a message board
            5) Register another user
                       
            0) Exit
            """
    command = raw_input("command:")


    # create Message board
    if command == "1":
        mbsName = raw_input("board name:")  # board name is taken from user
        msgToSend = "CREATE:"+mbsName
        clientSocket.sendto(msgToSend, (MBS_ADDRESS, MBS_PORT)) # send CREATE command
        response, serverAddress = clientSocket.recvfrom(2048)   # wait for response
        responseMes = response.split(':')
        if responseMes[0] == 'ACCEPT':
            print responseMes[1]+' Message board is created'    #Success
        else:
            print responseMes[1]+' Message board could not be created' #Failure


    # List Message Boards
    elif command == "2":
        clientSocket.sendto("LIST:BOARDS", (MBS_ADDRESS, MBS_PORT))
        response, serverAddress = clientSocket.recvfrom(2048)
        responseMes = response.split(':')
        responseMes = responseMes[2:]  # removing first 2 headers (list,boards) from list
        if len(responseMes) == 1:      # if there is 1 message => 2 possible case
            if responseMes[0] == '':   # empty : means no message board
                print 'There is no message board'
            else:                      # or name of 1 message board
                print "Message boards:"
                print responseMes[0]
        else:                          # if there are more than 1 message board
            print "Message boards:"
            for mbsName in responseMes:
                print mbsName


    # Add a message to message board
    elif command == "3":
        # username password is asked to user everytime to validate
        user = raw_input("username:")
        passwd = raw_input("pasword:")
        mbsName = raw_input("board name:")
        msgContent = raw_input("Message:")

        requestMsg = "ADD:"+user+":"+passwd+":"+mbsName+":"+msgContent # Creating ADD command
        clientSocket.sendto(requestMsg, (MBS_ADDRESS, MBS_PORT))       # Sending ADD
        response, serverAddress = clientSocket.recvfrom(2048)          # Wait for response
        responseMes = response.split(':')           # split message
        status = responseMes[0]
        uName = responseMes[1]
        bName = responseMes[2]
        mCon = responseMes[3]

        # checking the validation conditions
        invalidCredentials = False
        if uName == '':
            invalidCredentials= True
        invalidBoardName = False
        if bName == '':
            invalidBoardName = True

        if status == "ACCEPT": # in case of ACCEPT, server already accepted and validated
            print uName + " added the message " + mCon + " on " +bName + " Message Board!"
        else:
            # in case of REJECT we need to determine the reason of rejection
            if invalidCredentials and invalidBoardName:
                # both are invalid
                print "Error: invalid username/password and board name"
            elif invalidCredentials:
                # only username/password invalid
                print "Error: invalid username/password"
            elif invalidBoardName:
                # only boardname is invalid
                print "Error: invalid board name"


    # list messages on a message board
    elif command == "4":

        user = raw_input("username:")
        passwd = raw_input("pasword:")
        mbsName = raw_input("board name:")

        requestMsg = "LIST:MESSAGES:" + user + ":" + passwd + ":" + mbsName # create LIST:MESSAGES command
        clientSocket.sendto(requestMsg, (MBS_ADDRESS, MBS_PORT))            # send
        response, serverAddress = clientSocket.recvfrom(2048)               # wait for answer

        responseMes = response.split(':')
        status = responseMes[0] # can be REJECT or MESSAGE

        if status == "REJECT":
            # Assuming message is format : REJECT:username:boardname
            # I believe there is a mistake in assignment description at number 8
            # in rejection case server is not sending any message
            uName = responseMes[1]
            bName = responseMes[2]

            # detecting invalid part in the data
            invalidCredentials = False
            if uName == '':
                invalidCredentials = True
            invalidBoardName = False
            if bName == '':
                invalidBoardName = True

            if invalidCredentials and invalidBoardName:
                print "Error: invalid username/password and board name"
            elif invalidCredentials:
                print "Error: invalid username/password"
            elif invalidBoardName:
                print "Error: invalid board name"

        else:
            bName = responseMes[1]
            uName = responseMes[2]
            mNum = int(responseMes[3])
            mCon = responseMes[4]

            if mNum == -1: # if message board is empty first package will be sentinel
                print 'message board is empty'
            else:
                print bName+" messages:"
                print "1. " + uName + ": " + mCon

                # getting all messages 1by1
                # -1 is a sentinel to understand that this is last package sent

                i = 1
                while mNum != -1: # wait new package until get -1 (finish case)
                    i +=1
                    response, serverAddress = clientSocket.recvfrom(2048) # wait for next package
                    responseMes = response.split(':')
                    uName = responseMes[2]
                    mNum = int(responseMes[3])
                    mCon = responseMes[4]
                    if mNum != -1:       # do not print the content of sentinel package
                        print str(i)+". "+ uName + ": " + mCon

    # possible Register another user
    elif command == "5":
        uName = raw_input('username:')
        passwd = raw_input('password:')

        regMes = "REG:" + uName + ":" + passwd  # first operation is by default registration
        clientSocket.sendto(regMes, (MBS_ADDRESS, MBS_PORT))  # send REG command

        response, serverAddress = clientSocket.recvfrom(2048)  # wait response
        responseMes = response.split(':')  # split response elements into array

        if responseMes[0] == 'ACCEPT':
            print 'Successful user registration: ' + responseMes[1]  # Success
        else:
            print 'Rejected user registration: ' + responseMes[1]  # Failure

    elif command == "0":    # exit
        exit(1)
    else:        # invalid choice from user
        print 'Please choose a valid command'

clientSocket.close()  # close socket


