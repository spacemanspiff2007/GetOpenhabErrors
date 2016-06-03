# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 10:45:34 2016

@author: gesebas
"""

import oh_rest
import json
import sys
import re

test_config = 0

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))
#print()

if len(sys.argv) > 1:
    if sys.argv[1] == "-T":
        print("Testing config")
        test_config = 1

errors = 0

def read_dict( filepath):
    try:
        new_dict = {}
        with open(filepath,'r') as inf:
            my_str = inf.read()
            if my_str == "":
                return new_dict
            new_dict = json.loads( my_str)
        return new_dict
        
    except Exception as e:
        print("Invalid Dict-File at '{}'!".format(filepath))
        print("Error: '{}'".format(e))
        return {}

def write_dict( my_dict, filepath):
    try:
        with open(filepath,'w') as inf:
            inf.write(json.dumps(my_dict, indent=4))
        return 0
    except Exception as e:
        print("Error while writing file at '{}'!".format(filepath))
        print("Error: '{}'".format(e))
        return 1
        

files  = read_dict( "files")
config = read_dict( "config")


if files == {} or config == {}:
    #exit()
    pass

if not config["OPENHAB"] or not config["OPENHAB"]["IP"] or not config["OPENHAB"]["PORT"]:
    exit()

rest = oh_rest.oh_rest( config["OPENHAB"]["IP"], config["OPENHAB"]["PORT"])

pattern_getlines = re.compile( "^(.+?)$", re.MULTILINE)

for k in config:
    if k == "OPENHAB":
        continue
    
    element = config[k]
    if not "PATH" in element:
        print( "No PATH entry in {:s}".format(k))
        continue
    if not "VAR" in element:
        print( "No VAR entry in {:s}".format(k))
        continue
    if not "INCLUDE" in element:
        print( "No INCLUDE entry in {:s}".format(k))
        continue

    #EXCLUDE is optional
    if not "EXCLUDE" in element:
        element["EXCLUDE"] = ""


    if not k in files:
        files[k] = {}
        files[k]["POS"] = 0

    with open( element["PATH"],'r') as logfile:
        logfile.seek(0,2) # move the cursor to the end of the file
        size = logfile.tell()
        pos  = files[k]["POS"]

        #Logrotate o.ä. -> von vorne
        if size < pos:
            pos = 0

        my_log = ""

        if test_config:
            logfile.seek( 0)
            my_log = logfile.read()            
        else:
            if pos == size:
                print( "No new lines in " + element["PATH"])
                continue
            
            #read rest of file
            logfile.seek( pos)
            my_log = logfile.read()
            files[k]["POS"] = logfile.tell()
        
        log_lines = re.findall(pattern_getlines, my_log)
        
        patter_include = re.compile( element["INCLUDE"], re.IGNORECASE)

        added   = 0
        sendstr = ""
        for line in log_lines:
            if re.search(patter_include, line):
                #check exclude                
                if element["EXCLUDE"] != "":
                    patter_exclude = re.compile( element["EXCLUDE"], re.IGNORECASE)
                    if re.search(patter_exclude, line):
                        continue
                
                #add line
                sendstr += (line + '\n', line) [ sendstr == ""]
                added += 1

        print( "{:d} of {:d} lines matched in {:s}".format( added, len(log_lines), element["PATH"]))
        #send string to openhab
        rest.put_status( element["VAR"], sendstr)
        
        #fertig
        logfile.close()


write_dict(files, "files")