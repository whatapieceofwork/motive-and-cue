"""Classes and functions used for parsing Folger Shakespeare API data."""

def process_folger_characters(play):
    """Given a play shortname, import the Folger list of characters in order of line count."""

    from bs4 import BeautifulSoup
    import requests

    shortname = play.shortname
    parts_page_url = f"https://folgerdigitaltexts.org/{shortname}/parts/"
    page = requests.get(parts_page_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    character_link_list = soup.find("a")

    for link in character_link_list:
        name = link.text
        if name.istitle():
          character = get_character_by_name(name, play.id)

    db.session.commit()