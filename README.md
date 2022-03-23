# red-qanary
Red QAnary - Tool to generate activity for testing/QAing EDR frameworks.

## Dependencies
`sudo pip install psutil`

If you want to utilize the included shell script on a Mac/Linux system you'll need to make it executable:
`chmod +x ./default_exec.sh`

## Usage
```
python red_qanary.py [-h] [-e EXE] [-a EXEARGS] [-f FILEPATH] [-u URL]

Run a series of commands to generate activity for testing EDR frameworks.

optional arguments:
    -h                  Show help message
    -e, --exe           Path to executable to run. Defaults to running included shell script for Unix-like systems and rundll32 for Windows systems
    -a, --args          Arguments to pass to the executable. Defaults to nothing
    -f, --filepath      Path to a file that will be created, modified, and then deleted. Defaults to red_qanary.txt
    -u, --url           External endpoint to make a GET request to
```
