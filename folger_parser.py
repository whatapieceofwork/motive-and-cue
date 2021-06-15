"""Classes and functions used for parsing Folger Shakespeare API data."""


def parse_folger_characters(play):
  """Given a play shortname, import the Folger list of characters in order of line count."""

  from bs4 import BeautifulSoup
  import requests

  shortname = play.shortname
  parts_page_url = f"https://folgerdigitaltexts.org/{shortname}/charText/"
  page = requests.get(parts_page_url)
  soup = BeautifulSoup(page.content, 'html.parser')
  character_link_list = soup.find_all("a")

  characters = []
  for character in character_link_list:
    if character.string.istitle():
     characters.append(character.string)

  return characters