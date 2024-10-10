import requests, argparse, os, json, base64
from time import sleep
from random import *

#EXPECTED IN THE SAME DIRECTORY AS THE PLUGIN
import nagiosxi_plugin_helper as xihlpr

#DEAL WITH THE SELF SIGNED NAGIOS SSL
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#NAGIOSXI PLUGIN TEMPLATE
#SNAPIER

#SCRIPT DEFINITION
cname = "nagiosxi_plugin_template"
cversion = "0.0.1"
appPath = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__" :
    
    #INPUT FROM NAGIOS
    args = argparse.ArgumentParser(prog=cname+"v:"+cversion, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    #ARGS
    #NSID
    args.add_argument(
        "-n","--nsid",
        required=False,
        choices=("drs","dev","prd"),
        default=None,
        help="String(nsid): The target nagiosxi environment for the plugin."
    ),    
    #HOSTNAME/ADDRESS
    args.add_argument(
        "-H","--host",
        required=True,
        default=None,
        help="String(hostname/hostaddress): The target host for the plugin to execute against."
    ),
    #CRITICAL THRESHOLD
    args.add_argument(
        "-c","--crit",
        required=True,
        default=None,
        help="String(CRITICAL Check Threshold): The critical threshold range for the check."
    ),
    #WARNING THRESHOLD
    args.add_argument(
        "-w","--warn",
        required=False,
        default=None,
        help="String(WARNING Check Threshold): The warning threshold range for the check."
    ),
    #PERFDATA
    args.add_argument (
        "-p","--perfdata",
        required=False,
        default=None,
        action="store_true",
        help="Boolean(True/False): If present in the comaand then perfdata for the check will be included in the output."
    )

    #PARSE ARGS
    meta = args.parse_args()

    #INCLUDED AS A TEST FOR THE NAGIOS CREDS FILE
    #INFO IS USED WITH NAGIOSXI GENERIC API CALLS
    if meta.nsid:
        #GET CREDS FROM YAML
        crds = xihlpr.creds(meta.nsid)
        print(crds)
    
    #GET RANDOM NUMBER TO EVALUATE
    x = xihlpr.test()

    #GLOBALS
    #NAGIOS DEVELOPMENT GUIDELINES STATE THAT YOU SHOULD SUPPORT THRESHOLD RANGES
    #TESTING FOR THE "@" SYMBOL AT THE START OR ":" IN THE VALUE 
    
    #CRITICAL RANGE
    cr = False
    #DID WE GET A CRITICAL RANGE
    if meta.crit.startswith("@") or ":" in meta.crit:
        cr = True
    
    #WARNING RANGE
    wr = False
    #DID WE GET A WARNING RANGE 
    if meta.warn and meta.warn.startswith("@") or ":" in meta.warn:
        wr = True
    
    #CRITICAL PROBLEM STATE
    cps = False
    
    #WARNING PROBLEM STATE
    wps = False
    
    #EVALUATE THE RESULT
    if x: 
        #FIRST IS WORSE SO WE EVALUATE CRITICAL RANGE    
        if cr:
            cps = xihlpr.nagThresholdRangeEval(meta.crit,x)
        #EVALUATE CRITICAL VALUE
        else:
            if cps == False and x >= int(meta.crit):
                cps = True

        #EVALUATE WARNING RANGE
        if cps == False and wr:
            wps = xihlpr.nagThresholdRangeEval(meta.warn,x)
        #EVALUATE WARNING
        else:
            if cps == False and wps == False and x >= int(meta.warn):
                wps = True
        
        #FORMAT THE OUTPUT
        #CRITICAL RANGE RESULT
        if cps and cr:
            stateid = 2
            msg = "{}: VALUE({}) IS IN RANGE({})".format(xihlpr.checkStateFromCode(stateid),x,meta.crit.strip("@"))
        #CRITICAL RESULT
        elif cps and not cr:
            stateid = 2
            msg = "{}: VALUE({}) IS >= ({})".format(xihlpr.checkStateFromCode(stateid),x,meta.crit)
        #WARNING RANGE RESULT
        elif wps and wr and not cps:
            stateid = 1
            msg = "{}: VALUE({}) IS IN RANGE({})".format(xihlpr.checkStateFromCode(stateid),x,meta.warn.strip("@"))
        #WARNING RESULT
        elif wps and not wr and not cps:
            stateid = 1
            msg = "{}: VALUE({}) IS >= ({})".format(xihlpr.checkStateFromCode(stateid),x,meta.warn)
        #OK OTHERWISE
        else:
            stateid = 0
            msg = "{}: VALUE IS ({})".format(xihlpr.checkStateFromCode(stateid),x)
    
        #NOW WE DEAL WITH THE PERFDATA
        #PERFDATA FOR A RANGE?! NOW THERE'S A NOODLE COOKER
        if meta.perfdata:
            if cr or wr:
                #DOESN'T FORMAT PROPERLY SO JUST GIVE RANDOM-INT VALUE
                pdata = " | random-int={};;;0;100;".format(x)
            else:
                #WARNING IS OPTIONAL SO WE NEED TO STEP AROUND THAT IN THE PERFDATA
                #0 is NOT A NONE VALUE WHICH IS WHAT WE WANT
                if meta.warn:
                    wrn = int(meta.warn)
                else:
                    wrn = ""
                
                #CRITICAL IS REQUIRED SO WE CAN JUST CONVER THAT TO AN INT
                crt = int(meta.crit)

                #UNIT OF MEASURE IS NOT NEED FOR AN INTEGER SO BLANK
                uom = ""
                
                #MINIMUM VALUE IS SET TO 0
                mn = 0
                
                #MAX IS SET TO 100
                mx = 100

                #PUT IT ALL TOGETHER
                pdata = " | random-int={}{};{};{};{};{};".format(x,uom,wrn,crt,mn,mx)
            
            #APPEND PDATA TO MSG
            msg = msg + pdata
    else:
        #WE DIDN'T GET ANYTHIN' TO EVALUATE
        stateid = 3
        msg = "{}: NO DATA GIVEN TO EVALUATE.".format(xihlpr.checkStateFromCode(stateid))

    #EXIT THE PLUGIN
    xihlpr.nagExit(stateid,msg)