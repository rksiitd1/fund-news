import requests
from bs4 import BeautifulSoup

url = "https://inc42.com/buzz/from-finnable-to-bombay-shaving-company-indian-startups-raised-163-mn-this-week/"

# Extract slug and first 4 words
slug = url.rstrip("/").split("/")[-1]
first4 = "_".join(slug.split("-")[:4])
md_filename = f"{first4}.md"

response = requests.get(url)
response.raise_for_status()
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

# Clean up unwanted tags
for tag in soup(["script", "style", "header", "footer", "nav"]):
    tag.extract()

# Extract headline
headline = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""

# Try to extract core content
main_content = ""
for selector in ["article", "div.article", "div.single-article", "div.content"]:
    container = soup.select_one(selector)
    if container:
        main_content = container.get_text(separator="\n", strip=True)
        break
if not main_content:
    paragraphs = soup.find_all("p")
    main_content = "\n".join(p.get_text(strip=True) for p in paragraphs)

# Format markdown
md_text = f"# {headline}\n\n{main_content}"

# Save as .md file
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(md_text)

print(f"Markdown file saved as {md_filename}")
