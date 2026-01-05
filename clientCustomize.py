def tmpWorker(clientSocket,cmd,optArgs):
    clientSocket.send(cmd.encode())
    return

#############################################################################
def processSpecialCmd(funcName, clientSocket, inMsgLst):

    if funcName != 'tmp':
        print(' Invalid funcName {}'.format(funcName))
        return

    #if len(inMsgLst) < 2:
    #    print(' ERROR: Too few command line parms.')
    #    return

    cmd      = inMsgLst[0].strip() # up
    optArgs  = inMsgLst[1:]

    tmpWorker(clientSocket,cmd,optArgs)

    return
