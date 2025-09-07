import os
import shutil
import logging
import json
import argparse  # Import the argparse library for CLI functionality.
from pathlib import Path

# --- Configuration ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])


# --- Core Logic ---
class FileOrganizer:
    """
    Organizes files in a directory based on rules from an external config.json file.
    """

    def __init__(self, target_directory):
        """
        Initializes the FileOrganizer.

        Args:
            target_directory (str): The absolute path to the directory to be organized.
        """
        self.target_directory = Path(target_directory)
        if not self.target_directory.is_dir():
            raise ValueError(f"Error: The specified path '{target_directory}' is not a valid directory.")

        self.file_mappings = self._load_mappings()
        logging.info(f"FileOrganizer initialized for directory: {self.target_directory}")

    def _load_mappings(self):
        """
        Loads sorting rules from 'config.json' and inverts them for efficient lookup.
        """
        try:
            config_path = Path(__file__).parent / 'config.json'
            with open(config_path, 'r') as f:
                data = json.load(f)

            mappings = data.get("file_mappings", {})
            extension_to_category = {
                ext.lower(): category
                for category, extensions in mappings.items()
                for ext in extensions
            }
            logging.info("Successfully loaded and processed 'config.json'.")
            return extension_to_category
        except FileNotFoundError:
            logging.error("FATAL: 'config.json' not found. Ensure it exists in the same directory as the script.")
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

        for source_path in self.target_directory.iterdir():
            if source_path.is_dir():
                continue

            file_extension = source_path.suffix.lower()

            if not file_extension:
                logging.warning(f"Skipping file without extension: {source_path.name}")
                files_skipped += 1
                continue

            destination_folder_name = self.file_mappings.get(file_extension, 'Other')
            destination_path = self.target_directory / destination_folder_name

            destination_path.mkdir(exist_ok=True)

            destination_file_path = destination_path / source_path.name

            try:
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
# This block is now a command-line interface handler.
if __name__ == "__main__":
    # 1. Create the parser object.
    parser = argparse.ArgumentParser(
        description="Aperture: A smart file organizer.",
        epilog="Example: python organizer.py C:/Users/YourUser/Downloads"
    )

    # 2. Add the positional argument for the directory. 'help' provides user guidance.
    parser.add_argument(
        "directory",
        type=str,
        help="The target directory to organize."
    )

    # 3. Parse the arguments provided by the user.
    args = parser.parse_args()

    # 4. Use the parsed directory.
    directory_to_organize = args.directory

    try:
        organizer = FileOrganizer(directory_to_organize)
        organizer.organize_files()
    except (ValueError, FileNotFoundError) as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")