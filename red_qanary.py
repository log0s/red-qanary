import os
import pwd
import argparse
import platform
import getpass
import datetime
import subprocess
import psutil
import json

system_platform = platform.system()

is_mac = system_platform == 'Darwin'
is_linux = system_platform == 'Linux'
is_windows = system_platform == 'Windows'

# Use the getpwuid solution on Unix-like systems to properly handle the sudo case
username = getpass.getuser() if is_windows else pwd.getpwuid(os.getuid()).pw_name

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

parser.add_argument('executable', type=str, help='path to the executable to be run')
parser.add_argument('-a', '--args', type=str, dest='exeargs', default='', help='OPTIONAL - arguments to pass when running the executable')
parser.add_argument('-f', '--filepath', type=str, default=f'{"" if is_windows else "./"}redQAnary.json', help='OPTIONAL - path (including name) of the temporary file to be created')
parser.add_argument('-u', '--url', type=str, default='http://www.redcanary.com', help='OPTIONAL - external endpoint to make a GET request to')

args = parser.parse_args()

# Run executable
try:
    exe_cmd = ' '.join([args.executable, args.exeargs])
    print(f'Running executable. Command: {exe_cmd}')
    base_log['logs']['exe_run'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'process_command': exe_cmd,
        'error': None
    }

    exe_process = subprocess.check_output(exe_cmd, shell=True)

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
    file_create_cmd = f'{"copy NUL" if is_windows else "touch"} {args.filepath}'

    # Create dirs first if necessary
    if filepath_includes_dirs and is_windows:
        dir_create_cmd = f'mkdir {"/".join(split_filepath[:-1])}'
    elif filepath_includes_dirs:
        dir_create_cmd = f'mkdir -p {"/".join(split_filepath[1:-1])}'  
    else:
        dir_create_cmd = None

    full_create_cmd = ' && '.join([dir_create_cmd, file_create_cmd]) if dir_create_cmd is not None else file_create_cmd

    print(f'Creating file. Command: {full_create_cmd}')
    base_log['logs']['file_create'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'file_path': args.filepath,
        'action_type': 'create',
        'process_command': full_create_cmd,
        'error': None
    }

    file_create_process = subprocess.Popen(full_create_cmd, shell=True)

    base_log['logs']['file_create']['process_id'] = file_create_process.pid
    base_log['logs']['file_create']['process_name'] = psutil.Process(file_create_process.pid).name()

    file_create_process.wait()
except Exception as err:
    print(f'ERROR - Error creating file. Details: {err}')
    base_log['logs']['file_create']['error'] = err

# Modify file
if base_log['logs']['file_create']['error'] is None:
    try:
        file_modify_cmd = f'echo "This test courtesy of Red QAnary" {">" if is_windows else ">>"} {args.filepath}'
        print(f'Modifying file. Command: {file_modify_cmd}')
        base_log['logs']['file_modify'] = {
            'start_time': datetime.datetime.now(),
            'username': username,
            'file_path': args.filepath,
            'action_type': 'modify',
            'process_command': file_modify_cmd,
            'error': None
        }

        file_modify_process = subprocess.Popen(file_modify_cmd, shell=True)

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
            file_delete_cmd = f'rd /s /q {split_filepath[0]}' if is_windows else f'rm -rf {split_filepath[1]}'
        else:
            file_delete_cmd = f'del /q {args.filepath}' if is_windows else f'rm -f {args.filepath}'

        print(f'Deleting file. Command: {file_delete_cmd}')
        base_log['logs']['file_delete'] = {
            'start_time': datetime.datetime.now(),
            'username': username,
            'file_path': args.filepath,
            'action_type': 'delete',
            'process_command': file_delete_cmd,
            'error': None
        }

        file_delete_process = subprocess.Popen(file_delete_cmd, shell=True)

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
    network_request_cmd = f'curl -o {"nul" if is_windows else "/dev/null"} -w "%{{local_ip}}:%{{local_port}},%{{remote_ip}}:%{{remote_port}},%{{size_request}}" http://www.redcanary.com'

    print(f'Making network request. Command: {network_request_cmd}')
    base_log['logs']['network_request'] = {
        'start_time': datetime.datetime.now(),
        'username': username,
        'process_command': network_request_cmd,
        'protocol': 'HTTP',
        'error': None
    }

    network_request_process = subprocess.Popen(network_request_cmd, shell=True, stdout=subprocess.PIPE)

    base_log['logs']['network_request']['process_id'] = network_request_process.pid
    base_log['logs']['network_request']['process_name'] = psutil.Process(network_request_process.pid).name()

    (res, err) = network_request_process.communicate()

    if err is not None:
        raise Exception(err)

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