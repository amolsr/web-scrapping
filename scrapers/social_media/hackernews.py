# Import required packages (must be preinstalled on self-hosted n8n)
import simplejson as json
from bs4 import BeautifulSoup

# Get the HTML content from the input
html_content = items[0].get('json', {}).get('data', '')

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Store metadata of GitHub posts
github_posts = []

# Find all 'tr' elements with class 'athing submission'
posts = soup.find_all('tr', class_='athing submission')

for post in posts:
    post_id = post.get('id')
    title_line = post.find('span', class_='titleline')
    if not title_line:
        continue

    # Extract the title and URL
    title_tag = title_line.find('a')
    if not title_tag:
        continue

    title = title_tag.get_text(strip=True)
    url = title_tag.get('href', '')

    # Only include GitHub links
    if 'github.com' not in url.lower():
        continue

    # Extract the domain (optional)
    site_bit = title_line.find('span', class_='sitebit comhead')
    site = site_bit.find('span', class_='sitestr').get_text(strip=True) if site_bit else ''

    # Get the 'subtext' row (next sibling row)
    subtext_tr = post.find_next_sibling('tr')
    if not subtext_tr:
        continue

    subtext_td = subtext_tr.find('td', class_='subtext')
    if not subtext_td:
        continue

    # Extract score, author, age, and comments
    score_span = subtext_td.find('span', class_='score')
    score = score_span.get_text(strip=True) if score_span else '0 points'

    author_a = subtext_td.find('a', class_='hnuser')
    author = author_a.get_text(strip=True) if author_a else 'unknown'

    age_span = subtext_td.find('span', class_='age')
    age_a = age_span.find('a') if age_span else None
    age = age_a.get_text(strip=True) if age_a else 'unknown'

    comments_a_list = subtext_td.find_all('a')
    comments_a = comments_a_list[-1] if comments_a_list else None
    comments_text = comments_a.get_text(strip=True) if comments_a else '0 comments'

    # Construct the Hacker News URL
    hn_url = f"https://news.ycombinator.com/item?id={post_id}"

    # Store post metadata
    post_metadata = {
        'Post': post_id,
        'title': title,
        'url': url,
        'site': site,
        'score': score,
        'author': author,
        'age': age,
        'comments': comments_text,
        'hn_url': hn_url
    }

    print(post_metadata)


