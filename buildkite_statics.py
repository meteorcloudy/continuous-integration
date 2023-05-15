import json
import requests
import datetime

""" Run python3 buildkite_statics.py > output and copy the content to a spreadsheet to analyze """

# Replace `YOUR_API_TOKEN` with your Buildkite API access token.
api_token = "YOUR_API_TOKEN"

# Replace `YOUR_ORGANIZATION` and `YOUR_PIPELINE` with the name of the organization and pipeline you want to query.
organization = "bazel"
pipeline = "bazel-bazel"

# Construct the URL for the API request.
url = f"https://api.buildkite.com/v2/organizations/{organization}/pipelines/{pipeline}/builds?state=passed"

# Set the API authentication headers.
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

MAX_PAGES = 20

def download_builds():
    page_number = 1
    while page_number <= MAX_PAGES:
        url = f"https://api.buildkite.com/v2/organizations/{organization}/pipelines/{pipeline}/builds?state=passed&page={page_number}&per_page=100"

        # Make the API request and parse the JSON response.
        response = requests.get(url, headers=headers)
        builds_for_page = response.json()

        # Dump the json file to a file
        with open(f"data/builds_{page_number}.json", "w") as f:
            json.dump(builds_for_page, f, indent=4)

        print("Downloaded " + str(page_number) + " pages of builds")
        page_number += 1

def get_wait_time_for_job(job):
    if 'started_at' not in job or 'scheduled_at' not in job:
        return 0
    return (datetime.datetime.fromisoformat(job["started_at"].replace('Z', '+00:00')) - datetime.datetime.fromisoformat(job["scheduled_at"].replace('Z', '+00:00'))).total_seconds()

def get_run_time_for_job(job):
    if 'started_at' not in job or 'finished_at' not in job:
        return 0
    return (datetime.datetime.fromisoformat(job["finished_at"].replace('Z', '+00:00')) - datetime.datetime.fromisoformat(job["started_at"].replace('Z', '+00:00'))).total_seconds()

def analyze():
    page_number = 1
    while page_number <= MAX_PAGES:
        # Load json file from a file
        f = open(f"data/builds_{page_number}.json", "r")
        builds_for_page = json.load(f)
        f.close()

        # Iterate over the builds on the current page.
        for build in builds_for_page:
            if build["state"] == "passed" and build["branch"] == "master":
                for job in build["jobs"]:
                    name = job.get("name", None)
                    if name == ":darwin: (OpenJDK 11, Xcode)":
                        print(job["created_at"] + "\t" + job["web_url"] + "\t" + str(get_wait_time_for_job(job)//60) + "\t" + str(int(get_run_time_for_job(job)//60)))
                        # print("\n\n+++ For job " + job["web_url"] + ":")
                        # print(name + " waited " + str(get_wait_time_for_job(job)) + " seconds" + ", ran for " + str(int(get_run_time_for_job(job)) // 60) + " minutes")

        page_number += 1

def main():
    # download_builds()
    analyze()

if __name__ == "__main__":
    main()
