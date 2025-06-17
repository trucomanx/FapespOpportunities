import requests
from bs4 import BeautifulSoup
import re

def get_open_opportunities(url = "https://fapesp.br/oportunidades/mais-recentes/"):
    """
    Retrieves the HTML of currently open opportunities from the FAPESP website.

    Parameters:
        url (str): The URL to fetch opportunities from. Default is the most recent opportunities page.

    Returns:
        list: A list of HTML strings, each representing an open opportunity (<li> element).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    ul = soup.find('ul', class_='list')
    if not ul:
        return []

    results = []
    for li in ul.find_all('li'):
        classes = li.get('class', [])
        if 'box_col' in classes and 'aberta' in classes:
            results.append(str(li))

    return results


def filter_grants_by_title(lista_li_html, contents):
    """
    Filters the list of opportunities by checking if their title contains any of the specified keywords.

    Parameters:
        lista_li_html (list): A list of <li> elements (as HTML strings).
        contents (set or list): Set of strings to search for in the opportunity titles.

    Returns:
        list: Filtered list of <li> HTML strings matching the title criteria.
    """
    if len(contents) == 0:
        return lista_li_html

    filtered_result = []

    for li_html in lista_li_html:
        soup = BeautifulSoup(li_html, 'html.parser')
        title_tag = soup.find('strong', class_='title')
        if title_tag:
            title_text = title_tag.get_text()
            if any(keyword in title_text for keyword in contents):
                filtered_result.append(li_html)

    return filtered_result


def filter_grants_by_content(lista_li_html, contents):
    """
    Filters the list of opportunities by checking if their full text contains any of the specified keywords.

    Parameters:
        lista_li_html (list): A list of <li> elements (as HTML strings).
        contents (set or list): Set of strings to search for in the full opportunity text.

    Returns:
        list: Filtered list of <li> HTML strings matching the content criteria.
    """
    if len(contents) == 0:
        return lista_li_html

    search_words = {word.lower() for word in contents}
    filtered_result = []

    for li_html in lista_li_html:
        text = BeautifulSoup(li_html, 'html.parser').get_text().lower()
        if any(word in text for word in search_words):
            filtered_result.append(li_html)

    return filtered_result


def parse_opportunity(li_html, base_url="https://fapesp.br"):
    """
    Extracts structured data from a single HTML opportunity block.

    Parameters:
        li_html (str): HTML string representing an opportunity.
        base_url (str): The base URL to complete relative links.

    Returns:
        dict: A dictionary containing:
            - title (str): The opportunity title.
            - body (str): The summary or description.
            - link (str): Full URL to the opportunity.
            - end-date (str): Application deadline in DD/MM/YYYY format.
    """
    soup = BeautifulSoup(li_html, 'html.parser')
    
    # Título
    title_tag = soup.find('strong', class_='title')
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Corpo/resumo
    summary_tag = soup.find('span', class_='text-resumo')
    body = summary_tag.get_text(strip=True) if summary_tag else ""

    # Link (href relativo)
    link_tag = soup.find('a', class_='link_col')
    href = link_tag.get('href', '') if link_tag else ''
    link = base_url + href if href.startswith('/') else href

    # City
    full_text = soup.get_text(" ", strip=True)
    date_match = re.search(r"Cidade:\s*(\d{2}/\d{2}/\d{4})", full_text)
    end_date = date_match.group(1) if date_match else ""

    # Extract full text from the HTML
    full_text = soup.get_text(" ", strip=True)
    date_match = re.search(r"Inscrições até:\s*(\d{2}/\d{2}/\d{4})", full_text)
    end_date = date_match.group(1) if date_match else ""

    # Find city
    strong_tag = soup.find('strong', string=lambda s: s and 'Cidade:' in s)
    city = strong_tag.next_sibling.strip() if strong_tag and strong_tag.next_sibling else ""

    # institute
    strong_tag = soup.find('strong', string=lambda s: s and 'Instituição:' in s)
    institute = strong_tag.next_sibling.strip() if strong_tag and strong_tag.next_sibling else ""
    
    return {
        "title": title,
        "body": body,
        "link": link,
        "end-date": end_date,
        "city": city,
        "institute": institute
    }


def parse_opportunities(list_html, base_url="https://fapesp.br"):
    total_list = []
    for item in list_html:
        res = parse_opportunity(item, base_url=base_url)
        total_list.append(res)
    return total_list

# Main execution block
if __name__ == "__main__":
    URL = "https://fapesp.br/oportunidades/mais-recentes/"
    TITLES = {"Bolsa de PD"}  # Filter by this title (e.g., "Postdoctoral Fellowship")
    CONTENTS = {"computação", "elétrica", "neural", "neurais", "sinais", "machine learning"}  # Keywords to search in content

    # Step 1: Retrieve all open opportunities
    opportunities = get_open_opportunities(url=URL)

    # Step 2: Filter them by title keywords
    opportunities = filter_grants_by_title(opportunities, TITLES)

    # Step 3: Further filter by keywords in the full content
    opportunities = filter_grants_by_content(opportunities, CONTENTS)

    import json
    # Step 4: Parse and display each result
    for i, item in enumerate(opportunities, 1):
        print(f"\n--- Opportunity {i} ---\n")
        res = parse_opportunity(item)
        print(json.dumps(res, indent=2, ensure_ascii=False))

