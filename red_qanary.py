import os
import argparse
import platform
import getpass
import datetime
import subprocess
import psutil
import json
import shlex

is_windows = platform.system() == 'Windows'

# Use the getpwuid solution on Unix-like systems to properly handle the sudo case
if is_windows:
    username = getpass.getuser()
else:
    # pwd doesn't exist on Windows so we need to conditionally import it
    import pwd
    username = pwd.getpwuid(os.getuid()).pw_name

base_log = {
    'start_time': datetime.datetime.now(),
    'username': username,
    'process_id': os.getpid(),
    'logs': {
        'exe_run': {},
        'file_create': {},
        'file_modify': {},
        'file_delete': {},
        'network_request': {}
    }
}

parser = argparse.ArgumentParser('Red QAnary');

parser.add_argument('-e', '--exe', type=str, default='rundll32' if is_windows else './default_exec.sh', help='OPTIONAL - path to the executable to be run')
parser.add_argument('-a', '--args', type=str, dest='exeargs', default='', help='OPTIONAL - arguments to pass when running the executable')
parser.add_argument('-f', '--filepath', type=str, default=f'{"" if is_windows else "./"}red_qanary.txt', help='OPTIONAL - path (including name) of the temporary file to be created')
parser.add_argument('-u', '--url', type=str, default='http://www.redcanary.com', help='OPTIONAL - external endpoint to make a GET request to')

args = parser.parse_args()

# Run executable
try:
    exe_cmd = ' '.join([args.exe, args.exeargs])
    print(f'Running executable. Command: {exe_cmd}')
    base_log['logs']['exe_run'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'process_command': exe_cmd,
        'error': None
    }

    exe_process = subprocess.Popen(exe_cmd if is_windows else shlex.split(exe_cmd))

    base_log['logs']['exe_run']['process_id'] = exe_process.pid
    base_log['logs']['exe_run']['process_name'] = psutil.Process(exe_process.pid).name()

    exe_process.wait()
except Exception as err:
    print(f'ERROR - Error running executable. Details: {err}')
    base_log['logs']['exe_run']['error'] = err

# Detect whether filepath includes dirs we might need to create
split_filepath = args.filepath.split('/')
filepath_includes_dirs = len(split_filepath) > 2 or (is_windows and len(split_filepath) > 1)

# Create file
try:
    file_create_cmd = f'{"cmd /c type NUL >" if is_windows else "touch"} {args.filepath}'

    # Create dirs first if necessary
    if filepath_includes_dirs:
        dir_create_cmd = f'cmd /c mkdir {"/".join(split_filepath[:-1])}' if is_windows else f'mkdir -p {"/".join(split_filepath[1:-1])}'
        subprocess.check_call(dir_create_cmd.split(' ') if is_windows else shlex.split(dir_create_cmd))

    print(f'Creating file. Command: {file_create_cmd}')
    base_log['logs']['file_create'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'file_path': args.filepath,
        'action_type': 'create',
        'process_command': file_create_cmd,
        'error': None
    }

    file_create_process = subprocess.Popen(file_create_cmd.split(' ') if is_windows else shlex.split(file_create_cmd))

    base_log['logs']['file_create']['process_id'] = file_create_process.pid
    base_log['logs']['file_create']['process_name'] = psutil.Process(file_create_process.pid).name()

    file_create_process.wait()
except Exception as err:
    print(f'ERROR - Error creating file. Details: {err}')
    base_log['logs']['file_create']['error'] = err

# Modify file
if base_log['logs']['file_create']['error'] is None:
    try:
        file_modify_cmd = f'cmd /c echo "ThistestcourtesyofRedQAnary" > {args.filepath}' if is_windows else 'echo "This test courtesy of Red QAnary"'
        print(f'Modifying file. Command: {file_modify_cmd}')
        base_log['logs']['file_modify'] = {
            'start_time': datetime.datetime.now(),
            'username': username,
            'file_path': args.filepath,
            'action_type': 'modify',
            'process_command': file_modify_cmd,
            'error': None
        }

        if is_windows:
            file_modify_process = subprocess.Popen(file_modify_cmd.split(' '))
        else:
            output_file = open(args.filepath, 'a')
            file_modify_process = subprocess.Popen(shlex.split(file_modify_cmd), stdout=output_file)

        base_log['logs']['file_modify']['process_id'] = file_modify_process.pid
        base_log['logs']['file_modify']['process_name'] = psutil.Process(file_modify_process.pid).name()

        file_modify_process.wait()
    except Exception as err:
        print(f'ERROR - Error modifying file. Details: {err}')
        base_log['logs']['file_modify']['error'] = err
else:
    file_modify_error = 'Could not modify file due to error during file creation'
    print(f'ERROR - {file_modify_error}')
    base_log['logs']['file_modify'] = {
        'start_time': datetime.datetime.now(),
        'error': file_modify_error
    }

# Delete file
if base_log['logs']['file_create']['error'] is None:
    try:
        # Clean up dirs as well if necessary
        if filepath_includes_dirs:
            file_delete_cmd = f'cmd /c rd /s /q {split_filepath[0]}' if is_windows else f'rm -rf {split_filepath[1]}'
        else:
            file_delete_cmd = f'cmd /c del /q {args.filepath}' if is_windows else f'rm -f {args.filepath}'

        print(f'Deleting file. Command: {file_delete_cmd}')
        base_log['logs']['file_delete'] = {
            'start_time': datetime.datetime.now(),
            'username': username,
            'file_path': args.filepath,
            'action_type': 'delete',
            'process_command': file_delete_cmd,
            'error': None
        }

        file_delete_process = subprocess.Popen(file_delete_cmd.split(' ') if is_windows else shlex.split(file_delete_cmd))

        base_log['logs']['file_delete']['process_id'] = file_delete_process.pid
        base_log['logs']['file_delete']['process_name'] = psutil.Process(file_delete_process.pid).name()

        file_delete_process.wait()
    except Exception as err:
        print(f'ERROR - Error deleting file. Details: {err}')
        base_log['logs']['file_delete']['error'] = err
else:
    file_delete_error = 'Could not delete file due to error during file creation'
    print(f'ERROR - {file_delete_error}')
    base_log['logs']['file_delete'] = {
        'start_time': datetime.datetime.now(),
        'error': file_delete_error
    }

# Make network request
try:
    network_request_cmd = f'curl -o {"nul" if is_windows else "/dev/null"} -w "%{{local_ip}}:%{{local_port}},%{{remote_ip}}:%{{remote_port}},%{{size_request}}" {args.url}'

    print(f'Making network request. Command: {network_request_cmd}')
    base_log['logs']['network_request'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'process_command': network_request_cmd,
        'protocol': args.url.split(':/')[0],
        'error': None
    }

    network_request_process = subprocess.Popen(network_request_cmd if is_windows else shlex.split(network_request_cmd), stdout=subprocess.PIPE)

    base_log['logs']['network_request']['process_id'] = network_request_process.pid
    base_log['logs']['network_request']['process_name'] = psutil.Process(network_request_process.pid).name()

    (res, err) = network_request_process.communicate()
    res_params = res.decode('utf-8').split(',')

    base_log['logs']['network_request']['source_address'] = res_params[0]
    base_log['logs']['network_request']['destination_address'] = res_params[1]
    base_log['logs']['network_request']['data_sent_size'] = res_params[2]
except Exception as err:
    print(f'ERROR - Error making network request. Details: {err}')
    base_log['logs']['network_request']['error'] = err

with open('red_qanary_logs.json', 'w') as f:
    print('Creating log file')
    json.dump(base_log, f, indent=4, default=str)
    print(f'Log file created at {"./" if not is_windows else ""}red_qanary_logs.json')