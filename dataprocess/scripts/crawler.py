# In this script, we will implement a simple web crawler that fetches data from GitHub and all the repositories related to reinforcement learning.
# The crawler will extract repository names, descriptions, and URLs. and automatically download the repo in a indicated folder.
import os
from github import Github
from github import RateLimitExceededException
import git
import time

# --- Configuration ---
# Your GitHub Personal Access Token. It's best to load this from an environment variable.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# The search query to find relevant repositories.
SEARCH_QUERY = "learning stars:>20"
# The folder where repositories will be downloaded.
DOWNLOAD_FOLDER = "/home/lee/code/Eureka/dataprocess/data"

def search_github_repos(api):
    """
    Searches GitHub for repositories based on the query and handles rate limiting.
    """
    print("🔎 Starting GitHub repository search...")
    try:
        # Search for repositories with the specified topic.
        # The 'sort' and 'order' parameters help in getting popular repos first.
        repositories = api.search_repositories(query=SEARCH_QUERY, sort="stars", order="desc")
        # Output the total number of repositories found and ask for confirmation before proceeding.
        total_count = repositories.totalCount
        print(f"🔢 Total repositories matching query: {total_count}")
        confirm = input("Do you want to proceed with crawling these repositories? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Crawl cancelled by user. Exiting search.")
            return []
        repo_list = []
        for repo in repositories:
            repo_list.append({
                "name": repo.name,
                "description": repo.description,
                "url": repo.clone_url
            })
            # A small delay to be respectful to the API.
            time.sleep(0.1)
        print(f"✅ Found {len(repo_list)} repositories.")
        return repo_list
    except RateLimitExceededException:
        print("❌ GitHub API rate limit exceeded. Please wait and try again later.")
        return None
    except Exception as e:
        print(f"An error occurred during search: {e}")
        return None


def download_repos(repos_to_download):
    """
    Downloads a list of repositories into the specified folder.
    """
    if not os.path.exists(DOWNLOAD_FOLDER):
        print(f"📁 Creating download directory: {DOWNLOAD_FOLDER}")
        os.makedirs(DOWNLOAD_FOLDER)

    print(f"\n🚀 Starting download of {len(repos_to_download)} repositories...")
    for i, repo in enumerate(repos_to_download):
        repo_path = os.path.join(DOWNLOAD_FOLDER, repo['name'])
        print(f"\n[{i+1}/{len(repos_to_download)}] Processing '{repo['name']}'...")

        # Check if the repository is already downloaded.
        if os.path.exists(repo_path):
            print(f"👍 Repository '{repo['name']}' already exists. Skipping.")
            continue

        # Try to clone the repository.
        try:
            print(f"Cloning from {repo['url']}...")
            git.Repo.clone_from(repo['url'], repo_path)
            print(f"✅ Successfully cloned '{repo['name']}'.")
        except git.exc.GitCommandError as e:
            print(f"❌ Failed to clone '{repo['name']}'. Error: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred while cloning '{repo['name']}': {e}")


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

    # Ask the user for confirmation before downloading.
    user_input = input(f"Do you want to proceed with downloading them into the '{DOWNLOAD_FOLDER}' folder? (yes/no): ").lower()

    if user_input in ["yes", "y"]:
        download_repos(all_repos)
        print("\n🎉 All downloads complete!")
    else:
        print("Download cancelled by user. Exiting.")


if __name__ == "__main__":
    main()