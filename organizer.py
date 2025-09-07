import os
import shutil
import logging
import json  # Import the JSON module to handle the configuration file.
from pathlib import Path

# --- Configuration ---
# The logging system remains essential for transparent operation.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])


# --- Core Logic ---
class FileOrganizer:
    """
    Organizes files in a directory based on rules from an external config.json file.
    This demonstrates a more robust and flexible design.
    """

    def __init__(self, target_directory):
        """
        Initializes the FileOrganizer. It now also loads the configuration.

        Args:
            target_directory (str): The absolute path to the directory to be organized.
        """
        self.target_directory = Path(target_directory)
        if not self.target_directory.is_dir():
            raise ValueError(f"Error: The specified path '{target_directory}' is not a valid directory.")

        # The core of our evolution: loading rules from an external source.
        self.file_mappings = self._load_mappings()
        logging.info(f"FileOrganizer initialized for directory: {self.target_directory}")

    def _load_mappings(self):
        """
        Loads sorting rules from 'config.json' and inverts them for efficient lookup.
        This function makes the entire system dynamic.
        """
        try:
            config_path = Path(__file__).parent / 'config.json'
            with open(config_path, 'r') as f:
                data = json.load(f)

            mappings = data.get("file_mappings", {})
            # Invert the dictionary for efficient lookups: {'.ext': 'Category'}
            extension_to_category = {
                ext.lower(): category
                for category, extensions in mappings.items()
                for ext in extensions
            }
            logging.info("Successfully loaded and processed 'config.json'.")
            return extension_to_category
        except FileNotFoundError:
            logging.error("FATAL: 'config.json' not found. Cannot proceed.")
            raise
        except json.JSONDecodeError:
            logging.error("FATAL: 'config.json' is malformed. Please check its syntax.")
            raise

    def organize_files(self):
        """
        Executes the file organization process using the loaded mappings.
        """
        logging.info("Starting file organization process...")
        files_moved = 0
        files_skipped = 0

        # Iterate using the modern Path object for better cross-platform compatibility.
        for source_path in self.target_directory.iterdir():
            # We only process files, not directories created by us or others.
            if source_path.is_dir():
                continue

            file_extension = source_path.suffix.lower()

            if not file_extension:
                logging.warning(f"Skipping file without extension: {source_path.name}")
                files_skipped += 1
                continue

            # Determine destination category from our loaded mappings. Default is 'Other'.
            destination_folder_name = self.file_mappings.get(file_extension, 'Other')
            destination_path = self.target_directory / destination_folder_name

            # Create destination folder if it doesn't exist.
            destination_path.mkdir(exist_ok=True)

            destination_file_path = destination_path / source_path.name

            try:
                # The core action: moving the file.
                shutil.move(str(source_path), str(destination_file_path))
                logging.info(f"Moved: {source_path.name} -> {destination_folder_name}/")
                files_moved += 1
            except Exception as e:
                logging.error(f"Failed to move {source_path.name}. Error: {e}")
                files_skipped += 1

        logging.info("--- Organization Complete ---")
        logging.info(f"Total files moved: {files_moved}")
        logging.info(f"Total files skipped: {files_skipped}")


# --- Execution Block ---
if __name__ == "__main__":
    # IMPORTANT: Update this path to your test directory.
    # e.g., 'C:/Users/YourUser/Downloads' or '/home/youruser/Desktop/TestFolder'
    directory_to_organize = "C:/Path/To/Your/Test/Folder"

    try:
        organizer = FileOrganizer(directory_to_organize)
        organizer.organize_files()
    except (ValueError, FileNotFoundError) as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")