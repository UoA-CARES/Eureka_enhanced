# In this script, we will implement a multithreading downloader that cloning data from Github 
# based on the dataprocess/repo_list.csv url in to the folder: /home/lee/code/Eureka/dataprocess/data
# After each download, it will delete all the files inside the folder that larger than 10KB.

import os
import csv
import subprocess
import threading
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Constants
REPO_LIST_PATH = '/home/lee/code/Eureka/dataprocess/repo_list.csv'
OUTPUT_DIR = '/home/lee/code/Eureka/dataprocess/data'
MAX_FILE_SIZE = 50 * 1024  # 50KB in bytes
MAX_WORKERS =8  # Number of concurrent downloads

def ensure_dir_exists(dir_path):
    """Ensure that the specified directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def clone_repository(repo_url):
    """Clone a repository from GitHub to the target directory."""
    try:
        # Create a unique subdirectory for this repository
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_dir = os.path.join(OUTPUT_DIR, repo_name)
        
        # Remove directory if it already exists
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        
        # Clone the repository
        # print(f"Cloning {repo_url} to {repo_dir}...")
        subprocess.run(['git', 'clone', repo_url, repo_dir], check=True)
        
        # Clean up large files
        cleanup_large_files(repo_dir)
        
        # print(f"Successfully processed {repo_url}")
        return True
    except Exception as e:
        print(f"Error processing {repo_url}: {str(e)}")
        return False

def cleanup_large_files(directory):
    """Remove all files larger than MAX_FILE_SIZE from the directory."""
    print(f"Cleaning up large files in {directory}...")
    file_count = 0
    
    # Remove .git folder if it exists
    git_dir = os.path.join(directory, '.git')
    if os.path.exists(git_dir) and os.path.isdir(git_dir):
        try:
            shutil.rmtree(git_dir)
            print(f"Removed .git directory from {directory}")
        except Exception as e:
            print(f"Error removing .git directory: {str(e)}")
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    os.remove(file_path)
                    file_count += 1
            except Exception as e:
                print(f"Error removing file {file_path}: {str(e)}")
    
    print(f"Removed {file_count} files larger than {MAX_FILE_SIZE/1024}KB")

def read_repo_list():
    """Read the list of repositories from the CSV file."""
    repos = []
    try:
        with open(REPO_LIST_PATH, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row (name,description,url)
            for row in reader:
                if row and len(row) >= 3:  # Ensure we have at least 3 columns
                    repos.append(row[2].strip())  # URL is in the third column
    except Exception as e:
        print(f"Error reading repository list: {str(e)}")
    
    return repos

def main():
    """Main function to coordinate the download process."""
    print("Starting GitHub repository downloader...")
    
    # Ensure output directory exists
    ensure_dir_exists(OUTPUT_DIR)
    
    # Read repository list
    repos = read_repo_list()
    print(f"Found {len(repos)} repositories to process")
    
    # Download repositories in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(clone_repository, repos)
    
    print("All repositories processed.")

if __name__ == "__main__":
    main()