def processSpecialCmd(funcName, clientSocket, inMsgLst):
    rspStr = 'done'

    if funcName != 'dummy':
        return ' Invalid funcName {}'.format(funcName)

    return rspStr
