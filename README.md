# oauth-list
Test project to implement **Google's Oauth 2.0**

to start the virtual environment:
source venv/Scripts/activate

to start the flask-app from project root:\
export FLASK_APP=app/routes.py'\
python -m flask run

the flow of the web application will be:
- *User* will arrive at the landing page and see a prompt to login using their Google credentials
- *User* logs in using their Google credentials
- *User* will be shown a list of things(TBA as of 2022-07-29)
- *User* will be able to logout of their Google account
- *User* will be moved back to the landing page
