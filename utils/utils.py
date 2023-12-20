import logging
import os
import time

from core import LOG_DIR

logger = logging.getLogger(__name__)


def clear_log_files():
    """
    Function to clear all files ending with .log from the LOG_DIR directory.
    """
    for filename in os.listdir(LOG_DIR):
        # Check if it's a log file before attempting to delete
        if filename.endswith(".log"):
            try:
                # Use os.remove instead of os.unlink for better compatibility
                os.remove(os.path.join(LOG_DIR, filename))
            except OSError as e:
                logger.error(f"Error deleting log file '{filename}': {e.strerror}.")


def get_file_size(filename: str) -> int:
    """
    Get the size of a file.

    Args:
        filename (str): The name of the file.

    Returns:
        int: The size of the file if it exists, -1 otherwise.
    """
    if os.path.isfile(filename):
        st = os.stat(filename)
        return st.st_size
    else:
        return -1


def wait_for_generation(file_path, timeout=1):
    """
    Waits for a file to finish generating or updating by periodically checking its size.

    Args:
        file_path (str): The path to the file.
        timeout (int, optional): The time in seconds to wait between checks. Defaults to 1.

    Returns:
        bool: True if the file has finished generating or updating, False otherwise.
    """
    current_size = get_file_size(file_path)
    time.sleep(timeout)
    while current_size != get_file_size(file_path) or get_file_size(file_path) == 0:
        current_size = get_file_size(file_path)
        time.sleep(timeout)
    return True
