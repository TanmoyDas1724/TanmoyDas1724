import os
import json
import urllib.request
from datetime import date, timedelta


USERNAME = "TanmoyDas1724"
TOKEN = os.environ["GH_TOKEN"]


# GitHub GraphQL API
query = """
query($from: DateTime!, $to: DateTime!) {
  user(login: "TanmoyDas1724") {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        restrictedContributionsCount
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


today = date.today()

# Look back 1 year
start_date = today - timedelta(days=365)

variables = {
    "from": f"{start_date}T00:00:00Z",
    "to": f"{today}T23:59:59Z"
}


payload = json.dumps({
    "query": query,
    "variables": variables
}).encode("utf-8")


request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "TanmoyDas1724-streak"
    },
    method="POST"
)


with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))


if "errors" in result:
    raise RuntimeError(result["errors"])


calendar = (
    result["data"]
    ["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)


total_contributions = calendar["totalContributions"]
private_contributions = calendar["restrictedContributionsCount"]


# ---------------------------------------
# Collect contribution days
# ---------------------------------------

days = {}

for week in calendar["weeks"]:
    for contribution_day in week["contributionDays"]:

        day = contribution_day["date"]
        count = contribution_day["contributionCount"]

        days[day] = count


# ---------------------------------------
# Calculate current streak
# ---------------------------------------

current_day = today

# If today has no contribution yet,
# start checking from yesterday.
if days.get(current_day.isoformat(), 0) == 0:
    current_day -= timedelta(days=1)


streak = 0

while days.get(current_day.isoformat(), 0) > 0:
    streak += 1
    current_day -= timedelta(days=1)


# ---------------------------------------
# Print diagnostic information
# ---------------------------------------

print("====================================")
print("       GITHUB CODING STREAK")
print("====================================")

print(f"Username: {USERNAME}")
print(f"Total contributions: {total_contributions}")
print(f"Private contributions: {private_contributions}")
print(f"Current streak: {streak} days")

print("")
print("Recent contribution days:")

check_day = today

for _ in range(15):

    day_string = check_day.isoformat()
    count = days.get(day_string, 0)

    print(f"{day_string}: {count} contributions")

    check_day -= timedelta(days=1)


print("====================================")


# ---------------------------------------
# Generate SVG
# ---------------------------------------

svg = f'''<svg width="700" height="220"
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
    font-family="Arial, sans-serif"
    font-size="24"
    fill="#ffffff">
🔥 CODING STREAK
</text>

<text
    x="350"
    y="125"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="58"
    font-weight="bold"
    fill="#ff7b72">
{streak} DAYS
</text>

<text
    x="350"
    y="165"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="18"
    fill="#c9d1d9">
Public + Private Contributions
</text>

<text
    x="350"
    y="195"
    text-anchor="middle"
    font-family="Arial, sans-serif"
    font-size="14"
    fill="#8b949e">
Tanmoy Das • Keep building. Keep learning.
</text>

</svg>
'''


with open("streak.svg", "w", encoding="utf-8") as file:
    file.write(svg)


print(f"Generated streak.svg with {streak} days.")
