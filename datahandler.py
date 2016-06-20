__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Data handler Functions
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
#Python import
import json ,time, os, threading, requests, struct
from requests.auth import HTTPBasicAuth
import logging, sys
#My import
import utility, log_handler , loginhandler

##################################   DEFINITIONS   ##################################
#####################################################################################
POSTURL='https://talaiot.io:3000/datalanding/v1'  #URL of the server POST API
NumStoredjson = 9   #Maximum numbers of stored json files
MaxSizeStoredJson = 100000 #Maximum size of each stored json file 200kb
####################################################################################

#We do not want that requests spam us with logs..we only want the critical ones
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.CRITICAL)
requests.packages.urllib3.disable_warnings()    #disable warnings for untrusted certificate! maybe you want to log it?(logging.captureWarnings(True))

global rawmutex, jsonmutex
rawmutex = threading.Lock() #Mutex for the raw sensor data file
jsonmutex = threading.Lock()#Mutex for the json data file

#parse the header of the row and call the right json parser
def rowtojson(data):
    try:
        #firstly we need to parse the header (fff is not reliable because we do not know what is the real type yet)
        complete=struct.unpack("=ccccccccccccccccfffccccqc", data)
        if "".join(complete[8:12])=="DFLO" or "".join(complete[8:12])=="AFLO":
            return jsfloat(complete)    # return the correct json format
        elif "".join(complete[8:12])=="INTE" or  "".join(complete[8:12])=="AINT": #we need to reunpack complete with i instead of f because is a int
            complete=struct.unpack("=cccccccccccccccciiiccccqc", data)
            return jsint(complete)
        elif "".join(complete[8:12])=="CHAR":
            complete=struct.unpack("=ccccccccccccccccccccccccccccccccqc", data)
            return jschar(complete)
        elif "".join(complete[8:12])=="SHORT":
            complete=struct.unpack("=cccccccccccccccchhhhhhccccqc", data)
            return jsshort(complete)
        else:
            log_handler.ERR("Failed to parse a row")
            return -1
    except Exception as e:
        print e
        return -1


def jsfloat(data):  #convert the float row to json
    try:
        temp=[]
        nsens=4-"".join(data[12:16]).count("-")  #find how many sensor data are ecoded
        for i in range(nsens):
            temp.append({"SensorNr":"".join(data[0:4]),"".join(data[4:8])+data[12+i]:data[16+i], "Date": data[23], "latitude": str(utility.latitude),"longitude":str(utility.longitude) })
        temp2={"data":temp}
        myjason=json.dumps(temp2, separators=(",",":"), indent=4)
        return myjason
    except:
        log_handler.ERR("Failed to convert a row from float datagram")
        return -1


def jsint(data):    #convert the int row to json
    try:
        temp=[]
        nsens=4-"".join(data[12:16]).count("-")  #find how many sensor data are ecoded
        for i in range(nsens):
            temp.append({"SensorNr":"".join(data[0:4]),"".join(data[4:8])+data[12+i]:data[16+i], "Date": data[23], "latitude": utility.latitude ,"longitude":utility.longitude })
        temp2={"data":temp}
        myjason=json.dumps(temp2, separators=(",",":"), indent=4)
        return myjason
    except:
        log_handler.ERR("Failed to convert a row from integer datagram")
        return -1

def jschar(data): #in case we sent char, we generate a json format as string, without divinding it
    try:
        temp=[]
        temp.append({"SensorNr":"".join(data[0:4]),"".join(data[4:8])+"".join(data[12:16]):"".join(data[16:28]), "Date":data[32], "latitude": utility.latitude ,"longitude":utility.longitude })
        temp2={"data":temp}
        myjason=json.dumps(temp2, separators=(",",":"), indent=4)
        return myjason
    except:
        log_handler.ERR("Failed to convert a row from char datagram")
        return -1

def jsshort(data): #Despite there are 6 fields of possible data, only the first fours are considered
    try:
        temp=[]
        nsens=4-"".join(data[12:16]).count("-")  #find how many sensor data are ecoded
        for i in range(nsens):
            temp.append({"SensorNr":"".join(data[0:4]),"".join(data[4:8])+data[12+i]:data[16+i], "Date": data[26], "latitude": utility.latitude ,"longitude":utility.longitude })
        temp2={"data":temp}
        myjason=json.dumps(temp2, separators=(",",":"), indent=4)
        return myjason
    except:
        log_handler.ERR("Failed to convert a row from short datagram")
        return -1

def datatojson(storedfile): #convert the data in the stored file into json format
    json=""
    with open(storedfile) as myfile:
        i=myfile.readline()
        if sys.getsizeof(i)<41:
            i+=myfile.readline()
        while i:
        #for i in myfile:    #for each row parse and append to json object
            temp=rowtojson(i)
            if temp!=-1:
                json+=temp+","
            i=myfile.readline()
            if sys.getsizeof(i)<41:
                i+=myfile.readline()
    return json


#POST the data on the BACKEND..also delete the token in case of server respond 401
def httpsend(JSON):
    #return -1 #used for TESTING and simulate failure.. TO BE REMOVED
    try:
        if JSON=='{ "dataarray": [ \n]} \n':  #return 0 so we do not append empty json to the json file
            return 0
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(POSTURL, headers=headers,  data=JSON, auth=HTTPBasicAuth(loginhandler.MY_MAC, loginhandler.MY_TOKEN), verify=loginhandler.certpath, timeout=10)
        if resp.status_code==200:
            log_handler.DBG("Json Successfully sent!")
            return 0
        elif resp.status_code==400:
            log_handler.INFO("The Json was wrongly formatted... probably empty?")
            return 0 #we return 0 so we do not append a wrong json to the json file
        elif resp.status_code==413:
            log_handler.ERR("The Json was TOO BIG to be handled by the server and will be lost...reduce the stored file size or reduce the sleeping time for the thread!")
            return 0 #we return 0 so we delete the data... the data will be lost
        elif resp.status_code==401:
            os.remove(loginhandler.TOKEN_FILE)
            log_handler.ERR("GOT UNAUTHORIZED BACK... I WILL DELETE THE TOKEN ADN TRY TO REFETCH IT FROM ONLINE")
            loginhandler.init_tokenhandler()
            return -1
        else:
            log_handler.WARN("JSON failed to send: "+ str(resp.status_code))
            return -1
    except Exception as e:
        log_handler.WARN("File Send Failed" +str(e))
        return -1 #Simulate failure! --->0 Success, -1= failure

#store a json on the harddrive...if it doensnt exist it will create a new one
def storejson(data, datafile):
    doRollOver(data, datafile)
    try:
        jsonmutex.acquire()
        if (not os.path.isfile(datafile)) or os.path.getsize(datafile) == 0:
            with open(datafile,mode='w') as f:
                f.write('{ "datacollection": [ \n' + data)
                f.close()
                log_handler.INFO("Successfully stored JSON formatted data in a NEW file called: "+ datafile)

        else:
            with open(datafile,mode='a') as f:
                f.write(","+data)
                f.close()
                log_handler.INFO("Successfully stored JSON formatted data in a EXISTING file called: "+ datafile)
    except:
        log_handler.WARN("Failed to acquire the MUTEX Lock on :"+ datafile)
    finally:
        jsonmutex.release()

#This function check if the json file is larger than maxsize...if it is it will rename it as .01 and the .01 as .02. etc
def doRollOver(data, datafile):
    try:
        if not os.path.isfile(datafile) or os.path.getsize(datafile)<MaxSizeStoredJson: #if the file does not exist or size is less than maxbyte than retur
            return
        else:
            if  os.path.isfile(datafile+'.rot'+str(NumStoredjson)):
                os.remove(datafile+'.rot'+str(NumStoredjson)) #remove the last in queue
            for i in range(NumStoredjson-1,0, -1):
                oldname=datafile+'.rot'+str(i)
                newname=datafile+'.rot'+str(i+1)
                if os.path.isfile(oldname):
                    os.rename(oldname, newname)
            #lets process the final file... we need mutex
            with jsonmutex: #this is acquired when entered and released when exit
                os.rename(datafile, oldname)    #when it exit the loop, oldname is datafilename.rot1
            return
    except Exception as e:
        print e


#main loop in the first thread
def datahandler(datafile, sleeptime,filenoconnection ):
    while utility.CONTINUE_RUNNING:                                              #CONTINUE_RUNNING is set false by SIGINT signal handler
        try:
            if os.path.isfile(datafile) and os.path.getsize(datafile) > 0:           #if there is a file and is larger than 0 byte
                data='{ "dataarray": [ \n' + datatojson(datafile)[:-1] +"]} \n"
                if httpsend(data)!=0:                                                # Try to send the stored data as jason format... if sendhttpdata fails
                    log_handler.WARN("Unable to send data. Storing it in local file")
                    storejson(data, filenoconnection)                                # than store jason formated version
                os.remove(datafile)                                             # we can delete the file here, since we stored the json formatted version of it
                log_handler.DBG("Data file rowdata.brn removed")
            else:
                log_handler.INFO("Data file NOT found in :"+ str(datafile) +". Trying again in: " +str(sleeptime)+ " seconds")
        except Exception as e:
            log_handler.ERR("An exception happed while i was deleting or storing datafile!"+ str(e))
        time.sleep(sleeptime)


############################ SENSE DATAHANDLER FUNCTION ###############################
if __name__ == "__main__":
    pass


#Main Entry point for the datareading thread