# Group-8

[![Build Status](https://travis-ci.org/simkimsia/UtilityBehaviors.png)](https://travis-ci.org/simkimsia/UtilityBehaviors)

### Project Description

This project aims to design and develop a web-based email client where users will be able to login, send and receive messages, forward messages, and upload attachments.
This will be accomplished using a popular Python based web framework called Django.
The resulting web-app will run in Docker containers allowing it to be deployed easily wherever and whenever.
This project also aims to develop this product in such a way that enables for future development given customer feedback and later requirements.
This project will be developed in 4 sprints, varying from 2 to 4 weeks long each.
Development will follow Agile paradigms.

*Note: this project is intended as a deliverable for CSE 4214 Intro to Software Engineering.*

### Objective and Features
The primary objective of this project is to design and develop a web-based email client with which users should be able to:
- Login and access emails
- Compose, edit, and send emails to other users
- Search through and forward emails to other users
- Send attachments along with emails

### Project Members
Name | Github
--- | ---
Denton Young | [theextrapack](https://github.com/theextrapack)
Shorn Rose | [ShornRose](https://github.com/ShornRose)
Joshua Morgan | [Uriel110](https://github.com/Uriel110)
Kaleb Thornton | [krthornton](https://github.com/krthornton)


### Languages & Technologies
Our project uses the following languages and technologies:
- **Python** - the main language in which most of the webserver/database code is written
- **HTML/CSS/JS** - the usual suspects for developing web-app front-ends
- [**Bootstrap**](https://getbootstrap.com) - a collection of prebuilt CSS styles and JS functionalities
- [**JQuery**](https://jquery.com) - a popular JS library with a bunch of pre-built functionalities
- [**Django**](https://www.djangoproject.com/start/overview/) - a Python web framework for developing web-apps fast
- [**SQLite3**](https://www.sqlite.org/index.html) - a simple database solution used by default in Django (this could change)
- [**Docker**](https://www.docker.com/resources/what-container) - a containerization tool to help keep our development environments consistent
- [**PyCharm**](https://www.jetbrains.com/pycharm/) - Python IDE with support for debugging with Django and Docker


# Development Environment Setup

### Prerequisites
1. First, make sure you have Docker installed and ready to go. [Here][1] is a link to download docker and [here][2] are instructions on how to set it up.
2. Also, go grab the latest version of git from [here][3].
3. Download and install the latest version of PyCharm from [here][4]. Some of the features we'll be using require the professional version but don't worry, you can sign up for free with your school email [here][5]. Once you install it, go ahead and open it up and sign in to your freshly made pro account.

[1]: https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe
[2]: https://docs.docker.com/docker-for-windows/install-windows-home/
[3]: https://git-scm.com/download/win
[4]: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=win
[5]: https://www.jetbrains.com/shop/eform/students

### Clone the Repo
1. Open up PyCharm and select "Get from Version Control"
2. In the url box, enter `https://github.com/Intro-to-SE-Lab-Fall-20/Group-8.git` and select "Clone".

### Setup Project Interpreter
1. After cloning the repo, close the project within PyCharm and then reopen it. This is a workaround for a bug in PyCharm not loading it properly after a clone.
2. Go to "File > Settings > Project > Project Interpreter".
3. Next to the "Python Interpreter" drop down, click the gear icon and choose "Add"
4. On the left, select "Docker Compose"
5. In the "Configuration Files" textbox, select the folder icon. In the popup, click the "+" then browse to and select `debug-docker-compose.yml`
6. In the Service dropdown, select `django-debug` and click "OK"
7. Next, navigate to "Languages & Frameworks > Django"
8. Select "Enable Django Support"
9. For "Django Project Root", browse to and select the `code` directory
10. For "Settings", browse to and select `code/project/settings.py`
11. Click "OK" in the bottom right

### Start the Webserver
1. In the top right of the main PyCharm window, make sure the configurations dropdown has "Django Debug" selected.
2. Click the green play button to start the Django web server. If this is the first time you've done this, it could take a while to download and build the necessary docker images.
3. Once the server is up and running, open up a browser and go to http://localhost:8080
4. If everything went well, you should see a rocket ship. Congrats!
5. To stop the server, click the red stop button in PyCharm.
