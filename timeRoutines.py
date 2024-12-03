'''
Simple module that contains only one function that returns the date and time.
It can be called from the program's main prompt (gt command).
It's also called from the function rp (Run (active) Profile).

rp is in file runActProfRtns.py and it is an ifinite loop that continually
reads the date/time and compares it the the profile to see if a relay should
be opened or closed ... rp is the whole point of this project ...

The infinite can be exited with the sp (Stop Profile) command.
'''

import datetime as dt

def getTimeDate( prnEn = True ):
    now = dt.datetime.now()

    dowStrLst = ['Monday', 'Tuesday', 'Wednesday',
                 'Thursday', 'Friday', 'Saturday', 'Sunday']

    year   = now.year
    month  = now.month
    day    = now.day
    hour   = now.hour
    minute = now.minute
    second = now.second
    dowNum = now.weekday() # Monday is 0.
    dowStr = dowStrLst[dowNum]

    rspStr  = ' {}\n'.format(now)
    rspStr += ' year   {:4}'.format(   year   )
    rspStr += ' month  {:4}'.format(   month  )
    rspStr += ' day    {:4}\n'.format( day    )
    rspStr += ' hour   {:4}'.format(   hour   )
    rspStr += ' minute {:4}'.format(   minute )
    rspStr += ' second {:4}\n'.format( second )
    rspStr += ' dow    {:4} ({})'.format( dowNum, dowStr )

    if prnEn:
        pass
        #print(rspStr)

    rtnDict = {'year':   year,   'month':  month,  'day':   day,
               'hour':   hour,   'minute': minute, 'second':second,
               'dowNum': dowNum, 'dowStr': dowStr,
               'now':    now}

    return [rspStr, rtnDict]
#############################################################################
