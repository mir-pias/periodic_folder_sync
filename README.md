# periodic_folder_sync
test task for the position of Developer in QA with Python

This Python script can be used to synchronize two folders periodically. It monitors a source folder for changes and updates a replica folder to match the source folder's contents. the user can specify the source and replica folder paths, the sync interval, and log file path.

## Features

- Periodically syncs a source folder to a replica folder.
- Tracks file and folder creation in the source folder after the first sync.
- Logs synchronization events to a specified log file and console.
- Supports both file and folder synchronization.
- Computes MD5 checksums to verify file integrity.

## Usage

### Prerequisites
Before using the script, make sure you have Python 3.x installed on your system.

### Installation
1. Clone this repository or download the script directly.

    `git clone https://github.com/mir-pias/periodic_folder_sync.git`

2. Navigate to the script's directory.

    `cd periodic_folder_sync`

### Command Line Usage
Run the script from the command line with the following arguments:

- source_folder: The path to the source folder you want to synchronize.
- replica_folder: The path to the replica folder that will mirror the source folder.
- sync_interval: The sync interval in seconds, specifying how often the folders should be checked for changes.
- log_file: The path to the log file where synchronization events will be recorded.
Example:

`python sync_folders.py /path/to/source /path/to/replica 3600 sync.log`

This command will synchronize the source folder with the replica folder every 3600 seconds (1 hour) and log events to sync.log.

### test script
the `test_script.py` was used to test the functionality of the `sync_folders.py` script. To use it, follow these steps: 

1. Install pytest by running the following command:

    `pip install -r requirements.txt`

2. Run the script from command line with:

    `pytest test_script.py`

### Behavior
- The script will create the replica folder if it does not exist.
- During the first synchronization, it will copy all files and folders from the source to the replica.
- Subsequent synchronizations will track and log any new files or folders created in the source.
- The script will copy new files and folders from the source to the replica.
- If a file in the replica has a different MD5 checksum from the source, it will be updated.
- If a file or folder exists in the replica but not in the source, it will be deleted from the replica.

### Customization
You can customize the behavior of the script by modifying the source code directly. For example, you can change the log format, adjust the checksum method, or add additional synchronization rules.


