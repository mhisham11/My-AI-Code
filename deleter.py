import os
import tkinter as tk
from tkinter import filedialog

def get_folder_path():
    """Opens a window for the user to select a folder."""
    # Create a dummy window and hide it immediately
    root = tk.Tk()
    root.withdraw()
    
    # Open the folder selection dialog
    folder_path = filedialog.askdirectory(title="Select the folder to clean")
    return folder_path

def main():
    print("--- Python File Deleter ---")
    
    # 1. Ask user to select a folder
    print("Opening folder selection window...")
    folder = get_folder_path()
    
    if not folder:
        print("No folder selected. Canceling operation.")
        return

    print(f"\nSelected Folder: {folder}")
    
    # 2. Ask for the extension
    ext = input("Enter the file extension you want to delete (e.g., .txt, .log): ").strip().lower()
    
    if not ext:
        print("No extension provided. Canceling operation.")
        return
        
    # Ensure it starts with a dot
    if not ext.startswith('.'):
        ext = '.' + ext

    # 3. Find matching files
    files_to_delete = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(ext):
            full_path = os.path.join(folder, filename)
            # Make sure it's a file, not a folder that happens to end with the extension
            if os.path.isfile(full_path): 
                files_to_delete.append(full_path)

    # 4. Handle results
    if not files_to_delete:
        print(f"\nGood news! No files ending in '{ext}' were found in that folder.")
        return

    print(f"\nFound {len(files_to_delete)} file(s) to delete:")
    for file in files_to_delete:
        print(f" - {os.path.basename(file)}")

    # 5. Final Confirmation
    print("\nWARNING: These files will be PERMANENTLY deleted (bypassing the Recycle Bin).")
    confirm = input(f"Are you absolutely sure you want to delete these {len(files_to_delete)} files? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        deleted_count = 0
        for file in files_to_delete:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {os.path.basename(file)}: {e}")
                
        print(f"\nSuccess: {deleted_count} file(s) permanently deleted.")
    else:
        print("\nOperation canceled. Your files are safe.")

if __name__ == "__main__":
    main()