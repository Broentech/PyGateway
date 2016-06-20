__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     utility Functions: position, shoutdown handler
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


#this functions initialize the gateway position based on the ip.. it can be extended by reading gps position
import requests
import logging
from bs4 import BeautifulSoup
import log_handler

import signal

#We do not want that requests spam us with logs..we only want the critical ones
requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.CRITICAL)

latitude="N/A"
longitude="N/A"
def init_position():
    try:
        myposition=requests.get("http://freegeoip.net/xml/", timeout=10)
        soup = BeautifulSoup(myposition.text, 'html.parser')
        global latitude
        global longitude
        latitude=soup.latitude.text
        longitude=soup.longitude.text
        log_handler.INFO("Position Successfully Initialized..")
    except:
        log_handler.WARN("Unable to initialize/find my position")
        pass

#this functions shout down the threads grafully if signint is called
CONTINUE_RUNNING=True
'''NOTE:If the write is interrupted is entirely unrelated to the 'with-open' statement.
unfortunately the only thing the 'with' statement does is that it ensures the file will be closed if
the flow of control leaves the block. Signals(sigint etc) are not delivered to other threads,
just the main thread,so the write shouldn't be interrupted. Even so, the only way to protect against partial write is to
use a temp file and then rename it...may be implemented if file corruption start to be a problem'''

def sigint_handler(signum, frame):
    global CONTINUE_RUNNING
    log_handler.CRITICAL( "SIGINT received!  Shutting down in controlled fashion ...Waiting that the sleeping threads wakes up.. This may take a while")
    #global flag to stop datalogger threads..the thread will stop the next time they will wake up ..
    CONTINUE_RUNNING=False


############################################ TESTING FUNCTION  ##########################################

if __name__ == "__main__":
    print  "-------------------------------------------------------"
    print "Welcome to Broentech Gateway Position() Test"
    print "Copyright Broentech Solutions AS"
    print "For info contact Lucap(at)Broentech.no"
    print "-------------------------------------------------------"
    print "Trying to retrive your position"
    init_position()
    if longitude=="N/A" or latitude=="N/A":
        print "Test Failed. Value for latitude is: " +str(latitude)+" And for Longitude is: "+str(longitude)
    else:
        print "Position Successfully recovered! Latitude is: " +str(latitude)+" and Longitude is: "+str(longitude)