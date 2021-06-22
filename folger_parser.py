"""Classes and functions used for parsing Folger Shakespeare API data."""

import re #regex

def parse_folger_characters(play):
  """Given a play shortname, return the Folger list of characters in order of line count."""

  from bs4 import BeautifulSoup
  import requests

  shortname = play.shortname
  parts_page_url = f"https://folgerdigitaltexts.org/{shortname}/charText/"
  page = requests.get(parts_page_url)
  soup = BeautifulSoup(page.content, "html.parser")
  character_link_list = soup.find_all("a")

  characters = []
  for character in character_link_list:
    if character.string.istitle():
     characters.append(character.string)

  return characters


def parse_folger_scenes(play):
  """Given a play, scrape the Folger works page and return a dictionary of scene information."""

  from bs4 import BeautifulSoup
  import requests

  scenes = {}

  play_title = play.title
  play_title = play_title.lower().replace(" ", "-")

  scenes_page_url = f"https://shakespeare.folger.edu/shakespeares-works/{play_title}"
  page = requests.get(scenes_page_url)
  soup = BeautifulSoup(page.content, "html.parser")
  scene_list = soup.find_all("h3", attrs={"class": "contents-title"})

  scene_count = 0
  for scene in scene_list:
    # print(f"***********SCENETEXT: {scene.text}")
    scene_regx = re.search(r'(?P<act>(?<=Act )\d+).*(?P<scene>(?<=, scene )\d+)', str(scene))
    # print(f"*************SCENEREGX: {scene_regx}")
    if scene_regx:
      scenes[scene_count] = scene_regx.groupdict()
      scene_count += 1

  print(f"********SCENESDICT: {scenes}")

  return scenes
