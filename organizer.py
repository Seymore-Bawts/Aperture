import os
import shutil
import logging
from collections import defaultdict

# --- Configuration ---
# Configure the logging system to provide clear, timestamped output.
# This is crucial for diagnostics and tracking the operations of our utility.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

# --- Core Logic ---
class FileOrganizer:
    """
    A class to organize files in a specified directory by their extension.
    It provides a structured, reusable, and extensible way to manage file sorting.
    """

    def __init__(self, target_directory):
        """
        Initializes the FileOrganizer with a target directory.

        Args:
            target_directory (str): The absolute path to the directory to be organized.
        """
        if not os.path.isdir(target_directory):
            # We must validate our inputs. A system is only as strong as its weakest assumption.
            raise ValueError(f"Error: The specified path '{target_directory}' is not a valid directory.")
        self.target_directory = target_directory
        self.file_mappings = self._create_default_mappings()
        logging.info(f"FileOrganizer initialized for directory: {self.target_directory}")

    def _create_default_mappings(self):
        """
        Creates a default dictionary mapping file extensions to category folders.
        This modular design allows for easy expansion in the future.
        """
        mappings = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            'Documents': ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.rtf', '.odt'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
            'Video': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
            'Scripts': ['.py', '.js', '.sh', '.bat'],
            'Executables': ['.exe', '.msi', '.dmg'],
        }
        # Invert the dictionary for efficient lookups: {'.ext': 'Category'}
        extension_to_category = {ext: category for category, extensions in mappings.items() for ext in extensions}
        return extension_to_category

    def organize_files(self):
        """
        Executes the file organization process.
        It iterates through all files in the target directory and moves them
        to their respective category folders.
        """
        logging.info("Starting file organization process...")
        files_moved = 0
        files_skipped = 0

        for filename in os.listdir(self.target_directory):
            source_path = os.path.join(self.target_directory, filename)

            # We only process files, not directories. This prevents recursion errors.
            if os.path.isdir(source_path):
                continue

            # Extract the file extension, ensuring it's in lowercase for consistent matching.
            file_extension = os.path.splitext(filename)[1].lower()

            if not file_extension:
                logging.warning(f"Skipping file without extension: {filename}")
                files_skipped += 1
                continue

            # Determine the destination category. If unknown, it goes into 'Other'.
            destination_folder_name = self.file_mappings.get(file_extension, 'Other')
            destination_path = os.path.join(self.target_directory, destination_folder_name)

            # Create the destination folder if it does not exist. A necessary precaution.
            os.makedirs(destination_path, exist_ok=True)

            # Construct the final destination file path.
            destination_file_path = os.path.join(destination_path, filename)

            try:
                # The core action: moving the file.
                shutil.move(source_path, destination_file_path)
                logging.info(f"Moved: {filename} -> {destination_folder_name}/")
                files_moved += 1
            except Exception as e:
                logging.error(f"Failed to move {filename}. Error: {e}")
                files_skipped += 1

        logging.info("--- Organization Complete ---")
        logging.info(f"Total files moved: {files_moved}")
        logging.info(f"Total files skipped: {files_skipped}")


# --- Execution Block ---
# This allows the script to be run directly.
# It serves as the entry point for your execution.
if __name__ == "__main__":
    # IMPORTANT: Replace this path with the actual directory you want to organize.
    # For example: 'C:/Users/YourUser/Downloads' or '/home/youruser/Desktop/TestFolder'
    # For safety, I recommend creating a test folder with some dummy files first.
    directory_to_organize = "C:/Path/To/Your/Test/Folder"

    try:
        # Create an instance of our organizer and run it.
        organizer = FileOrganizer(directory_to_organize)
        organizer.organize_files()
    except ValueError as ve:
        # We handle our custom errors gracefully.
        logging.error(ve)
    except Exception as e:
        # A general catch-all for any other unforeseen issues.
        logging.error(f"An unexpected error occurred: {e}")