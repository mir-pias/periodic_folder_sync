import os
import time
import shutil
import hashlib
import argparse
import logging

# MD5 checksum
def get_file_checksum(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

# Track file/folder creation in the source folder after first sync and log it 
def track_source_changes(source_folder, sync_interval, logger, first_sync=False):  
    if first_sync:
        return
    
    for entry in os.scandir(source_folder):
        if entry.is_file() or entry.is_dir():
            created_time = os.path.getctime(entry.path)
            current_time = time.time()
            time_difference = current_time - created_time

            # Check if the entry was created within the sync interval
            if 0 < time_difference <= sync_interval:
                event_type = "File Created" if entry.is_file() else "Folder Created"
                log_message = f"{event_type}: {entry.name} at {source_folder}"
                logger.info(log_message)

# copy files and folders from source to replica
def copy_files_and_folders(source_folder, replica_folder, logger, sync_interval, first_sync):
    track_source_changes(source_folder, sync_interval, logger, first_sync)

    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)
        replica_path = os.path.join(replica_folder, item)

        # copy a folder and all its subfolders and files if it doesn't exist
        if os.path.isdir(source_path):
            if not os.path.exists(replica_path):
                shutil.copytree(source_path, replica_path)
                logger.info(f"Copied: {source_path} to {replica_path}")
            # if root folder exists, recursive function call on the root
            else:
                copy_files_and_folders(source_path, replica_path, logger, sync_interval, first_sync)            
                
        # copy a file if it doesn't exist
        elif os.path.isfile(source_path):
            if not os.path.exists(replica_path) or get_file_checksum(source_path) != get_file_checksum(replica_path):
                shutil.copy2(source_path, replica_path)
                logger.info(f"Copied: {source_path} to {replica_path}")
    
# delete files and folders from replica if its not found in source
def del_files_and_folders(source_folder, replica_folder, logger):
    for item in os.listdir(replica_folder):
        replica_path = os.path.join(replica_folder, item)
        source_path = os.path.join(source_folder, item)

        # If a folder is in the replica but not in the source, delete it
        if os.path.isdir(replica_path):
            if not os.path.exists(source_path):
                shutil.rmtree(replica_path)
                logger.info(f"Removed folder: {replica_path}")
            # if root folder exists in source, go into the folder and repeat the process
            else:
                del_files_and_folders(source_path, replica_path, logger)
            

        # If a file is in the replica but not in the source, delete it
        elif os.path.isfile(replica_path) and not os.path.exists(source_path):
            os.remove(replica_path)
            logger.info(f"Removed file: {replica_path}")
            
# Sync source to replica folder
def sync_folders(source_folder, replica_folder, logger, sync_interval, first_sync):
    if not os.path.exists(replica_folder):
        os.mkdir(replica_folder)

    copy_files_and_folders(source_folder, replica_folder, logger, sync_interval, first_sync)
    
    del_files_and_folders(source_folder, replica_folder, logger)

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders periodically.")
    parser.add_argument("source_folder", help="Source folder path")
    parser.add_argument("replica_folder", help="Replica folder path")
    parser.add_argument("sync_interval", type=int, help="Sync interval in seconds")
    parser.add_argument("log_file", help="Log file path")
    args = parser.parse_args()
    
    first_sync = True  # Track file/folder creation only after the first synchronization

    # init logger
    logging.basicConfig(filename=args.log_file, level=logging.INFO, format="%(asctime)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    # init console handler for logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    # periodically sync source to replica
    try:
        while True:        
            sync_folders(args.source_folder, args.replica_folder, logger, args.sync_interval, first_sync)
            first_sync = False 
            time.sleep(args.sync_interval)
    except KeyboardInterrupt:
        print("Synchronization stopped.")

if __name__ == "__main__":
    main()
