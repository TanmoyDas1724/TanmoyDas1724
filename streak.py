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

calendar = result["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]

days = {}

for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days[day["date"]] = day["contributionCount"]


# Calculate current streak
streak = 0
current_day = today

while True:
    day_string = current_day.isoformat()

    if days.get(day_string, 0) > 0:
        streak += 1
        current_day -= timedelta(days=1)
    else:
        break


# If today has no contribution yet, allow yesterday's streak
if streak == 0:
    yesterday = today - timedelta(days=1)

    if days.get(yesterday.isoformat(), 0) > 0:
        current_day = yesterday
        streak = 0

        while days.get(current_day.isoformat(), 0) > 0:
            streak += 1
            current_day -= timedelta(days=1)


svg = f'''<svg width="700" height="220" viewBox="0 0 700 220"
xmlns="http://www.w3.org/2000/svg">

<rect width="700" height="220" rx="20"
fill="#0d1117"/>

<text x="350" y="55"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="24"
fill="#ffffff">
🔥 CODING STREAK
</text>

<text x="350" y="125"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="58"
font-weight="bold"
fill="#ff7b72">
{streak} DAYS
</text>

<text x="350" y="165"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="18"
fill="#c9d1d9">
Public + Private Contributions
</text>

<text x="350" y="195"
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

print(f"Current streak: {streak} days")
