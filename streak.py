import urllib.request
import re
from datetime import datetime, timedelta, timezone

USERNAME = "TanmoyDas1724"

URL = f"https://github.com/{USERNAME}"

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(request) as response:
    html = response.read().decode("utf-8")


# GitHub's contribution calendar contains contribution-day elements.
# Extract dates and contribution levels from the profile page.

pattern = r'<td[^>]*data-date="([^"]+)"[^>]*data-level="([^"]+)"[^>]*>'

matches = re.findall(pattern, html)

days = {}

for date_string, level in matches:
    try:
        contribution_date = datetime.strptime(
            date_string, "%Y-%m-%d"
        ).date()

        days[contribution_date] = int(level)

    except ValueError:
        continue


if not days:
    raise RuntimeError(
        "Could not read GitHub contribution calendar."
    )


# GitHub's contribution level:
# 0 = no contribution
# 1-4 = contribution activity
#
# Calculate the current continuous streak.

today = datetime.now().date()


def has_contribution(day):
    return days.get(day, 0) > 0


# GitHub's calendar may not yet contain today's activity
# depending on timezone/update timing.
if has_contribution(today):
    current = today
else:
    current = today - timedelta(days=1)


streak = 0

while has_contribution(current):
    streak += 1
    current -= timedelta(days=1)


print("================================")
print("GitHub Coding Streak")
print("================================")
print(f"Days detected: {streak}")
print(f"Latest date checked: {today}")
print("================================")


# Generate SVG

svg = f'''<svg width="700" height="220"
viewBox="0 0 700 220"
xmlns="http://www.w3.org/2000/svg">

<rect width="700"
      height="220"
      rx="20"
      fill="#0d1117"/>

<text x="350"
      y="55"
      text-anchor="middle"
      font-family="Arial, sans-serif"
      font-size="24"
      fill="#ffffff">
🔥 CODING STREAK
</text>

<text x="350"
      y="125"
      text-anchor="middle"
      font-family="Arial, sans-serif"
      font-size="58"
      font-weight="bold"
      fill="#ff7b72">
{streak} DAYS
</text>

<text x="350"
      y="165"
      text-anchor="middle"
      font-family="Arial, sans-serif"
      font-size="18"
      fill="#c9d1d9">
Public + Private Contributions
</text>

<text x="350"
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
