from selenium import webdriver
from bs4 import BeautifulSoup
import time

url = "https://inc42.com/buzz/from-finnable-to-bombay-shaving-company-indian-startups-raised-163-mn-this-week/"
slug = url.rstrip("/").split("/")[-1]
first4 = "_".join(slug.split("-")[:4])
md_filename = f"{first4}.md"

# Start Chrome
driver = webdriver.Chrome()
driver.get(url)
time.sleep(5)  # Give JS time to load

html_content = driver.page_source
driver.quit()

soup = BeautifulSoup(html_content, "html.parser")

# Remove common clutter
for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'noscript']):
    tag.decompose()

# Extract headline/title
headline = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""

# Extract summary (usually a set of <li> or opening bold <p>)
summary = ""
summary_ul = soup.find("ul")
if summary_ul:
    summary_list = [li.get_text(strip=True) for li in summary_ul.find_all("li")]
    summary += "\n".join(f"- {item}" for item in summary_list)

# Extract main content (all paragraphs)
main_content = []
for p in soup.find_all("p"):
    txt = p.get_text(strip=True)
    if txt and len(txt) > 30 and "share" not in txt.lower():  # Filter short or irrelevant text
        main_content.append(txt)

# Extract tables (deal table)
table = soup.find("table")
table_md = ""
if table:
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    table_md += "| " + " | ".join(headers) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for tr in table.find_all("tr")[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cells:
            table_md += "| " + " | ".join(cells) + " |\n"

# Compose Markdown
md_text = f"# {headline}\n\n"
if summary:
    md_text += "**SUMMARY**\n" + summary + "\n\n"
if table_md:
    md_text += "**Funding Table**\n" + table_md + "\n"
if main_content:
    md_text += "\n".join(main_content)

# Save to markdown file
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(md_text)

print(f"Markdown saved as {md_filename}")
