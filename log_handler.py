__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Functions handling Logs
//
//  author    Luca Petricca
//
//  date      29.09.2015
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

import os, sys, logging
from logging.handlers import RotatingFileHandler

#####################################################################################
#############################   LOG DEFINITIONS   ##################################
#####################################################################################

CONSOLE_LOG=True                                                           #print LOGS also in the console
SERVER_LOG=False                                                           #Send LOGS to our SERVERS: The URL is SET in Storedloghandler file
LINUX_PATH="/usr/local/broentech/logs/"

if sys.platform=='win32':
    LOG_FILE = os.path.dirname(os.path.abspath(__file__))+"/broentech.log"  #In windows it save the log in the same folder of the main..
    LOG_LEVEL = logging.INFO             # We log from INFO Level
else:
    if not os.path.exists(LINUX_PATH):
        os.makedirs(LINUX_PATH)
    LOG_FILE = LINUX_PATH+"broentech.log"                   #this is the default path for non-windows based System
    LOG_LEVEL = logging.INFO

############################ END of DEFINITIONS #######################################################

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    formatter=logging.Formatter('%(asctime)s %(name)-10s %(levelname)-10s %(threadName)-20s %(message)-s', datefmt='%d-%m-%Y %H:%M:%S')
    if CONSOLE_LOG:
        logging.getLogger().addHandler(logging.StreamHandler())
    handler = RotatingFileHandler(LOG_FILE, maxBytes=200000, backupCount=1) #create max 2 files of 200kbytes each
    handler.setFormatter(formatter)
    handler.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return


##########################  LOG API #########################

def DBG(inf):
    logging.debug(sys._getframe(1).f_code.co_name+'(): '+inf)

def INFO(inf):
    logging.info(sys._getframe(1).f_code.co_name+'(): '+inf)

def WARN(inf):
    logging.warning(sys._getframe(1).f_code.co_name+'(): '+inf)

def ERR(inf):
    logging.error(sys._getframe(1).f_code.co_name+'(): '+inf)

def CRITICAL(inf):
    logging.critical(sys._getframe(1).f_code.co_name+'(): '+inf)

############################ LOG TEST FUNCTION ###############################

if __name__ == "__main__":

    def log_test():
        print  "-------------------------------------------------------"
        print "Welcome to Ask4Cluster Gateway Log() Test"
        print "Copyright Broentech Solutions AS"
        print "For info contact Lucap@Broentech.no"
        print "-------------------------------------------------------"
        print "Generating some entries in the log file :" + LOG_FILE
        setup_logger()
        INFO("Welcome to Ask4Cluster Gateway Log() Test")
        DBG("This is a DEBUG entry") #This is not stored in the file because level set to Info
        INFO("This is a INFO entry")
        WARN("This is a WARNING entry")
        ERR("This is a ERROR entry")
        CRITICAL("This is a CRITICAL entry")
        INFO("Test PASSED!")

    log_test()