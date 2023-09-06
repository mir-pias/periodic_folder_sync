import os
import time
import shutil
import hashlib
import subprocess
import pytest
import filecmp

# Constants for test folders and log file
SOURCE_DIR = "source_folder"
REPLICA_DIR = "replica_folder"
LOG_FILE = "test_log.txt"

from sync_folders import get_file_checksum

# Compare MD5 checksums of files in two directories.
def check_folders(src_dir, replica_dir):
    src_files = {}
    replica_files = {}

    # Generate MD5 checksums for files in the source directory
    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            src_files[file_path] = get_file_checksum(file_path)

    # Generate MD5 checksums for files in the replica directory
    for root, _, files in os.walk(replica_dir):
        for file in files:
            file_path = os.path.join(root, file)
            replica_files[file_path] = get_file_checksum(file_path)

    # Compare the MD5 checksums of files in both directories
    for file_path, src_checksum in src_files.items():
        replica_checksum = replica_files.get(file_path.replace(src_dir,replica_dir))
        if replica_checksum is None or src_checksum is None or src_checksum != replica_checksum:
            return False

    return True

 # Create source and replica folders for testing
@pytest.fixture
def setup_test_folders():
    if not os.path.exists(SOURCE_DIR):
        os.mkdir(SOURCE_DIR)

    if not os.path.exists(REPLICA_DIR):
        os.mkdir(REPLICA_DIR)

    # Create some files in the source folder
    with open(os.path.join(SOURCE_DIR, "file1.txt"), "w") as f:
        f.write("Test file 1")

    yield

    # Clean up test folders and files after testing
    shutil.rmtree(SOURCE_DIR)
    shutil.rmtree(REPLICA_DIR)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

# Run the sync script with a short interval
def test_basic_synchronization(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if replica folder matches the source folder
    assert filecmp.dircmp(SOURCE_DIR, REPLICA_DIR) and check_folders(SOURCE_DIR, REPLICA_DIR)

def test_file_creation(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur

    # Create a new file in the source folder
    new_file_path = os.path.join(SOURCE_DIR, "new_file.txt")
    with open(new_file_path, "w") as f:
        f.write("New test file")

    # Wait for synchronization to happen again
    time.sleep(2)
    sync_process.terminate()

    # Check if the new file was copied to the replica folder
    assert os.path.exists(os.path.join(REPLICA_DIR, "new_file.txt"))

def test_file_deletion(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    
    # Delete a file in the source folder
    deleted_file_path = os.path.join(SOURCE_DIR, "file1.txt")
    os.remove(deleted_file_path)

    # Wait for synchronization to happen again
    time.sleep(2)
    sync_process.terminate()

    # Check if the deleted file was removed from the replica folder
    assert not os.path.exists(os.path.join(REPLICA_DIR, "file1.txt"))

def test_file_modification(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur

    # Modify a file in the source folder
    modified_file_path = os.path.join(SOURCE_DIR, "file1.txt")
    with open(modified_file_path, "a") as f:
        f.write("\nModified content")

    # Wait for synchronization to happen again
    time.sleep(2)
    sync_process.terminate()

    # Check if the modified file in the replica folder matches the source folder
    with open(os.path.join(REPLICA_DIR, "file1.txt"), "r") as replica_file:
        replica_content = replica_file.read()
    with open(modified_file_path, "r") as source_file:
        source_content = source_file.read()
    assert replica_content == source_content

# test sync of nested folders and files in the source directory
def test_nested_folders(setup_test_folders):
    os.mkdir(os.path.join(SOURCE_DIR, "subfolder"))
    with open(os.path.join(SOURCE_DIR, "subfolder", "nested_file.txt"), "w") as f:
        f.write("Nested file")

    # Run the synchronization script with a short interval
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the replica folder contains the nested folder and its contents
    assert os.path.exists(os.path.join(REPLICA_DIR, "subfolder"))
    assert os.path.exists(os.path.join(REPLICA_DIR, "subfolder", "nested_file.txt"))

def test_multiple_file_operations(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    

    # Create a new file, modify an existing file, and delete a file in the source folder
    new_file_path = os.path.join(SOURCE_DIR, "new_file.txt")
    with open(new_file_path, "w") as f:
        f.write("New test file")
    modified_file_path = os.path.join(SOURCE_DIR, "file1.txt")
    with open(modified_file_path, "a") as f:
        f.write("\nModified content")
    deleted_file_path = os.path.join(SOURCE_DIR, "file2.txt")
    open(deleted_file_path, "x") # create file2    
    os.remove(deleted_file_path) # delete file2
    

    # Wait for synchronization to happen again
    time.sleep(2)
    sync_process.terminate()

    # Check if the replica folder accurately reflects the changes
    assert os.path.exists(os.path.join(REPLICA_DIR, "new_file.txt"))
    with open(os.path.join(REPLICA_DIR, "file1.txt"), "r") as replica_file:
        replica_content = replica_file.read()
    with open(modified_file_path, "r") as source_file:
        source_content = source_file.read()
    assert replica_content == source_content
    assert not os.path.exists(os.path.join(REPLICA_DIR, "file2.txt"))


def test_logging_to_file(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the log file was created and contains expected log messages
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, "r") as log_file:
        log_content = log_file.read()
    assert "Copied" in log_content

def test_logging_to_console(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the console output contains expected log messages
    stdout, stderr = sync_process.communicate()
    output = stdout.decode("utf-8") + stderr.decode("utf-8")
    assert "Copied" in output

# Run the sync script with different replica folder, interval, and log file
def test_command_line_arguments(setup_test_folders):
    sync_process = subprocess.Popen(
        [
            "python",
            "sync_folders.py",
            SOURCE_DIR,
            'diff_replica',
            "5",  # Longer synchronization interval
            "custom_log.txt",  # Custom log file
        ]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the custom log file was created and contains expected log messages
    assert os.path.exists("custom_log.txt")
    with open("custom_log.txt", "r") as log_file:
        log_content = log_file.read()
    assert "Copied" in log_content

    
    shutil.rmtree('diff_replica')
    if os.path.exists('custom_log.txt'):
        os.remove('custom_log.txt')

# Run the sync script with incorrect folder paths
def test_error_handling(setup_test_folders):
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", "nonexistent_source", "nonexistent_replica", "1", LOG_FILE]
    )
    
    # Check if the script exits with a non-zero status code, indicating an error
    assert sync_process.returncode != 0

    sync_process.terminate()

    if os.path.exists("nonexistent_replica"):
        shutil.rmtree("nonexistent_replica")

# test sync of a large number of files and folders 
def test_performance(setup_test_folders):
    for i in range(100):
        os.mkdir(os.path.join(SOURCE_DIR, f"folder_{i}"))
        with open(os.path.join(SOURCE_DIR, f"file_{i}.txt"), "w") as f:
            f.write(f"Test file {i}")

    # Run the synchronization script with a short interval
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(5)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the replica folder matches the source folder
    assert filecmp.dircmp(SOURCE_DIR, REPLICA_DIR) and check_folders(SOURCE_DIR, REPLICA_DIR)

# Create a second set of source and replica folders for concurrent testing
def test_concurrency(setup_test_folders):
    os.mkdir("source_folder2")
    # os.mkdir("replica_folder2")

    # Run two instances of the synchronization script concurrently
    sync_process1 = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    sync_process2 = subprocess.Popen(
        ["python", "sync_folders.py", "source_folder2", "replica_folder2", "1", "log_file2.txt"]
    )

    time.sleep(5) # Allow time for synchronization to occur
    sync_process1.terminate()
    sync_process2.terminate()

    # Check if both replica folders match their respective source folders
    assert filecmp.dircmp(SOURCE_DIR, REPLICA_DIR) and check_folders(SOURCE_DIR, REPLICA_DIR)
    assert filecmp.dircmp("source_folder2", "replica_folder2") and check_folders("source_folder2", "replica_folder2")


    # Clean up test folders and files after testing
    shutil.rmtree("source_folder2")
    shutil.rmtree("replica_folder2")
    if os.path.exists("log_file2.txt"):
        os.remove("log_file2.txt")

def test_resource_usage(setup_test_folders):
    start_time = time.time()
    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
    )
    time.sleep(5)  # Allow time for synchronization and resource measurement
    sync_process.terminate()
    end_time = time.time()

    # Check if the script completes within a reasonable time (e.g., less than 10 seconds)
    assert end_time - start_time < 10

def test_cross_platform_compatibility(setup_test_folders): ## tested only on windows
    os_name = os.name
    if os_name == "posix":
        # Linux and macOS
        sync_process = subprocess.Popen(
            ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
        )
    elif os_name == "nt":
        # Windows
        sync_process = subprocess.Popen(
            ["python", "sync_folders.py", SOURCE_DIR, REPLICA_DIR, "1", LOG_FILE]
        )
    else:
        pytest.skip("Unsupported operating system for this test")

    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the replica folder matches the source folder on the respective OS
    assert filecmp.dircmp(SOURCE_DIR, REPLICA_DIR) and check_folders(SOURCE_DIR, REPLICA_DIR)

# Run the sync script with empty source and replica folders
def test_edge_cases(setup_test_folders):
    empty_source_dir = os.path.join(SOURCE_DIR, "empty_source")
    empty_replica_dir = os.path.join(REPLICA_DIR, "empty_replica")
    os.mkdir(empty_source_dir)
    os.mkdir(empty_replica_dir)

    sync_process = subprocess.Popen(
        ["python", "sync_folders.py", empty_source_dir, empty_replica_dir, "1", LOG_FILE]
    )
    time.sleep(2)  # Allow time for synchronization to occur
    sync_process.terminate()

    # Check if the empty replica folder matches the empty source folder
    assert filecmp.dircmp(SOURCE_DIR, REPLICA_DIR) 


