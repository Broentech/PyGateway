__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Token handler Functions
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

import log_handler, utility
import requests, json                     #library for handling http requests
import os , sys                          #library for accessing files on the pc
from uuid import getnode as get_mac #library for returning mac address
import time, logging
from requests.auth import HTTPBasicAuth
#We do not want that requests spam us with logs..we only want the critical ones
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.CRITICAL)
requests.packages.urllib3.disable_warnings()    #disable warnings for untrusted certificate! maybe you want to log it?(logging.captureWarnings(True))

#####################################################################################
#############################   LOGIN DEFINITIONS   #################################
#####################################################################################
STORE_SAME_FOLDER= True                  #This variable when set to true set the path certificate and token to the same as this file
CERTIFICATE_SRC_DIR="/usr/local/broentech/src/"
if sys.platform=='win32' or STORE_SAME_FOLDER:
    CERTIFICATE_SRC_DIR=os.path.dirname(os.path.abspath(__file__))+"/"     #in case of windows based system use current directory as base path
CERT_FILE="broendev.pem"
TOKEN_FILE=CERTIFICATE_SRC_DIR+"tokenfile"
certpath=CERTIFICATE_SRC_DIR+CERT_FILE                    #path of the certificate file

TOKEN_BASE_URL="https://talaiot.io/access/token"  #Base URL for TOKEN Fetching
#############################   END OF DEFINITIONS   #################################


#####################################################################################
#############################   LOGIN FUNCTIONS   ##################################
#####################################################################################

MY_MAC="" #we want to keep the mac and the token always in memory because we use it in all the places!!!
MY_TOKEN= ""

#store a token in a local file called tokenfile
def storetoken(token):
    try:
        with open(TOKEN_FILE,mode='w') as f:
            f.write(token)
            f.close()
            log_handler.INFO("Token fetched and Stored in local file")
            return 0
    except Exception as e:
        log_handler.CRITICAL("Unable to store the token in Local File :" +e)
        log_handler.CRITICAL("You will probably need to REGENERATE a new token online for this device.. The Process now terminates")
        sys.exit(-1)


#retrive a token from a local file called tokenfile..if the file does not exist or is empty return -1
def tokenfromfile():
    if os.path.isfile(TOKEN_FILE) and os.path.getsize(TOKEN_FILE) > 0:
        try:
            with open(TOKEN_FILE,mode='r') as f:
                token=f.read()
                f.close()
                return token

        except:
            log_handler.ERR("Error in Reading the Token file: " +TOKEN_FILE)
    else:
        return -1

#return a HEX version (standard format) of the MAC address and update the MY_MAC global variable
def mymac():
    mac= ':'.join('%02X' % ((get_mac() >> 8*i) & 0xff) for i in reversed(xrange(6)))
    global MY_MAC
    MY_MAC=mac
    return MY_MAC

#Retreive the token from online server
def fetchonlinetoken(mac):
    mypara= {"mac":str(mac)}
    try:
        log_handler.INFO("Requesting token at: "+ TOKEN_BASE_URL)
        myrequest=requests.get(TOKEN_BASE_URL,params=mypara, verify=certpath)
        if myrequest.status_code==200:
            return extracttoken(myrequest)
        elif myrequest.status_code==204:
            log_handler.ERR("Seems that the token has already been fetched but i do not have it! You must regenerate a new one from your portal")
        elif myrequest.status_code==500:
            log_handler.ERR("It seems that the server does't find my mac...Have you correcly added my mac to the portal? My MAC is: " + mac)
        else:
            log_handler.ERR("unable to fetch the token: "+ str(myrequest.status_code) + str(myrequest.content))
    except requests.exceptions.RequestException as e:   # This is the correct syntax
        log_handler.ERR("Unable to fetch online token: " + str(e))
        return -1

#look for a token in the http response text
def extracttoken(myreq):
    try:
        token_json=json.loads(myreq.text)
        token=str(token_json['token'])
        return token
    except:                      #otherwise is some error message
        log_handler.CRITICAL("The server gave wrong formatted token!")
        return -1

#this function initialize the MYTOKEN and MYMAC Variable... it loops forever until it has a valid token retrived
def init_tokenhandler():
    mymac()                 #this function initialize the global variable... probably has already been called... if not better to recall it
    token=tokenfromfile()   #check if the token is already stored and if yes fetch it
    if token==-1:           #if is not in memory fetch it online...
        log_handler.WARN("The token was not stored in local file! Trying to retrive it online")
        while (token==-1 or token is None) and os.path.isfile(TOKEN_FILE)==False and utility.CONTINUE_RUNNING: #loop untill you do not get it, and if you get it store it in the file
            token= fetchonlinetoken(MY_MAC)
            if token==-1 or token is None:
                log_handler.WARN("Fetching online token Failed.. Retrying in 30 seconds")
                time.sleep(30)
            else:
                storetoken(token)
    global MY_TOKEN  #we update the global variable
    MY_TOKEN=token
    log_handler.INFO("Token Loaded Correctly!")

####################################################################################
################################# Testing Functions! ###############################
####################################################################################

if __name__ == "__main__":

#simulate a login in the server in order to check credentials
    def login():
        try:
            myrequest=requests.get('https://talaiot.io/access', auth=HTTPBasicAuth(mymac(), MY_TOKEN), verify=certpath)
            print "Getting: ", myrequest.url
            print "Server respond: " + str(myrequest.status_code)
            return myrequest

        except requests.exceptions.RequestException as excep:
            print("Something is wrong...maybe the server down or no internet connection..? here more info: " +str(excep))
            return -1
        return -1

    def test_login():
        print  "-------------------------------------------------------"
        print "Welcome to Broentech Gateway Login() Test Environment"
        print "Copyright Broentech Solutions AS"
        print "For info contact Lucap@Broentech.no"
        print "-------------------------------------------------------"
        print "Your MAC address is: " + mymac() #this also inizialize the MY_MAC var
        log_handler.setup_logger()      #init the MY_TOKEN var
        print "Retriving token..(if I freeze is probably because I am unable to fetch the token"
        print "from the server! please see the log file for more info): "+ log_handler.LOG_FILE
        init_tokenhandler()
        print "Token retrived is: "+ MY_TOKEN
        print "Testing Login with the retrived token"
        resp=login()
        if resp==-1:
            print("Test Failed!")
        elif resp.status_code==200:
            print("!!Congratulation!! Your login credentials Works Fine!!!")
        elif resp.status_code==401:
            print("It Seems that the token stored locally is wrong or the device was deleted from the server! Have you registered it in the portal?")
            os.remove(TOKEN_FILE)
            print "I Deleted the token file...i will re-try to fetch it from the server"
            init_tokenhandler()
            resp=login()
            if resp.status_code==200:
                print "!!Congratulation!! Your login credentials Works Fine!!!"
            else:
                print "Test Failed...please try again"
        else:
            print("Something was wrong... the server says: " + str(resp.status_code) + str(resp.text) )

    test_login()