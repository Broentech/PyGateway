#!/usr/bin/python
__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Broentech Gateway Test
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

import log_handler
import threading, time
import loginhandler, serialhandler
import datahandler
import stored_jsonhandler
import os,sys, signal
import utility

#####################################################################################
#############################   MAIN DEFINITIONS   ##################################
#####################################################################################
DATA_IN_LOCAL_FOLDER=True                       #if true: look rowdata.brn aa file in the same folder of this main.py file
DATA_SRC_DIR="/usr/local/broentech/src/"
if sys.platform=='win32' or DATA_IN_LOCAL_FOLDER:
    DATA_SRC_DIR=os.path.dirname(os.path.abspath(__file__))+"/"
rowfilepath=DATA_SRC_DIR+"rawdata.brn"        #Define the file path of the original Datafile
sleeptime=5                                  #Define the how often (seconds) it check the presence of Datafile

JSON_IN_LOCAL_FOLDER=True                       #if true: store json files (in case of no internet connection) in the same folder of main.py file
JSON_SRC_DIR="/usr/local/broentech/src/"
if sys.platform=='win32' or JSON_IN_LOCAL_FOLDER:
    JSON_SRC_DIR=os.path.dirname(os.path.abspath(__file__))+"/"
filenoconnection=JSON_SRC_DIR+"jsondata"     #Define where to locally store the json object in case of no internet connection
retrytime=30                                 #Define how often (seconds) will try to re sent the stored json data in case that there was no internect connection

#################### MAIN APPLICATION ENTRY POINT #####################################

if __name__ == "__main__":

    def main_run():
        log_handler.setup_logger()      #Initialize logging module
        log_handler.INFO("Broentech Gateway App. started on device running: "+ sys.platform + " With MAC address: "+ loginhandler.mymac())
        signal.signal(signal.SIGINT, utility.sigint_handler)
        log_handler.INFO("LOGS file are stored in: "+ log_handler.LOG_FILE)
        log_handler.INFO("Folder where I am storing for rowdata.brn file is: "+ rowfilepath)
        log_handler.INFO("Initializing Position...This may take few seconds")
        utility.init_position()
        log_handler.INFO("Loading Token...")
        #check and create the two folders if needed...
        if not os.path.exists(DATA_SRC_DIR):
            os.makedirs(DATA_SRC_DIR)
        if not os.path.exists(JSON_SRC_DIR):
            os.makedirs(JSON_SRC_DIR)

        loginhandler.init_tokenhandler()  #initializate my_token and my_mac global variables
        t1=threading.Thread(name="GTW_SerialHandler",target =serialhandler.read, args=[rowfilepath])
        t2=threading.Thread(name="GTW_Jsonhandler",target =datahandler.datahandler, args=[rowfilepath, sleeptime, filenoconnection])
        t3=threading.Thread(name="GTW_Sendhandler",target =stored_jsonhandler.handle_storedjson,args=[filenoconnection, retrytime])
        t1.start()
        t2.start()
        t3.start()
        while utility.CONTINUE_RUNNING: #THIS WHILE COULD BE REMOVED in production...however the program will not hear SIGNINT signal anymore
            time.sleep(1)
            if not (t1.is_alive()and t2.is_alive() and t3.is_alive()): #if one of the thread dies exit close the program... the script will respawn it
                log_handler.CRITICAL("one of the Thread died without any apparent reason.. i will now close the program.. status of t1, t2, t3 is: " +str(t1.is_alive())+  str(t2.is_alive()) + str(t3.is_alive()))
                exit()
        t1.join()
        t2.join()
        t3.join()

    main_run()