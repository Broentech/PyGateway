__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Stored JSON handler Functions
//
//  author    Luca Petricca
//
//  date      22.09.2015
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


import time, os, requests
import datahandler, loginhandler
import utility, log_handler
import storedloghandler
from requests.auth import HTTPBasicAuth

#main loop of thread2 This also sent the stored logs file
def handle_storedjson(file, sleeptime):
    while utility.CONTINUE_RUNNING:      #continue_running is set to false from the sig_int handler..
        try:
            for i in range(datahandler.NumStoredjson,0, -1):
                if os.path.isfile(file+'.rot'+str(i)):      #lets loop and send all the stored files
                    send_storedjason(file+'.rot'+str(i))
            send_storedjason(file)                          #finally we also send the current file...
            if log_handler.SERVER_LOG:   #we send the logs only if is set the relative variable
                    if storedloghandler.send_log()==0:
                        log_handler.INFO("Log File Sent and locally removed!")
            time.sleep(sleeptime)
        except Exception as e:
            log_handler.WARN("Problem while sending data or logs:" +str(e))
            time.sleep(sleeptime)

#check if there is a stored json file...if yes try to sent it
def send_storedjason(file):
    if os.path.isfile(file) and os.path.getsize(file) > 0:
        try:
            datahandler.jsonmutex.acquire()          #this file can also be written from the other thread... we need to lock it
            with open(file,mode='r+')as f:
                jtext=f.read()+"]}"
                f.close()
                if simplehttpsend(jtext)==0:          #there is a file...send it and if ok than delete it
                    os.remove(file)
                    log_handler.DBG("JSON file SUCCESSFULLY sent!"+file)
                    return 0
                else:
                    log_handler.INFO("JSON_FILE send FAILED!" +file)
        except:
            log_handler.WARN("Unable to get MUTEX on file: "+ file)
            return -1
        finally:
            datahandler.jsonmutex.release()
    else:
        log_handler.DBG("JSON File was not there...nothing to send!")

    return -1


#POST the data on the BACKEND..do not do anything if you the server respond 401
def simplehttpsend(JSON):
    #return -1 #used for TESTING and simulate failure.. TO BE REMOVED
    try:
        timeoutlen= 10+int(len(JSON)/100000)
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(datahandler.POSTURL, headers=headers,  data=JSON, auth=HTTPBasicAuth(loginhandler.MY_MAC, loginhandler.MY_TOKEN), verify=loginhandler.certpath, timeout=timeoutlen)
        if resp.status_code==200:
            log_handler.DBG("Json Successfully sent!")
            return 0
        elif resp.status_code==400:
            log_handler.ERR("The Json Was wrong...I will delete it.. next log line is not correct.")
            return 0
        elif resp.status_code==413:
            log_handler.ERR("The Json was TOO BIG to be handled by the server and will be lost...reduce the stored file size or reduce the sleeping time for the thread!")
            return 0 #we return 0 so we delete the data... the data will be lost
        else:
            log_handler.WARN("JSON failed to send: "+ str(resp.status_code))
            return -1
    except Exception as e:
        log_handler.WARN("File Send Failed" +str(e))
        return -1 #Simulate failure! --->0 Success, -1= failure
####################################################################################
################################# Testing Functions! ###############################
####################################################################################
if __name__ == "__main__":
    send_storedjason(os.path.dirname(os.path.abspath(__file__))+"\jsondata")