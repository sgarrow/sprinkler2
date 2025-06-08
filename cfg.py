
#############################################################################

def getCfgDict():
    requiredKeys = ['myLan', 'myIP', 'myPort', 'myPwd']
    cfgDict = {}
    try:
        with open('cfg.cfg', 'r', encoding='utf-8') as f:
            for line in f:
                if '#' not in line and line.strip():
                    lSplit = line.split()
                    if len(lSplit) >= 2:
                        cfgDict[lSplit[0]] = lSplit[-1]
    except FileNotFoundError:
        return None

    if not all(key in cfgDict for key in requiredKeys):
        return None
    return cfgDict
#############################################################################
