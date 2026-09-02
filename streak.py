import re
import urllib.request
from datetime import datetime, timedelta

USERNAME = "TanmoyDas1724"

# GitHub's contribution calendar endpoint
url = f"https://github.com/users/{USERNAME}/contributions"

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(request) as response:
    html = response.read().decode("utf-8")


# Extract contribution dates and contribution levels
matches = re.findall(
    r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"',
    html
)

if not matches:
    # GitHub may put data-level before data-date
    matches = re.findall(
        r'data-level="(\d+)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"',
        html
    )

    matches = [
        (date, level)
        for level, date in matches
    ]


if not matches:
    raise RuntimeError(
        "Could not read GitHub contribution calendar."
    )


days = {}

for date_string, level in matches:
    days[date_string] = int(level)


# ---------------------------------------
# Calculate current streak
# ---------------------------------------

today = datetime.now().date()

streak = 0
current = today

# If GitHub hasn't updated today's contribution yet,
# start from yesterday.
if days.get(current.isoformat(), 0) == 0:
    current -= timedelta(days=1)


while days.get(current.isoformat(), 0) > 0:
    streak += 1
    current -= timedelta(days=1)


# ---------------------------------------
# Diagnostic output
# ---------------------------------------

print("====================================")
print("       GITHUB CODING STREAK")
print("====================================")

print(f"Username: {USERNAME}")
print(f"Current streak: {streak} days")

print("")
print("Recent contribution days:")

check_day = today

for _ in range(15):

    date_string = check_day.isoformat()
    count_level = days.get(date_string, 0)

    print(
        f"{date_string}: level {count_level}"
    )

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
