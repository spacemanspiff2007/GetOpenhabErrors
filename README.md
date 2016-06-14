# GetOpenhabErrors
Small script to search logs for custom entries.
Matching lines are then be transfered to openhab through the REST-API.
It supports multiple calls and and then processes only the new log entries.

## Prerequisites
The script is written for Python 3. Additionally the "requests" module has to be installed.
This can be easily installed through pip (
```"pip install requests"```).

### Raspberry PI
[Here is some documentation how to install both on the Raspberry PI](https://www.raspberrypi.org/documentation/linux/software/python.md "Guide how to install Python and PI for Raspberry PI"). Please make sure to install for Python 3!

## Installation
It is recommended to put the script in the ```openhab/etc/GetOpenhabErrors``` folder but it can be run from everywhere.
Just copy all the files in the same directory.

## Configuration
Configuration can be done through the ```config``` file.
```python
{
	"OPENHAB" : {
		"IP"		: "localhost",
		"PORT"		: "8080",
		"USERNAME"	: "",
		"PASSWORD"	: ""
	},
	
    "name1" : {
        "PATH"		: "/opt/openhab/logs/openhab.log",
        "VAR" 		: "LastError",
		"INCLUDE"	: "\\[error.+\\]",
		"EXCLUDE"	: ""
    }
}
```

The configuration file is split in two parts:
- an entry with "OPENHAB"
- 1 .. n entries with a unique name

### The OPENHAB section
The OPENHAB section defines how the REST-API connects to the openhab-server. It is possible to push status-updates to a different machine, but usually the script is running on the same machine running openhab. Then the defaults should be sufficient.

### Other sections
The other sections can have any name, it just has to be unique. Each section has three mandatory entries, the "EXCLUDE" entry is optional.

| key | value |
|:----:|---|
| PATH | Specifies the path to the file which will be processed |
| VAR | Name of the string(!) variable in openhab which will receive the matching lines|
| INCLUDE | If this regular expression is found, the line will be included in the result |
| EXCLUDE (optional)| If this regula expression matches, the line will not be appendet to the result |

## Calling the script
Just call ```"python GetOpenhabErrors.py"``` or 
```"python3 GetOpenhabErrors.py"``` on the Raspberry PI.

Note: The first call will give you an error since the file which holds the file positions (```files```) is not yet created.

### Parameters
Call the script with parameter ```-T``` to test your regular expression. It will not update the file positions but rather process the whole specified file.

## Calling the script from openhab
It is possible to call the script directly from openhab.
This is a rule example which checks the openhab log (on a Raspberri PI) every two hours for new errors. The errors then are sent as notifications through the pushover-addon.
```java
rule "Check for Errors"
when
	Time cron "0 30 0/2 ? * *"
then
	val String results = executeCommandLine("python3@@/opt/openhab/etc/GetOpenhabErrors/GetErrors.py", 15000)
	logInfo("Exec", results)
end


rule "Error Change"
when
	Item LastError received update
then
	var String error =  LastError.state.toString
	
	if( error == "") {
		return false
	}
	
	if (error.length > 500){
		error = error.left(500)
	}
	
	pushover( error, 1)
end
```
