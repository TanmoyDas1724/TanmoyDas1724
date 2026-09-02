import os
import json
import urllib.request
from datetime import date, timedelta


USERNAME = "TanmoyDas1724"
TOKEN = os.environ["GH_TOKEN"]

today = date.today()
start_date = today - timedelta(days=365)


query = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions

        weeks {
          contributionDays {
            date
            contributionCount
            restrictedContributionCount
          }
        }
      }
    }
  }
}
"""


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
        "User-Agent": USERNAME
    }
)


with urllib.request.urlopen(request) as response:
    result = json.load(response)


if "errors" in result:
    raise RuntimeError(result["errors"])


calendar = (
    result["data"]["viewer"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)


# --------------------------------------------
# Build daily contribution data
# --------------------------------------------

days = {}

for week in calendar["weeks"]:

    for contribution_day in week["contributionDays"]:

        day = contribution_day["date"]

        public_count = contribution_day["contributionCount"]

        private_count = contribution_day.get(
            "restrictedContributionCount", 0
        )

        total_count = public_count + private_count

        days[day] = total_count


# --------------------------------------------
# Calculate current streak
# --------------------------------------------

streak = 0
current = today


# If there is no contribution recorded today yet,
# start checking from yesterday.

if days.get(current.isoformat(), 0) == 0:
    current -= timedelta(days=1)


while days.get(current.isoformat(), 0) > 0:

    streak += 1

    current -= timedelta(days=1)


# --------------------------------------------
# Print diagnostic information
# --------------------------------------------

print("====================================")
print("        GITHUB CODING STREAK")
print("====================================")

print(f"Username: {USERNAME}")

print(
    f"Total contributions: "
    f"{calendar['totalContributions']}"
)

print(f"Current streak: {streak} days")

print("")

print("Last 10 days:")

check_day = today

for _ in range(10):

    day_string = check_day.isoformat()

    count = days.get(day_string, 0)

    print(f"{day_string}: {count}")

    check_day -= timedelta(days=1)

print("====================================")


# --------------------------------------------
# Generate SVG
# --------------------------------------------

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
