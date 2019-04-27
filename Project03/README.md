# Project03: Trivia
Project03 is an authenticated two player live trivia game. 

#### How to run Project03 on the mac1xa3 server
1. Clone the project, and in a Python virtual enviroment, run `pip install requirements.txt`
2. Navigate to Project03/django_project, and run `python manage.py runserver localhost:10007`
3. The project will now be accessible at https://mac1xa3.ca/e/bhatts39/

#### Project features

This project makes use of Django's build-in user authentication system to allow for users to register and login before they play the game. 

The game includes 1v1 matchmaking, live multiplayer trivia, and a leaderboard with top players.

All client-server interaction is done through web requests, using AJAX as well as long-polling techniques to allow for the server to push data to the clients.

#### How it was made

* Django backend
* jQuery, HTML, Bootstrap frontend
* Open Trivia DB API for trivia questions: https://opentdb.com

#### How to play the game
* Two players are matched up to one trivia game
* Questions are presented to both players at the same time
* Whoever answers the question correctly first wins the point, and the next question is displayed
* If neither player answers correctly, nobody gets a points
* First player to 5 points wins


