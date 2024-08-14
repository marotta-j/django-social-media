![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# django-social-media
A social media website created with Django

## Features
- Share text and image posts (with comments)
- User authentication and authorization
- User profiles with editable bio
- Track followers and likes

## How to deploy it yourself
1. Change the environment variables in `socialwebsite/settings.py`
2. Change the database settings in `socialwebsite/settings.py` to where the DB will be hosted
3. Install the dependencies in the `requirements.txt` file
4. Run:
```
python manage.py makemigrations
python manage.py migrate
```
5. Run `python manage.py runserver` and enjoy!


