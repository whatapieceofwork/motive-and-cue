Documentation currently under development!

See project demo video here: https://www.youtube.com/watch?v=7QBUfK2O5jo

# Motive and Cue

Motive and Cue (MaC) is a full-stack Python application for tracking interpretations made in film adaptations of Shakespeare plays. It was created by Alison Bain as the capstone project for the Hackbright Software Engineering course of September 2021.

Currently in alpha: http://motiveandcue.com/


## Major Dependencies

Motive and Cue relies on the following major dependencies:

[Flask](https://flask.palletsprojects.com/en/2.0.x/): Minimalist web framework for Python
[SQLAlchemy](https://sqlalche.me/): Python SQL toolkit and Object Relational Mapper
[Jinja](https://jinja.palletsprojects.com/): HTML templating system
[Whoosh](https://whoosh.readthedocs.io/): Python search engine library

See the requirements.txt file for more details on requirements.


## APIs

Motive and Cue is made possible due to these excellent APIs:

[The Movie Database API](https://developers.themoviedb.org/3): Film metadata, posters, and cast and crew images
[The Folger Shakespeare API](https://www.folgerdigitaltexts.org/api): Shakespeare play data
(Special thanks to the Folger API team for adding the Scenes and Synopsis functions for me!)
[Cloudinary](https://cloudinary.com/): Cloud storage and image and video APIs


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

This project is my first real foray into development, and while I would love the code to be useful for someone, I make no promises!


## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)