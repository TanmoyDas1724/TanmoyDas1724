import os
import requests
from datetime import datetime, date, timedelta

USERNAME = "TanmoyDas1724"
STREAK_FILE = "streak_data.txt"
START_STREAK = 68

TOKEN = os.environ["GH_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_repositories():
    """Get public + private repositories accessible by the token."""

    repos = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/user/repos"
            f"?per_page=100&page={page}&affiliation=owner,collaborator"
        )

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            raise Exception(
                f"Failed to get repositories: "
                f"{response.status_code} {response.text}"
            )

        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


def get_commit_dates(repo):
    """Get dates on which the user made commits."""

    owner = repo["owner"]["login"]
    name = repo["name"]

    url = (
        f"https://api.github.com/repos/{owner}/{name}/commits"
        f"?author={USERNAME}&per_page=100"
    )

    dates = set()
    page = 1

    while True:

        url = (
            f"https://api.github.com/repos/{owner}/{name}/commits"
            f"?author={USERNAME}&per_page=100&page={page}"
        )

        response = requests.get(url, headers=HEADERS)

        if response.status_code == 409:
            break

        if response.status_code != 200:
            print(f"Skipping {name}: {response.status_code}")
            break

        commits = response.json()

        if not commits:
            break

        for commit in commits:

            author = commit.get("commit", {}).get("author", {})

            commit_date = author.get("date")

            if commit_date:
                dt = datetime.fromisoformat(
                    commit_date.replace("Z", "+00:00")
                )

                dates.add(dt.date())

        page += 1

        # Prevent unnecessary API calls
        if page > 10:
            break

    return dates


def load_data():

    if not os.path.exists(STREAK_FILE):
        return START_STREAK, None

    with open(STREAK_FILE, "r") as f:
        lines = f.read().strip().splitlines()

    streak = int(lines[0])
    last_active = date.fromisoformat(lines[1])

    return streak, last_active


def save_data(streak, last_active):

    with open(STREAK_FILE, "w") as f:
        f.write(f"{streak}\n")
        f.write(str(last_active))


# ------------------------------------------------
# GET ALL COMMIT DAYS
# ------------------------------------------------

print("Getting repositories...")

repositories = get_repositories()

print(f"Found {len(repositories)} repositories.")


commit_days = set()

for repo in repositories:

    print(f"Checking {repo['full_name']}")

    dates = get_commit_dates(repo)

    commit_days.update(dates)


print(f"Found {len(commit_days)} active commit days.")


# ------------------------------------------------
# CALCULATE STREAK
# ------------------------------------------------

today = date.today()

streak, last_active = load_data()


# First run
if last_active is None:

    if today in commit_days:
        last_active = today
        print("Today has a commit.")
    else:
        print("No commit today.")

else:

    # Already processed today
    if today == last_active:
        print("Already processed today.")

    # Consecutive day
    elif today == last_active + timedelta(days=1):

        if today in commit_days:
            streak += 1
            last_active = today
            print("🔥 Consecutive commit day!")

        else:
            print("No commit today. Waiting for next commit.")

    # Missed one or more days
    elif today > last_active + timedelta(days=1):

        if today in commit_days:
            streak = 1
            last_active = today
            print("❌ Streak broken. Starting again from 1.")

        else:
            print("No commit today. Streak remains unchanged.")


save_data(streak, last_active)


# ------------------------------------------------
# CREATE SVG
# ------------------------------------------------

svg = f"""<svg width="700" height="220"
viewBox="0 0 700 220"
xmlns="http://www.w3.org/2000/svg">

<rect
    width="700"
    height="220"
    rx="20"
    fill="#0d1117"/>

<text
    x="350"
    y="55"
    text-anchor="middle"
    font-family="Arial"
    font-size="24"
    fill="white">
🔥 CODING STREAK
</text>

<text
    x="350"
    y="125"
    text-anchor="middle"
    font-family="Arial"
    font-size="58"
    font-weight="bold"
    fill="#ff7b72">
{streak} DAYS
</text>

<text
    x="350"
    y="165"
    text-anchor="middle"
    font-family="Arial"
    font-size="18"
    fill="#c9d1d9">
Public + Private Commits
</text>

<text
    x="350"
    y="195"
    text-anchor="middle"
    font-family="Arial"
    font-size="14"
    fill="#8b949e">
Tanmoy Das • Keep building. Keep learning.
</text>

</svg>
"""

with open("streak.svg", "w", encoding="utf-8") as f:
    f.write(svg)


print(f"\n🔥 CURRENT STREAK: {streak} DAYS")
print(f"Last active day: {last_active}")
