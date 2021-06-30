"""Classes and functions used for parsing Folger Shakespeare API data."""

import re #regex
from bs4 import BeautifulSoup
import requests
from crud import *
from server import *

def parse_folger_characters(play):
  """Given a play shortname, return the Folger list of character names in order of line count."""

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

  scenes = {}

  play_title = play.title
  play_title = play_title.lower().replace(" ", "-")
  play_title = play_title.strip("'',:")

  scenes_page_url = f"https://shakespeare.folger.edu/shakespeares-works/{play_title}"
  print(f"****************** IN PARSE_FOLGER_SCENES, URL {scenes_page_url} *******************")

  page = requests.get(scenes_page_url)
  soup = BeautifulSoup(page.content, "html.parser")
  scene_list = soup.find_all("h3", attrs={"class": "contents-title"})
  print(f"****************** IN PARSE_FOLGER_SCENES, play {play.title} *******************")
  print(f"****************** SCENE_LIST: {scene_list} *******************")

  scene_count = 0
  for scene in scene_list:
    scene_regx = re.search(r'(?P<act>(?<=Act )\d+).*(?P<scene>(?<=, scene )\d+)', str(scene))
    if scene_regx:
      scenes[scene_count] = scene_regx.groupdict()
      scene_count += 1

  print(f"********SCENESDICT: {scenes}")

  return scenes


def parse_folger_scene_descriptions(play):
  """Given a dictionary of acts and scenes, scrape each Folger scene page and add those descriptions to the Scene database objects."""

  from crud import get_all_scenes_by_play, get_scene
  from server import db

  scenes = get_all_scenes_by_play(play)

  for db_scene in scenes:
    act_num = db_scene.act
    scene_num = db_scene.scene
    scene_page_url = f"https://shakespeare.folger.edu/shakespeares-works/{play.title}/act-{act_num}-scene-{scene_num}/"
    page = requests.get(scene_page_url)
    soup = BeautifulSoup(page.content, "html.parser")
    synopsis = soup.find("div", attrs={"id": "modal-ready"}).find("p", recursive=False).string
    db_scene.description = synopsis
    db.session.merge(db_scene)

  db.session.commit()

  return get_all_scenes_by_play(play)