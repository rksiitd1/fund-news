import requests
from bs4 import BeautifulSoup
import re

url = "https://inc42.com/buzz/from-finnable-to-bombay-shaving-company-indian-startups-raised-163-mn-this-week/"
slug = url.rstrip("/").split("/")[-1]
first4 = "_".join(slug.split("-")[:4])
md_filename = f"{first4}.md"

response = requests.get(url)
response.raise_for_status()
html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")

# Remove clutter
for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'noscript']):
    tag.decompose()

# Headline
headline = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""

# Byline/author and date
byline = ""
author = soup.find("a", href=re.compile("/author/"))
if author:
    author_name = author.get_text(strip=True)
    date_tag = author.find_previous("span")
    pub_date = date_tag.get_text(strip=True) if date_tag else ""
    byline = f"{pub_date} | By {author_name}"

# Find summary: summary could be in bullet points or first <ul> or summary div
summary_items = []
summary_ul = soup.find("ul")
if summary_ul:
    summary_items = [li.get_text(strip=True) for li in summary_ul.find_all("li")]
else:
    # fallback: find the first few <p> before the article body/table
    all_ps = soup.find_all("p")
    summary_items = [p.get_text(strip=True) for p in all_ps[:2]]

# Table extraction (deal table, as markdown)
table_md = ""
table = soup.find("table")
if table:
    # Markdown table header
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cells:
            rows.append("| " + " | ".join(cells) + " |")
    # Combine
    table_md += "| " + " | ".join(headers) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    table_md += "\n".join(rows)
else:
    # fallback to find and join tabulated info (if no table tag, grab by <p> containing dates)
    table_md = ""

# Extract rest of important blocks, paragraph by paragraph
content_blocks = []
reached_table = False
for tag in soup.find_all(["h2", "p", "li"]):
    txt = tag.get_text(strip=True)
    if not txt:
        continue
    # Skip social/share blocks
    if "share" in txt.lower() or "follow us" in txt.lower():
        continue
    # Recognize major sections by h2
    if tag.name == "h2":
        content_blocks.append(f"\n## {txt}\n")
    elif re.match(r"^\d{1,2} \w{3} \d{4}$", txt):  # dates/rows header in table region
        reached_table = True
        continue
    elif reached_table and tag.name == "p" and txt.startswith("Source:"):
        reached_table = False
        continue
    else:
        content_blocks.append(txt)

# Compose Markdown sections
md_content = f"# {headline}\n"
if byline.strip():
    md_content += f"\n*{byline}*\n"
if summary_items:
    md_content += "\n**SUMMARY**\n"
    for item in summary_items:
        md_content += f"- {item}\n"

if table_md:
    md_content += f"\n**Funding Table**\n{table_md}\n"

# Add rest of content
if content_blocks:
    md_content += "\n" + "\n\n".join(content_blocks)

# Save markdown file
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Saved article as '{md_filename}'")
