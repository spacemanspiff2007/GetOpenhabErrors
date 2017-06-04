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

path   = str(sys.argv[0])
folder = path.partition('GetErrors.py')[0]
#print("folder:")
#print(folder)

if len(sys.argv) > 1:
    if sys.argv[1] == "-T":
        print("Testing config")
        test_config = 1



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
        
errors = 0
files  = read_dict( folder + "files")
config = read_dict( folder + "config")


if not config["OPENHAB"] or not config["OPENHAB"]["IP"] or not config["OPENHAB"]["PORT"]:
    sys.exit("No valid 'OPENHAB' entry in config file.")

#empty user + password
if not config["OPENHAB"]["USERNAME"]:
    config["OPENHAB"]["USERNAME"] = ""
if not config["OPENHAB"]["PASSWORD"]:
    config["OPENHAB"]["PASSWORD"] = ""

rest = oh_rest.oh_rest( config["OPENHAB"]["IP"], config["OPENHAB"]["PORT"], config["OPENHAB"]["USERNAME"], config["OPENHAB"]["PASSWORD"])

pattern_getlines = re.compile( r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}.+?)(?=\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3})", re.MULTILINE | re.DOTALL)

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

    with open( element["PATH"],'r', encoding="latin-1", errors="surrogateescape") as logfile:
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
        
        log_lines     = re.findall(pattern_getlines, my_log)
        log_lines_len = len(log_lines)
        
        patter_include = re.compile( element["INCLUDE"], re.IGNORECASE)
        patter_exclude = re.compile( element["EXCLUDE"], re.IGNORECASE)

        added   = 0
        sendstr = ""
        for line in log_lines:
            if re.search(patter_include, line):
                #check exclude                
                if element["EXCLUDE"] != "":
                    if re.search(patter_exclude, line):
                        continue
                
                #add line
                sendstr += '\n\n' + line if sendstr != "" else line
                added += 1

        print( "{:4d} of {:5d} lines matched for '{:s}' in '{:s}'".format( added, log_lines_len, k, element["PATH"]))
        #send string to openhab
        try:        
            rest.put_status( element["VAR"], sendstr)
        except Exception as e:
            print("Could not post update to variable '{}'!".format(element["VAR"]))
            print("Error: '{}'".format(e))
            errors = errors + 1
        
        #fertig
        logfile.close()


if write_dict(files, folder + "files") != 0:
    sys.exit("Error! Could not persist file pointers!")
    
if errors != 0:
    sys.exit("There were Errors during program execution")