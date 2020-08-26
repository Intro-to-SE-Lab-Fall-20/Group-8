# Group-8

# Development Environment Setup
***Prerequisites***
1. Grab the latest version of Github desktop from [here][7], or if you prefer, git-bash from [here][3].
2. If you do not already have Python 3.8.5, download and install it from [here][6].
3. Install pipenv by running the following in your favorite shell/terminal: ```python3 -m pip install pipenv```
4. Download and install the latest version of PyCharm from [here][4]. Some of the features we'll be using require the professional version but don't worry, you can sign up for free with your school email [here][5]. Once you install it, go ahead and open it up and sign in to your freshly made pro account.

[1]: https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe
[2]: https://docs.docker.com/docker-for-windows/install-windows-home/
[3]: https://git-scm.com/download/win
[4]: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=win
[5]: https://www.jetbrains.com/shop/eform/students
[6]: https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe
[7]: https://central.github.com/deployments/desktop/desktop/latest/win32

***Clone the Repo***
1. Open up PyCharm and select "Get from Version Control"
2. In the url box, enter `https://github.com/Intro-to-SE-Lab-Fall-20/Group-8.git` and select "Clone".

***Setup Project Interpreter***
1. After cloning the repo, close the project within PyCharm and then reopen it. This is a workaround for a bug in PyCharm not loading it properly after a clone.
1. Go to "File > Settings > Project > Project Interpreter".
2. Next to the "Python Interpreter" drop down, click the gear icon and choose "Add".
3. On the left, select "Pipenv Environment".
4. Make sure that "Install packages from Pipfile" is checked and that your "Base Interpreter" says `Python 3.8` or similar.
5. Click "OK" and wait for "Setting up Pipenv Environment" to finish.
6. Make sure the newly created "Pipenv (Group-8)" interpreter option is selected and click "OK".
6. Next, navigate to "Languages & Frameworks > Django".
7. Select "Enable Django Support".
8. For "Django Project Root", browse to and select the `Group-8/code` directory.
9. For "Settings", browse to and select `Group-8/code/project/settings.py`.
10. Click "OK" in the bottom right.

***Start the Webserver***
1. In the top right of the main PyCharm window, make sure the configurations dropdown has "Django Debug" selected.
2. Click the green play button to start the Django web server. If this is the first time you've done this, it could take a while to download and build the necessary docker images.
3. Once the server is up and running, open up a browser and go to http://localhost:8080
4. If everything went well, you should see a rocket ship. Congrats!
5. To stop the server, click the red stop button in PyCharm.
