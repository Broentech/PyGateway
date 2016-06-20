__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Stored LOGs handler Functions
//
//  author    Luca Petricca
//
//  date      10.10.2015
//
//  par       Copyright: The MIT License (MIT)
//Copyright (c) 2016 Broentech Solutions A.S., Norway
//
//Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
//documentation files (the "Software"), to deal in the Software without restriction, including without limitation
//the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
//and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
//
//The above copyright notice and this permission notice shall be included in all copies or substantial portions of
//the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
//WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
//COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
//OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//
//h-////////////////////////////////////////////////////////////////////////// '''

import threading, log_handler, loginhandler
import os , requests, json
from requests.auth import HTTPBasicAuth
myloglock = threading.Lock()

#####################################################################################
#############################   HTTP DEFINITIONS   ##################################
#####################################################################################
POSTLOGURLS='https://talaiot.io/loglanding'               #URL of the LOG server POST API"
####################################################################################



#Send the log in json format.. if it fails: it leaves the log file as it is...if succeed: delete the log file
def send_log():
    if os.path.isfile(log_handler.LOG_FILE+".1") and os.path.getsize(log_handler.LOG_FILE+".1") > 0:  #we only sent the last log this is why .1
        try:
            myloglock.acquire()
            myje=logtojson(log_handler.LOG_FILE+".1")

            ret= httplogsent(myje) # if success return 0. otherwise -1
            if ret==0:
                os.remove(log_handler.LOG_FILE+".1")
                return 0
            else:
                log_handler.WARN("Failed to sent log file")
                return -1
        except Exception as e:
            log_handler.WARN("Problem while sending log files: "+ str(e))
            return -1
        finally:
            myloglock.release()

    else:
        log_handler.INFO("No Log to Sent")
        return -1

#POST the LOGs on the server
def httplogsent(logjson):
#return -1 #used for TESTING and simulate failure.. TO BE REMOVED
    try:
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(POSTLOGURLS, data=logjson, headers=headers, auth=HTTPBasicAuth(loginhandler.MY_MAC, loginhandler.MY_TOKEN),)
        if resp.status_code==200:
            log_handler.INFO("LOGs Successfully sent!")
            return 0
        else:
            log_handler.WARN("LOGs failed to send: "+ str(resp.status_code))
            return -1
    except Exception as e:
        log_handler.WARN("LOGs Send Failed" +str(e))
        return -1 #Simulate failure! --->0 Success, -1= failure

#almost same function used in sensedatahandler... anyway, i reimplemented it here
def logtojson(logfile):
    jsonlogtemp=""
    with open(logfile) as f:
        for i in f:
             jsonlogtemp+=str(logrowtojson(i))
        jsonlog='{"log_array": [ \n' + jsonlogtemp +"]}"
        return jsonlog

#Transform a log row to json
def logrowtojson(row):
    try:
        Date, Time, User ,Level, Thread , Function, Info=row.replace("/n","").split(None,6)
        temp=({"Date":Date, "Time":Time, "User":User, "Level":Level,"Thread":Thread, "Function":Function, "Info":Info})
        temp2={"log":temp}
        toreturn=json.dumps(temp2, separators=(",",":"), indent=4)
        return toreturn
    except Exception as e:
        log_handler.ERR("Failed to convert LOG row to JSON: "+str(e))
        return ""

################################# Testing Functions! ###############################
if __name__ == "__main__":
    pass