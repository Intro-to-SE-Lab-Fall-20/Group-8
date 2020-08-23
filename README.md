# Group-8

# Development Environment Setup
***Prerequisites***
1. First, make sure you have Docker installed and ready to go. [Here][1] is a link to download docker and [here][2] are instructions on how to set it up.
2. Also, go grab the latest version of git from [here][3].
3. Download and install the latest version of PyCharm from [here][4]. Some of the features we'll be using require the professional version but don't worry, you can sign up for free with your school email [here][5]. Once you install it, go ahead and open it up and sign in to your freshly made pro account.

[1]: https://download.docker.com/win/stable/Docker%20Desktop%20Installer.exe
[2]: https://docs.docker.com/docker-for-windows/install-windows-home/
[3]: https://git-scm.com/download/win
[4]: https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=win
[5]: https://www.jetbrains.com/shop/eform/students

***Clone the Repo***
1. Open up PyCharm and select "Get from Version Control"
2. In the url box, enter `https://github.com/Intro-to-SE-Lab-Fall-20/Group-8.git` and select "Clone".

***Setup Project Interpreter***
1. Once PyCharm finishes cloning the repo and opens up, go to "File > Settings > Project > Project Interpreter". (If you don't see this, you may have to reopen the project after cloning.)
2. Next to the "Python Interpreter" drop down, click the gear icon and choose "Add"
3. On the left, select "Docker Compose"
4. In the "Configuration Files" textbox, select the folder icon. In the popup, click the "+" then browse to and select `debug-docker-compose.yml`
5. In the Service dropdown, select `django-debug` and click "OK"
6. Next, navigate to "Languages & Frameworks > Django"
7. Select "Enable Django Support"
8. For "Django Project Root", browse to and select the `code` directory
9. For "Settings", browse to and select `code/project/settings.py`
10. Click "OK" in the bottom right

***Start the Webserver***
1. In the top right of the main PyCharm window, make sure the configurations dropdown has "Django Debug" selected.
2. Click the green play button to start the Django web server. If this is the first time you've done this, it could take a while to download and build the necessary docker images.
3. Once the server is up and running, open up a browser and go to http://localhost:8080
4. If everything went well, you should see a rocket ship. Congrats!
5. To stop the server, click the red stop button in PyCharm.
