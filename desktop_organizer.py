import os
import shutil
from PIL import Image

def get_desktop_path():
    """Gets the path to the user's desktop, returning None if not on Windows."""
    if os.name != 'nt':
        print("This script is intended to be run on Windows.")
        return None
    return os.path.join(os.path.expanduser('~'), 'Desktop')

# Central configuration for file types and their destinations
FILE_TYPE_MAPPINGS = {
    'img_bin': ['.jpg', '.png', '.gif'],
    'pdf_bin': ['.pdf'],
    'html_bin': ['.html'],
    'adobe_bin': ['.ai', '.psd'],
    'vect_bin': ['.svg'],
    'txt_bin': ['.txt'],
}

def create_destination_folders(desktop_path, mappings):
    """Creates the destination folders on the desktop if they don't already exist."""
    print("\nCreating destination folders...")
    all_folder_names = set(list(mappings.keys()) + ['img_bin'])
    for folder_name in all_folder_names:
        folder_path = os.path.join(desktop_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"  - Created folder: {folder_path}")
        else:
            print(f"  - Folder already exists: {folder_path}")

def handle_webp_file(desktop_path, filename):
    """Converts a .webp file to .png and moves both files to the img_bin folder."""
    print(f"  - Handling .webp file: {filename}")
    webp_path = os.path.join(desktop_path, filename)
    png_filename = os.path.splitext(filename)[0] + '.png'
    png_path = os.path.join(desktop_path, png_filename)

    img_bin_path = os.path.join(desktop_path, 'img_bin')

    try:
        with Image.open(webp_path) as img:
            img.save(png_path, 'PNG')
            print(f"    - Converted '{filename}' to '{png_filename}'")

        shutil.move(webp_path, os.path.join(img_bin_path, filename))
        print(f"    - Moved '{filename}' to 'img_bin'")
        shutil.move(png_path, os.path.join(img_bin_path, png_filename))
        print(f"    - Moved '{png_filename}' to 'img_bin'")

    except Exception as e:
        print(f"    - Error processing '{filename}': {e}")

def scan_and_move_files(desktop_path, mappings):
    """Scans the desktop for files and moves them to their designated folders."""
    print("\nScanning and moving files...")
    for item_name in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item_name)

        if not os.path.isfile(item_path):
            continue

        if item_name.lower() in ['desktop_organizer.py', 'requirements.txt']:
            continue

        file_extension = os.path.splitext(item_name)[1].lower()

        if file_extension == '.webp':
            handle_webp_file(desktop_path, item_name)
            continue

        moved = False
        for folder_name, extensions in mappings.items():
            if file_extension in extensions:
                destination_folder_path = os.path.join(desktop_path, folder_name)
                shutil.move(item_path, os.path.join(destination_folder_path, item_name))
                print(f"  - Moved '{item_name}' to '{folder_name}'")
                moved = True
                break

        if not moved:
            all_target_extensions = [ext for exts in mappings.values() for ext in exts] + ['.webp']
            if file_extension in all_target_extensions:
                 print(f"  - Skipped '{item_name}' (already in a folder or other issue)")

def main():
    """Main function to run the desktop organization script."""
    desktop_path = get_desktop_path()
    if not desktop_path:
        return

    print("--- Starting Desktop Organization Script ---")
    print(f"Scanning Desktop at: {desktop_path}")

    create_destination_folders(desktop_path, FILE_TYPE_MAPPINGS)
    scan_and_move_files(desktop_path, FILE_TYPE_MAPPINGS)

    print("\n--- Desktop organization complete. ---")

if __name__ == "__main__":
    main()
