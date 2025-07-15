# In this script, we will implement a simple web crawler that fetches data from GitHub and all the repositories related to reinforcement learning.
# The crawler will extract repository names, descriptions, and URLs. and automatically download the repo in a indicated folder.
import os
from github import Github
from github import RateLimitExceededException
import git
import time
import datetime
from tqdm import tqdm
import csv
import shutil


# --- Configuration ---
# Your GitHub Personal Access Token. It's best to load this from an environment variable.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# The search query to find relevant repositories.
# The folder where repositories will be downloaded.
DOWNLOAD_FOLDER = "/home/lee/code/Eureka/dataprocess/data"
REPO_LIST = "/home/lee/code/Eureka/dataprocess/repo_list.csv"

# init: delete the contents in DOWNLOAD_FOLDER and delete the REPO_LIST
# Delete all contents in DOWNLOAD_FOLDER
# if os.path.exists(DOWNLOAD_FOLDER):
#     for item in os.listdir(DOWNLOAD_FOLDER):
#         item_path = os.path.join(DOWNLOAD_FOLDER, item)
#         if os.path.isdir(item_path):
#             shutil.rmtree(item_path)
#         else:
#             os.remove(item_path)
# else:
#     os.makedirs(DOWNLOAD_FOLDER)

# # Delete the REPO_LIST file if it exists
# if os.path.exists(REPO_LIST):
#     os.remove(REPO_LIST)

def search_github_repos(api):
    """
    Searches GitHub for repositories based on the query and handles rate limiting.
    """
    try:
        print(f"🔎 Searching GitHub for reinforcement learning repositories...")
        if not os.path.exists(REPO_LIST):
            repo_list = []
        else:
            # Load existing repositories from the CSV file to avoid duplicates
            with open(REPO_LIST, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                repo_list = [row for row in reader]
        
        # Break down search by date ranges to handle GitHub's 1000 result limitation
        start_date = datetime.datetime(2021, 7, 1)
        end_date = datetime.datetime(2025, 7, 1)
        current_date = start_date
        
        # Use 2-month intervals for search to stay under result limits
        interval = datetime.timedelta(days=30)
        
        while current_date < end_date:
            next_date = min(current_date + interval, end_date)
            date_query = f"created:{current_date.strftime('%Y-%m-%d')}..{next_date.strftime('%Y-%m-%d')}"
            query = f"reinforcement-learning in:readme {date_query} size:<1000000 stars:>10"
            print(query)
            try:
                batch_repos = api.search_repositories(query=query, sort="stars", order="desc")
                
                for repo in batch_repos:
                    if api.get_rate_limit().search.remaining < 5:
                        reset_time = api.get_rate_limit().search.reset
                        # Fix: make utcnow aware
                        now_aware = datetime.datetime.now(datetime.timezone.utc)
                        sleep_time = (reset_time - now_aware).total_seconds()
                        print(f"⚠️ API rate limit almost reached. Waiting {sleep_time:.0f} seconds...")
                        time.sleep(max(1, sleep_time))
                        
                    repo_info = {
                        "name": repo.name,
                        "description": repo.description,
                        "url": repo.clone_url
                    }
                    
                    # Skip if already in list (avoid duplicates)
                    if any(r["url"] == repo_info["url"] for r in repo_list):
                        continue
                        
                    repo_list.append(repo_info)
                    
                    # Save to CSV
                    csv_file = REPO_LIST
                    file_exists = os.path.isfile(csv_file)
                    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=["name", "description", "url"])
                        if not file_exists:
                            writer.writeheader()
                        writer.writerow(repo_info)
                    
                    # Download repo
                    # download_single_repo(repo.name, repo.clone_url, DOWNLOAD_FOLDER)
                    
                    time.sleep(.1)  # Sleep for 2.1 seconds to stay under GitHub's 30 requests/minute search API limit
                    
            except RateLimitExceededException:
                reset_time = api.get_rate_limit().search.reset
                # Fix: make utcnow aware
                now_aware = datetime.datetime.now(datetime.timezone.utc)
                sleep_time = (reset_time - now_aware).total_seconds()
                print(f"⚠️ Rate limit exceeded. Waiting {sleep_time:.0f} seconds...")
                time.sleep(max(1, sleep_time + 10))  # Add buffer time
            
            current_date = next_date
                
        print(f"✅ Found {len(repo_list)} repositories.")
        return repo_list
    except RateLimitExceededException:
        print("❌ GitHub API rate limit exceeded. Please wait and try again later.")
        return None
    except Exception as e:
        print(f"❌ An error occurred during search: {e}")
        return None


def download_single_repo(reponame, url, folder):
    """
    Downloads a single repository given its name and URL into the specified folder.
    Ensures the function runs for at least 2.1 seconds.
    """
    import time  # Ensure import is present at the top if not already
    min_duration = 2.1
    start_time = time.time()
    repo_path = os.path.join(folder, reponame)
    if os.path.exists(repo_path):
        print(f"👍 Repository '{reponame}' already exists at '{repo_path}'. Skipping.")
        time.sleep(min_duration)
    try:
        print(f"Cloning from {url} into {repo_path}...")
        git.Repo.clone_from(url, repo_path)
        print(f"✅ Successfully cloned '{reponame}'.")
    except git.exc.GitCommandError as e:
        print(f"❌ Failed to clone '{reponame}'. Error: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred while cloning '{reponame}': {e}")
    # Ensure minimum duration
    elapsed = time.time() - start_time
    if elapsed < min_duration:
        time.sleep(min_duration - elapsed)


# def download_repos(repos_to_download):
#     """
#     Downloads a list of repositories into the specified folder.
#     """
#     if not os.path.exists(DOWNLOAD_FOLDER):
#         print(f"📁 Creating download directory: {DOWNLOAD_FOLDER}")
#         os.makedirs(DOWNLOAD_FOLDER)

#     print(f"\n🚀 Starting download of {len(repos_to_download)} repositories...")
#     for i, repo in enumerate(repos_to_download):
#         repo_path = os.path.join(DOWNLOAD_FOLDER, repo['name'])
#         print(f"\n[{i+1}/{len(repos_to_download)}] Processing '{repo['name']}'...")

#         # Check if the repository is already downloaded.
#         if os.path.exists(repo_path):
#             print(f"👍 Repository '{repo['name']}' already exists. Skipping.")
#             continue

#         # Try to clone the repository.
#         try:
#             print(f"Cloning from {repo['url']}...")
#             git.Repo.clone_from(repo['url'], repo_path)
#             print(f"✅ Successfully cloned '{repo['name']}'.")
#         except git.exc.GitCommandError as e:
#             print(f"❌ Failed to clone '{repo['name']}'. Error: {e.stderr}")
#         except Exception as e:
#             print(f"An unexpected error occurred while cloning '{repo['name']}': {e}")


def main():
    """
    Main function to orchestrate the crawler.
    """
    if not GITHUB_TOKEN:
        print("❌ Error: GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return

    # Initialize the GitHub API client.
    g = Github(GITHUB_TOKEN)

    # Phase 1: Fetch repository information.
    all_repos = search_github_repos(g)

    if not all_repos:
        print("No repositories found or an error occurred. Exiting.")
        return

    # Phase 2: Confirm and download.
    print("\n--- Repository Fetch Complete ---")
    print(f"Found a total of {len(all_repos)} repositories.")

    # # Ask the user for confirmation before downloading.
    # user_input = input(f"Do you want to proceed with downloading them into the '{DOWNLOAD_FOLDER}' folder? (yes/no): ").lower()

    # if user_input in ["yes", "y"]:
    #     download_repos(all_repos)
    #     print("\n🎉 All downloads complete!")
    # else:
    #     print("Download cancelled by user. Exiting.")


if __name__ == "__main__":
    main()