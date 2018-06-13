# Cemal Turkoglu - 150140719
#
# Message Board Server Application
# UDP Communication

from socket import *

MBS_PORT = 12345

registeredUsers = dict()                        # To keep track of users in the system
messageBoards = dict()                          # To keep track of message boards in the system
                                                # messageBoards is a dictionary of dictionary data structure
                                                # format is as follows
                                                # messageBoards:{messageboard:{message,user,..},..}
                                                # message and the user who addes the message is saved

serverSocket = socket(AF_INET,SOCK_DGRAM)       # Create a server socket
serverSocket.bind(('',MBS_PORT))                # bind the host to the port

print 'MBS Started'
while True:
    message,clientAddress = serverSocket.recvfrom(2048)     # wait a request from any client
    recievedMes = message.split(':')    # split the message

    # Registration of new user
    if recievedMes[0] == "REG":
        username = recievedMes[1]
        password = recievedMes[2]
        print 'Registration request arrived from user '+username
        # if the username is already in use
        if username in registeredUsers:
            serverSocket.sendto("REJECT:"+username, clientAddress)  # Failure
            print 'Rejected user registration: '+username
        else:
            registeredUsers[username] = password       # Success
            serverSocket.sendto("ACCEPT:" + username, clientAddress)
            print 'Successful user registration: ' + username


    # Creating new message board
    elif recievedMes[0] == "CREATE":
        mbsName = recievedMes[1]
        # if message board name is already in user
        if mbsName in messageBoards:
            serverSocket.sendto("REJECT:" + mbsName, clientAddress) # Failure
            print mbsName+' Message Board could not be created!'
        else:
            messageBoards[mbsName] = dict()     # create an empty dictionary to store messages
            serverSocket.sendto("ACCEPT:" + mbsName, clientAddress) # Success
            print mbsName + ' Message Board is created!'

    # Listing message boards
    elif recievedMes[0] == "LIST" and recievedMes[1] == "BOARDS":
        print "Message board list command recieved"
        responseMsg = "LIST:BOARDS"
        if len(messageBoards) == 0:     # if message board list is empty
            serverSocket.sendto(responseMsg+":", clientAddress)
        else:
            # else add all message boards in message separated by colons
            for mbsName in messageBoards:
                responseMsg += ":"+mbsName
            serverSocket.sendto(responseMsg, clientAddress)


    # Adding new message to a message board
    elif recievedMes[0] == "ADD":
        uName = recievedMes[1]      # parse the message
        uPass = recievedMes[2]
        bName = recievedMes[3]
        mCont = recievedMes[4]
        responseMsg = ""    # empty response

        # checking if credentials and boardname is valid
        invalidCredentials = False
        if uName not in registeredUsers:
            invalidCredentials = True
        else:
            if uPass != registeredUsers[uName]:
                invalidCredentials = True

        invalidBoardName = False
        if bName not in messageBoards:
            invalidBoardName = True

        # creating response message according to validation check above
        if invalidCredentials and invalidBoardName:
            # if both of them are invalid
            responseMsg += "REJECT:::"+mCont
            print  "Error: invalid username/password and board name"

        elif invalidCredentials:
            # only username/password is invalid
            responseMsg += "REJECT::"+bName+":"+mCont
            print  "Error: invalid username/password"

        elif invalidBoardName:
            # only boardname is invalid
            responseMsg += "REJECT:"+uName+"::"+mCont
            print  "Error: invalid board name"

        else:
            # username/password and boardname are valid
            # we keep the data as {message, username}
            # username is the user who added the message
            messageBoards[bName][mCont] = uName
            # tempMes = {mCont:uName}
            #messageBoards[bName] = tempMes
            print messageBoards
            responseMsg += "ACCEPT:"+uName+":"+bName+":"+mCont  # Success
            print uName + " added the message " + mCont + " on " + bName + " Message Board!"

        serverSocket.sendto(responseMsg, clientAddress)

    # Listing messages in a message board
    elif recievedMes[0] == "LIST" and recievedMes[1] == "MESSAGES":
        uName = recievedMes[2]
        uPass = recievedMes[3]
        bName = recievedMes[4]
        responseMsg = ""        # empty response, to fill

        # checking if credentials and boardname is valid
        invalidCredentials = False
        if uName not in registeredUsers:
            invalidCredentials = True
        else:
            if uPass != registeredUsers[uName]:
                invalidCredentials = True

        invalidBoardName = False
        if bName not in messageBoards:
            invalidBoardName = True

        # creating response message according to validation check above
        # Assuming message is format : REJECT:username:boardname
        # I believe there is a mistake in assignment description at number 8
        # in rejection case server is not sending any message
        if invalidCredentials and invalidBoardName:
            # if both of them are invalid
            responseMsg += "REJECT::"       # fill the response message
            print  "Error: invalid username/password and board name"
            serverSocket.sendto(responseMsg, clientAddress)     # send response

        elif invalidCredentials:
            # only username/password is invalid
            responseMsg += "REJECT::"+bName
            print  "Error: invalid username/password"
            serverSocket.sendto(responseMsg, clientAddress)

        elif invalidBoardName:
            # only boardname is invalid
            responseMsg += "REJECT:"+uName+":"
            print  "Error: invalid board name"
            serverSocket.sendto(responseMsg, clientAddress)

        else:
            # Success case => ACCEPT
            i = 1
            if len(messageBoards[bName]) == 0:
                # if message board is empty
                responseMsg = "MESSAGE:" + bName + ":" + uName + ":-1:"  # send sentinel to finish connection
                serverSocket.sendto(responseMsg, clientAddress)

            for m,u in messageBoards[bName].items():
                # traverse the messages in a message board
                # m => message
                # u => user who added the message
                responseMsg = "MESSAGE:"+bName+":"+u+":"+str(i)+":"+m
                serverSocket.sendto(responseMsg, clientAddress)
                i+=1

            # send sentinel to say messages are finished and no more package will be sent
            responseMsg = "MESSAGE:" + bName + ":" + uName + ":-1:"
            serverSocket.sendto(responseMsg, clientAddress)