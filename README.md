# CA3: COVID Alarm Clock

__Please see the [Matching to mark scheme](#Matching-to-mark-scheme) section__

See `docs/index.html` for full Sphinx documentation

## Prerequisites

The system is written in Python 3 programming language. You will need to have a working python3 interpreter and also
a means to create new virtual environments to isolate this system's library requirements from other systems you 
may have installed. Information on how to do this is below.

Please see the [Important details](#Important-details) section.

## Setup

Create a new virtualenv using your favourite virtual env tool (virtualenv, pipenv etc), activate it, 
and install the requirements:
``` shell script
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip3 install -r requirements.txt
```
Note: If you create the virtualenv within the root directory and do __not__ name it `env`, you will need to add it
to the `.gitignore` file to prevent it from being added to the repo. 

## Running the application

Ensure you have activated the virtualenv, then run the app using:
``` shell script
    $ cd alarm_clock && python -m flask run
```

Then head to: [http://127.0.0.1:5000](http://127.0.0.1:5000) to open it.

## Testing

Ensure you have activated the virtualenv, then run the app using:
``` shell script
    $ pytest
```


## Pylint checking

Ensure that you have activated the virtual environment before testing.

Then in the project root directory:
``` shell script
    $ pylint alarm_clock/*.py
    $ pylint alarm_clock/alarm/*.py
    $ pylint alarm_clock/information/*.py
    $ pylint alarm_clock/notifications/*.py
    $ pylint alarm_clock/tests/*.py
```
OR run this to do it all at once
``` shell script
    $ pylint alarm_clock/*.py
```

## Description

### Important details

 - The main template is not modified, but instead I used my own, that I built from scratch, in order to take better 
 advantage of Flask's templating engine.

 - Instead of a JSON based config file, I used a `.env` file, see [Project configuration](#Project-configuration).

 - Instead of using the supplied COVID SDK, I used the builtin `requests` library, this was because the SDK targeted an 
outdated version of the COVID data API, so in the interests of forward compatibility, I used the v2 api, instead of v1.

 - I took a mostly object oriented approach to this assessment as it is what I am most familiar with, and allows
for further expansion if I ever needed it.

 - Managers manage the lists of main items, such as Alarms, Notifications. There is also a manager 
for the news item list, however this is only every instantiated when needed.

## Matching to mark scheme

This section covers how I have applied each point of the mark scheme in my work. 

### Alarms and Notifications:
This part covers the various aspects of the Alarms and notifications section of the mark scheme.

#### Functionality:
 - Briefings are scheduled by pressing the add alarm button. This gives the user the option to select a time, 
 the contents of the briefing, and whether it should be an audible announcement. This will also create scheduled alarms
  for the next 50 days at that time (This figure can be changed in the `.env` file).
 
 - The notifications are updated every time an alarm goes off. By default, the app creates an alarm for the time 
 when the app instance was created. This fills out the notifications with data as soon as the app starts.

#### Style:
 - On all files relating to alarms (`alarm_clock.alarm`) and notifications (`alarm_clock.notifications`), the average 
 pylint scores were 98.4% and 100% respectively.

### Smartness:
This part covers the various aspects of the smart-ness section of the mark scheme.

#### Functionality:
 - The system gathers both news and weather data in their respective managers, and models. The APIs for such are 
 [tested](#Testing).
    - For News, the audible announcement will read out the top two headlines, but put the top 5 into notifications.
    - For weather, the user is supplied with a description, precipitation, and temperature.

 - The COVID-19 data uses the governments v2 api, instead of the sdk, as it was more succinct and easier to use. The 
 user is told about local, and national data, including the new cases, and new deaths (Cumulative deaths are presented 
 for national figures only). The deaths figure uses the `___Deaths28DaysByPublishDate` figure as the one given in the 
 SDK documentation will always return 0 (The government changed their counting method). 
 
 - The information is accessed upon an alarm going off.
#### Style:
 - On all files relating to information gathering (`alarm_clock.information`), the average pylint score was 100%.

### Project delivery:

This part covers the various aspects of the project delivery section of the mark scheme.

#### Interface:
The user interface for this project uses Bootstrap and Jquery in order to both look nice, and function smoothly.

I used JQuery's Ajax library to ping the Flask server every 3.6 seconds (this can be changed in the `.env`
 file mentioned below). Ajax is also used when submitting the 'new alarm' form, which waits for a response from the 
 server before updating the page.

#### Project configuration:
The config file is seen as the `.env` file here. At the start of the app, the variables here are all stored in the 
python environment, and can be referenced anywhere in the project using `os.getenv(...)`. 
This method removes the time spent opening a JSON file.

In normal development, the `.env` file would not be stored in the Git Repository, but in this case it is, because it's 
required for assessment, and cannot be submitted separately. 

This is also more secure than using a JSON config, as it means in a real life scenario, the sensitive information is not
stored in the repo.

#### Logging:

Logging is simply achieved using the builtin Python logging library. Every significant event is logged, and 
any try/catch errors are reported too.  

All log items from the alarm clock are put into `applog.txt`, and put onto the main thread log stream.

#### Testing:

I have provided extensive testing throughout the project. These tests cover:
 - API statuses
 - The workflow through the whole project

However, it is incredibly difficult to test the the scheduling, so that is not currently covered. One way to allow 
for this is to run a self test when the server starts.

The workflow is covered up to the point of rendering html templates die to the lack of Flask context withing the PyTest 
environment.

## Licence

Copyright © 2020 Samuel James Mason

For full licence see [LICENCE](LICENSE).
