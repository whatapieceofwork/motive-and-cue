"""Classes and functions used for parsing Folger Shakespeare API data."""

from bs4 import BeautifulSoup

import re
import requests

def parse_folger_characters(play):
  """Given a play, return a numbered dictionary of character names and wordcounts from the Folger API, ordered by wordcount."""

  characters = {}
  shortname = play.shortname
  parts_page_url = f"https://folgerdigitaltexts.org/{shortname}/charText/"
  page = requests.get(parts_page_url)
  soup = BeautifulSoup(page.content, "html.parser")

  count = 0
  wordcount_names = re.findall('(?P<wordcount>(?<=60px;">)\d+).*(?P<character>(?<=.html">)\w+)', str(soup))
  for wordcount, name in wordcount_names:
    split_name = re.sub(r'(?<![A-Z\W])(?=[A-Z])', ' ', name) # Split name after each lowercase letter before an uppercase character
    name = "".join(split_name)
    name = name.lstrip()
    if not name.isupper(): # Discard all-CAPS names, which refer to plural speakers like ATTENDANTS
      characters[count] = (name, wordcount)
      count += 1

  print(f"**********IN FOLGERPARSECHAR, CHAR: {characters}")
  return characters


def parse_folger_scenes(play):
  """Given a play, return the Folger API list of scenes as a numbered dictionary."""

  scenes = {}

  shortname = play.shortname
  scenes_page_url = f"https://folgerdigitaltexts.org/{shortname}/scenes/"
  page = requests.get(scenes_page_url)
  soup = BeautifulSoup(page.content, "html.parser")
  scene_list = soup.find_all("p")

  scene_count = 0
  for scene in scene_list:
    scene_regx = re.search(r'(?P<act>(?<=Act )\d+).*(?P<scene>(?<=, scene )\d+)', str(scene))
    if scene_regx:
      scenes[scene_count] = scene_regx.groupdict()
      scene_count += 1

  print(f"********SCENESDICT: {scenes}")

  return scenes


def parse_folger_scene_descriptions(play):
  """Retrieve the Folger API scene descriptions for a play and update any existing Scene objects without a description."""
  from app.main.crud import get_scene, update_scene, get_all_scenes_by_play

  shortname = play.shortname
  synopses_page_url = f"https://folgerdigitaltexts.org/{shortname}/synopsis/"
  page = requests.get(synopses_page_url)
  soup = BeautifulSoup(page.content, "html.parser")
  
  act_scene_synopses = re.findall('(?P<act>(?<=<p>Act )\d+).*(?P<scene>(?<=, Scene )\d+): (?P<synopsis>.*)(?=</p>)', str(soup))

  for act, scene, synopsis in act_scene_synopses:
    db_scene = get_scene(act=act, scene=scene, play=play, description=synopsis)
    db_scene = update_scene(scene=db_scene, description=synopsis)

  return get_all_scenes_by_play(play)