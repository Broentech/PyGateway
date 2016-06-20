__author__ = 'Luca'
'''/////////////////////////////////////////////////////////////////////////////
//  brief     Serial handler Functions
//
//  author    Luca Petricca
//
//  date      22.10.2015
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

import sys, os ,log_handler
import glob, datahandler, struct
import serial, utility,time

# List all the serial ports avaialable or rise exception
def serial_ports(): #adapted from stackoverlow
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

#Try to find port and datagram... if it finds it it hook on the port
def autodetect(filepath): #try to autodetect the presence of a datagram in one of the available ports
    port=serial_ports() #Get the list of serialports
    if len(port)==0:    #if there are no ports
        return -1
    for i in port:
        testport= serial.Serial(i,baudrate=19200,parity='N', bytesize=8,stopbits=1,timeout=3)
        data=str(testport.read(63))
        for k, c in enumerate(data):
            if c=='$':
                data=data[k:k+32]
                break
        log_handler.INFO("Looking for datagram in ports: " + i)
        if checkdatagram(data):
            log_handler.INFO("Useful data found! "+ str(data)+ " Serial port hooked on: " +  i)
            storedata(data, filepath)
            testport.close()
            return i
        else:
            testport.close()
    return -1

#check if a datagram makes sense.by checking the first two ($A or $V) and the last two bytes (00)
def checkdatagram(data):
    if ((len(str(data)))==32):
        return data[0]=='$' and (data[1]=='A' or data[1]=='V') and data[30]=='0' and data[31]=='0'
    else:
        return False

#FIND the PORT with DATA
def getdataport(filepath):
    port=-1
    while port ==-1:
        port=autodetect(filepath)
    return port

#ONCE you hooked the serial port, use this function to retrive data
def givemedata(porta, filepath):
        try:
            while porta.inWaiting()<32:
                pass
            data=porta.read(32)
            if checkdatagram(str(data)):
                return data
            else:
                log_handler.ERR("Datagram check failed!")
                return -1
        except:
            porta.close()
            log_handler.ERR("Failed to read data from the port!")
            autodetect(filepath)
            return -1

#store the sensor data in a dataraw file
def storedata(data, filepath):
    try:
        datahandler.rawmutex.acquire()
        timestamp=int(1000*time.time())
        if (not os.path.isfile(filepath)) or os.path.getsize(filepath) == 0:
            with open(filepath,mode='w') as f:
                f.write(str(data+str(struct.pack('=q',timestamp))+"\n"))
                f.close()
        else:
            with open(filepath,mode='a') as f:
                f.write(str(data+str(struct.pack('q',timestamp))+"\n"))
                #print sys.getsizeof(data+str(struct.pack('q',timestamp))+"\n")

                f.close()
    except:
        log_handler.WARN("Failed to acquire the MUTEX Lock or to write data to: "+ filepath)
    finally:
        datahandler.rawmutex.release()

def allign(myport, rawfilepath):
    while myport.read() !='$':      #reallign the readings...lets find the first byte of the datagram
        pass
    first='$'+myport.read(31)
    if checkdatagram(first):
        storedata(first, rawfilepath)
        return 0
    else:
        return -1

#Main thread entry point... read data from serial and store it in the file
def read(rawfilepath):
    port= getdataport(rawfilepath)
    myport= serial.Serial(port,baudrate=19200,parity='N', bytesize=8,stopbits=1,timeout=3)
    while allign(myport, rawfilepath)==-1:      #Loop untill we do not get the right allignment
        pass
    while utility.CONTINUE_RUNNING:
        data=givemedata(myport, rawfilepath)
        if checkdatagram(data):
            storedata(data, rawfilepath)
        else:
            log_handler.ERR("Datagram received on serial was wrong.. i will now re-run the autodetection of serial port")
            myport.close()
            port=getdataport(rawfilepath)
            myport= serial.Serial(port,baudrate=9600,parity='N', bytesize=8,stopbits=1,timeout=3)
            while allign(myport, rawfilepath)==-1:
                pass


