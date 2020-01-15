# RutgersBot
A rutgers bot for the CS Discord!

##### Table of Contents
* [Abstract](#abstract)
* [Getting Started](#getting-started)
    * [Configuration](#configuration)
    * [Running](#running)
    * [Closing](#closing)
* [Command Information](#command-information)

##  Abstract
This application serves as the Rutgers discord bot that is currently running on the Computer Science discord. Details on the commands it provides for users can be looked up in the Wiki section of the github page. It provides tools for moderation, information on bus arrival time and more.

## Getting Started
Pre-requisites - these are assumed to be already installed on your computer
* Required
    * Python (minimum version: 3.6.7) - the language that this program was return in
    * pip - the package installer for Python to install the necessary packages
* Recommended
    * venv - virtual environment dedicated to run this application script so it doesn't pollute the global installation

Clone the repo and download all of the dependencies (to be listed in requirements.txt and can be installed using `pip install -r <path/to/requirements.txt>`). 

### Configuration
Locate the config.py file within the repo and provide it with the necessary information.
One necessary piece for the bot to run successful is the login token, generate your own token by navigating to the discord developer application portal and generate you own. Once generated put them in the "" that corresponds with the text below in the config.py file.
LOGIN_TOKEN = ""

For the busing commands to work on your instance you will also need a token for transloc's api, generate a rapid API token for that and provide it as input with the corresponding text.
X_RAPIDAPI_KEY = ""

Since the bot uses mongodb for storage of moderation information, provide the mongodb cluster link as a key here to store information in your own cluster when running the bot.
MONGO_KEY = ""

To determine who is a moderator, the bot needs input on what roles are representatives of mods. List the role names here in order for the bot to understand who deserves administration rights.
MODERATOR_ROLES = [""]

To mute a user, a role is assigned to them. The role listed here is what will be assigned upon muting.
MUTED_ROLE = ""

### Running
Finally, you are ready to run this Python program. To do so, open a terminal or command prompt, navigate to the folder
which contains the "turn_on.py" file and run the program using `python3 turn_on.py`
Note: if you have multiple python3 versions, you might need to specify the correct one using "python3.6" instead of "python3"

### Closing
If you ever decide you want to stop the bot from running on your machine for a while, simply close the bot by providing a SIGINT to it.
To do this, press CTRL + C on the terminal you are currently running it on or run kill with SIGINT on the correct process ID that represents it.

## Command Information
Command information for the bot can be located at the wiki section of the repo.
