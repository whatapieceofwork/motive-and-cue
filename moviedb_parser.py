"""Classes and functions used for parsing MovieDB API data."""

from flask import Flask, render_template, redirect, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
import jinja2
import os
import requests
import re #regex
import json

MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
GENDERS = {
    0: "Other/NA",
    1: "Female",
    2: "Male",
}

def get_moviedb_film_id(film_url):
    """Given the URL of a film on MovieDB, return the film's MovieDB ID."""

    moviedb_regx = ("(?<=https:\/\/www\.themoviedb\.org\/movie\/)[0-9]*") #MovieDB film ID format
    moviedb_id = re.search(moviedb_regx, film_url)[0] #first result of regex search for MovieDB film ID format in URL

    return int(moviedb_id)


def parse_moviedb_film(moviedb_id, play):
    """Given a film's MovieDB ID, process film information and return as dictionaries for user verfication."""

    moviedb_credits = "https://api.themoviedb.org/3/movie/" + str(moviedb_id) + "/credits?api_key=" + MOVIEDB_API_KEY
    credits = requests.get(moviedb_credits).json()
    cast_credits, crew_credits = credits["cast"], credits["crew"]

    film_details = parse_moviedb_film_details(moviedb_id, play) #parse MovieDB film details and create Film database object
    cast = parse_moviedb_cast(moviedb_id, cast_credits) #parse MovieDB actor details and create Actor database objects
    crew = parse_moviedb_crew(moviedb_id, crew_credits) #parse MovieDB crew details and create various crew database objects

    return (film_details, cast, crew)


def parse_moviedb_film_details(moviedb_id, play):
    """Given a MovieDB film ID, parse and return film details as dictionary."""

    film = {}
    date_format = "%Y-%m-%d"

    details_request_url = "https://api.themoviedb.org/3/movie/" + str(moviedb_id) + "?api_key=" + MOVIEDB_API_KEY + "&language=en-US"
    details = requests.get(details_request_url).json()

    film["moviedb_id"] = moviedb_id
    film["imdb_id"] = details["imdb_id"]
    film["title"] = details["title"]
    film["release_date"] = details["release_date"]
    film["release_date"] = datetime.strptime(film["release_date"], date_format)
    film["language"] = details["original_language"]
    film["length"] = details["runtime"]
    film["play_id"] = play.id
    if details["poster_path"]:
        film["poster_path"] = "https://www.themoviedb.org/t/p/original/" + details.get("poster_path")


    return film


def parse_moviedb_person(moviedb_id):
    """Given a person's MovieDB ID, parse and return person details as dictionary."""

    person = {}
    date_format = "%Y-%m-%d"

    profile_request_url = "https://api.themoviedb.org/3/person/" + str(moviedb_id) + "?api_key=" + MOVIEDB_API_KEY
    profile = requests.get(profile_request_url).json()

    person["moviedb_id"] = moviedb_id
    person["imdb_id"] = profile["imdb_id"]
    person["full_name"] = profile["name"].split()
    person["fname"] = person["full_name"][0]
    person["lname"] = person["full_name"][-1]
    person["gender"] = profile["gender"]
    person["birthday"] = profile["birthday"]
    if person["birthday"]:
        person["birthday"] = datetime.strptime(profile["birthday"], date_format)
    person["photo_path"] = profile["profile_path"]
    if person["photo_path"]:
        person["photo_path"] = "https://www.themoviedb.org/t/p/original/" + profile["profile_path"]

    print(f"*********** PERSON: {person}")
    return person


def parse_moviedb_cast(moviedb_id, cast_credits):
    """Given a MovieDB ID and cast credits JSON object, process cast info and return as dictionary of dictionaries."""
    
    cast = {}

    for castmember in cast_credits:
        cast_id = castmember["id"]
        person_dict = parse_moviedb_person(cast_id)
        cast[cast_id] = person_dict
        cast[cast_id]["parts_played"] = castmember["character"].split(" / ")
        cast[cast_id]["moviedb_id"] = moviedb_id

    print(f"*********** CAST: {cast}")
    return cast


def parse_moviedb_crew(moviedb_id, crew_credits):
    """Given a Movie record and crew credits JSON object, process crew info and return as dictionary of dictionaries."""

    crew = {}
    important_crew_jobs = {"Director", "Cinematographer", "Executive Producer", "Writer"}

    for crewmember in crew_credits:
        if crewmember["job"] in important_crew_jobs:
            crew_id = crewmember["id"]
            person_dict = parse_moviedb_person(crew_id)
            crew[crew_id] = person_dict
            crew[crew_id]["job"] = crewmember["job"]

    print(f"*********** CREW: {crew}")
    return crew

