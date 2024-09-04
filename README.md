[![Frame of Motive and Cue demo video](http://img.youtube.com/vi/7QBUfK2O5jo/0.jpg)](http://www.youtube.com/watch?v=7QBUfK2O5jo "Motive and Cue")

Watch project demo video here: https://www.youtube.com/watch?v=7QBUfK2O5jo

# Motive and Cue

Motive and Cue is a full-stack Python Flask application to track casting, editing, and directorial decisions made in film adaptations of Shakespeare. It was created by Alison Bain as the capstone project for the Hackbright Software Engineering course of September 2021.

Currently ~~in alpha~~ down, but not forgotten: http://motiveandcue.com/

# Functionality

Motive and Cue has four main branches of functionality; the three which affect the database are gated behind a user authentication system with tiered user permissions.

The first branch is an interface to import Shakespeare character and scene information from the Folger Shakespeare API. I use the Python requests library to query the Folger site, and then regex and the Beautiful Soup HTML parsing library to scrape the appropriate data from the returned HTML.

The second branch of the site is a film import tool. A request for film information is made to the Movie Database API, followed by additional queries for each cast and crew member. All of that information is collated and passed to the user in a single pre-populated form for verification. Older films may have missing data to add, and some credited parts may not be canonical Shakespeare characters; those can be marked for exclusion, which will prevent database entries from being created for them.

The third branch is the question and interpretation tracking system. Questions -- elements of textual ambiguity from the plays -- can be added with a simple form, as can interpretations, the decisions made by films on how to address those ambiguities. Related images can be uploaded using the Cloudinary storage API.

The Motive and Cue database is rich and interconnected, with 22 different tables including 10 association objects. I use the Marshmallow serialization library to export data in JSON format through the Motive and Cue API. Users with the appropriate permissions can request an API token that will allow them to post data to the site as well as query it.

The fourth and last branch is the front-end browsing experience. The site includes dynamic text search with optional search facets and a simple and responsive interface made with Jinja, Bootstrap, JavaScript, HTML, and CSS.


# Project Demo Screenshots
<img width="500" alt="Main site landing page" src="https://github.com/user-attachments/assets/55bdbcb3-768a-4a05-82b6-4c64e71ab918">
<img width="500" alt="Textual Questions page, with screenshots from films " src="https://github.com/user-attachments/assets/fc9dac4e-6fb4-4575-bbcd-00afb774e41d">
<img width="500" alt="Verify Film Information page, with ingested data" src="https://github.com/user-attachments/assets/1d63e40b-0e2e-49ab-863a-6fc87aeca0d6">
<img width="500" alt="Database structure diagram" src="https://github.com/user-attachments/assets/b822f1ce-1e3d-41ba-95e6-27b72d67996f">


## Major Dependencies

Motive and Cue relies on the following major dependencies:

* [Flask](https://flask.palletsprojects.com/en/2.0.x/): Minimalist web framework for Python
* [SQLAlchemy](https://sqlalche.me/): Python SQL toolkit and Object Relational Mapper
* [Jinja](https://jinja.palletsprojects.com/): HTML templating system
* [Whoosh](https://whoosh.readthedocs.io/): Python search engine library

See the requirements.txt file for more details on requirements.


## APIs

Motive and Cue is made possible due to these excellent APIs:

* [The Movie Database API](https://developers.themoviedb.org/3): Film metadata, posters, and cast and crew images
* [The Folger Shakespeare API](https://www.folgerdigitaltexts.org/api): Shakespeare play data\
(Special thanks to the Folger API team for adding the Scenes and Synopsis functions for me!)
* [Cloudinary](https://cloudinary.com/): Cloud storage and image and video APIs\


## Installation

Create a Python project.

Install all requirements in requirements.txt.

Either export local variables or create a secrets.sh file (PRIVATE AND .GITIGNORED!) including the following information:

```
export FLASK_APP=[name of Flask application]
export FLASK_DEBUG=[1 or 0 for True or False]
export FLASK_KEY=[secret Flask application key]
export MAIL_USERNAME=[email address to be used for administrative emails]
export MAIL_PASS=[email password]
export MAIL_SENDER=["From" line]
export MAIL_SUBJECT_PREFIX=[email subject prefix]
export MOVIEDB_API_KEY=[API key for The MovieDB API]
export DEV_DATABASE_URL=[database URI for development server]
export TEST_DATABASE_URL=[database URI for test server]
export CLOUD_NAME=[Cloudinary cloud name]
export CLOUDINARY_KEY=[Cloudinary key]
export CLOUDINARY_KEY_SECRET=[Cloudinary secret key]
```

Optional, to be used with the create-an-admin functionality in seed.py. Useful when repeatedly dropping and recreating databases during testing:

```export ADMIN_USERNAME=[admin username]
export ADMIN_NAME=[admin name]
export ADMIN_EMAIL=[admin email address]
export ADMIN_PASS=[admin password]
export ADMIN_ABOUT=[admin about section for profile]
```

## Using and Contributing

Bug reports and issues are welcome. 

This project is my first real foray into development, and was a personal project made under a class deadline. I would love for this code to be useful for someone, and I intend to maintain and improve on it, but I make no promises as to its long-term upkeep, usability, etc.


## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
