
--------------------------------------------------------------------------
READMEFILE of the PyGateway of Broentech Solutions A.S.
--------------------------------------------------------------------------
Broentech Solutions initial version of the python gateway code. This code read data from the serial interface and send it to Broentech Cloud service.
It is for example purpose only. you are free to reuse and modify it under MIT license.
It consist of three threads: 
1. First thread read and save serial data on the rawdata.brn file. The Datagram sent over the serial must be 32byte long. Read README file section to check the required fields....
2. Second thread read the rawdata.brn file converts it to json and try to send it over https. if it fails it store it as json file.
3. Third Thread read the stored json files and try to send it over the https.
It also include the token fetching functions and the Logger function.
Plase Read ReadMe file for detailed instructions (also include a Q/A section)!

--------------------------------------------------------------------------
Datagrams

By default the software try to read this datagram format from the serial.. you can change and adapt for your purposes by changing data_handler.py file.
The datagram send on the serial must be 32 byte long. The format is: $A01TEMPDFLOT---xxxxxxxxxxxx0000
Here is the bytes meaning:
$A01 ---> Byte[0-3] fist simbol is dollar followed by board ID.. dollar is used for alligment purpose
TEMP-->   Byte[4-7] This is the label of the sensor, can be whatever. 
DFLO -->  Byte[8-11] DFLOT, AINT, SHORT, CHAR... indicate what type of value is encoded later
T--- -->  Byte[12-15]For DFLOA and AINT indicate how many value are encoded.. T--- one value ; TC-- 2 values; TTX- 3 values... is basically the unit of measurement
xxxxxxxxxxxxxx --> Byte[16-27] 12 bytes of real data.. can be 3 int or 3 float or 12 chars (it depends from what was specified on field [8-11])..
0000--> Byte[28-31] -- End of package allignent simbol.

typedef struct Broentech_Package
{
   char boardID[4];    // $V01 $A05 etc                                     | 4 bytes 
   char sensID[4];     // Sensor ID: Temp,  CO_2, Humi                      | 4 bytes 
   char dataType[4];   // Type of the data: INT,DOU,FLO,CHA                 | 4 bytes 
   char dataID[4];     // data labels for the 4 payloads: example: xyz-     | 4 bytes
   float data[3];      // 													| 12 bytes 
   char footer[4];     // END\n												| 4 bytes
} Broentech_Package;   


--------------------------------------------------------------------------
TOKEN: 
Before the software is able to start it needs to fetch the token from our servers (it will then be stored locally on the gateway). This token will be required (together with the MAC address) for autenthication on our servers. 
In order for the gateway to fetch the token from our servers, you need login to our cloud service and add the mac address of the gateway device!


--------------------------------------------------------------------------
More detailed instruction about the code..
Before you start please do the following:
1- in the file log_handler.py SET:
    1.1- CONSOLE_LOG If you set this to false, it will not print anything to the console (only to log files)
    1.2- LINUX_PATH:: This is the path where the app store the LOGS... now set to "/usr/local/broentech/logs/" change it according with your need.
    1.3- Keep SERVER_LOG=False for now because the log server is not implemented yet.
2. in the main.py file SET:
    2.1 DATA_IN_LOCAL_FOLDER=False. If you swith to true it will always look for rawdata.brn in the same folder of main.
    2.2 Set DATA_SRC_DIR = This is the path (folder) of your rawdata.brn file >> set it according with your needs (overriden by DATA_IN_LOCAL_FOLDER)
    2.3 sleeptime:: this variable tells you how often the program look for the rawdata.brn file.... is expressed in seconds... Change it according to your wish 
    2.4 JSON_IN_LOCAL_FOLDER=True ...if this is set than it will store the jsondata file in the same folder as the main. If you do not care leave it like this..otherwise read 2.4.1
            2.4.1 IF you set JSON_IN_LOCAL_FOLDER=False... In this case, set also JSON_SRC_DIR.. This is a writable directory to be used to store data in case of no internet connection
    2.5 retrytime:: this variable tells you how often the program will try to re-send the JSON files that was unable to sent before. I suggest that you set it around 10 times higher than sleeptime.
3. in the login_handler.py SET:
    3.1 STORE_SAME_FOLDER=True means that it will store the token file and it will look for the certfile.pem file in the same folder of the main.py file. IF you set it to false, then you can set your own path to CERTIFICATE_SRC_DIR

4. Please check that the software has the permission to operate on the folders that you set (for example that has permission to write /usr/local/broentech/logs/ or has permission to delete the rawdata.brn file, etc) .
5. You can now deploy the software to your gateways. If you start the software at this point, it will try to download a token but it will fail because it is not recognized by the server. So write down the MAC ADDRESS of the gateway that you want to add and proceed to the next section

----Now you need to create an account and associate the gateway...for doing so:

6- CREATE an ACCOUNT on -->   https://talaiot.io:3000/#!  and  Log-in with the new account
7- Go on --> "Device" --> "Create a new device" (the + symbol on the right of the screen)
8- ADD the MAC ADDRESS of your gateway and a description. The mac must be UPPERCASE (eg.: 34:F3:3A:1B:DD).
9- Now your device will appear on your list. Also the TOKEN field shows the actual token (a random alphanumeric string).
10- START the GATEWAY app. This time the gateway will fetch the token from the server and store it in a file called "token". The file is located in the folder that you set at point 3.1 (by default is the same of main.py file)
11- You will notice that on the Webpage the status of the token has changed to FETCHED. This means that the device has correctly retrieved the token and is now ready to send data.

If everything worked as expected the gateway should automatically look for the rawdata.brn file and send it to the server.
You can now SEE the REAL TIME DATA in you admin page:

12- Go to "Sensordata" section. here you should have a list of your gateways. ONLY GATEWAYS that have sent data will appear. Select one from the list
13- Once you selected the Device, a sensor list will appear... Select the sensors that you are interested in
14. your data should now appear on the screen!

15. For adding new devices (gateways), go back on step 7.

The gateway also has more advanced features to recover from errors, we will explain those at a later time.

--------------------------------------------------------------------
Here are some FAQs that may interest you :
--------------------------------------------------------------------
Q0. How often the software check for rawdata.brn file
A0. You can set this interval by setting the sleeptime variable (see2.3)

Q1. Where does the device store the token file?
A1. By default the token file is stored in the same folder as the main.py file. You can override this (see 3.1)

Q2. Where i can set the path of my rawdata.brn file?
A2. The path is set in the main.py file. see 2.1/2.2

Q3.What is the jsondata file and where is it stored?
A3.jsondata is a file that is created when it fails to sent rawdata.brn file... by default use the same folder of main.py but you can override it (see 2.4)

Q4. What happens in case of no internet connection?
A4. The software will try to sent the rawdata.brn file, if it fails it will generate a jsondata file and will delete the rawdata.brn file... Basically your data will still be there saved as json.

Q5.  Is the jsonfile going to be deleted?
A5. The json file will be deleted from local storage  automatically when it has been  successfully sent to our servers.... IF THE CONNECTION NEVER COME BACK, THEN THIS FILE PERSISTS and will continue to grow was new data is appended.

Q6. The software is quite verbose..will the LOGS file grow up until they blow up my system?
A6. No. The log files will grow up to a max of 200kB. After that will be renamed as log.01 and the log.01 will be deleted. So you will have always 2 log files of 200kB as max.

Q7. I fails to Retrieve the token. The log says that " It seems that the server doesn't find my mac...Have you correctly added my mac to the portal? My MAC is:"
A7. have you added the device to your profile? Does the mac printed near the log line match the one you inserted? (is case sensitive)

Q8. The gateways says " Seems that the token has already been fetched but i do not have it! You must regenerate a new one from your portal", what i have to do?
A8. For security reason, the token can only be FETCHED once from our site. IF you manually fetch the token or if you manually delete the token file, then you must regenerate a new token online. Go to your admin profile-->"DEVICE" and click on "reset token" of the device that you want to reset. The token will show up. The Gateway will automatically fetch it, and the webpage will show "fetched".

Q9. In linux, if i press CTRL+C why the app does not stop immediately?
A9. Unfortunately some of the thread will be sleeping most of the time and thus will not "hear" the signint signal until they wake up. However, since they are sleeping, it is safe to force quit.

Q10. Can I use the shebang?
A10. In case that you really want to use the shebang, than you must clean the code from /n/r. I advice that you run it by simple typing:$ python main.py  

Q11. Can i test single modules?
A11. Yes, we included some testing functions in each module. 