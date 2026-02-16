def tmpWorker(clientSocket,cmd,optArgs):
    if optArgs: pass
    clientSocket.send(cmd.encode())
    return 0

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
