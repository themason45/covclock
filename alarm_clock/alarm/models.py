"""

This module contains the model for the alarm object, which contains the method
that gets fired when a scheduled event is triggered.

This module also contains the project scheduler instance.

Written By: Sam Mason
Date: Nov 2020

"""
import itertools
import logging
import os
import sched
import time
from datetime import datetime, timedelta

import pyttsx3
import requests
from flask import url_for

from alarm_clock.information.manager import NewsManager
from alarm_clock.information.models import CovidUpdate, WeatherUpdate

scheduler = sched.scheduler(time.time, time.sleep)
active_alarms = []

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))

# pylint: disable=W0703


class Alarm:
    """
    Encapsulates all the functions around alarms
    """
    _time = None  # type: datetime.time
    time_obj = None  # type: datetime.time
    announcement = False  # type: bool
    include_covid = True  # type: bool
    include_news = True  # type: bool
    include_weather = True  # type: bool
    test_mode = False  # type: bool
    event_objects = []  # type: list

    def __init__(self, selected_time: datetime.time, include_news=True, include_weather=True,
                 include_covid=True, announcement=False, test_mode=False):
        """
        Initiate an alarm
        """
        # Add current day to the time
        self.time_obj = selected_time  # Store the datetime.time instance for pretty printing
        self.include_covid = include_covid
        self.include_news = include_news
        self.include_weather = include_weather
        self.announcement = announcement
        self.test_mode = test_mode

        # Test mode is for the unit tests. It strips away all forms
        # of scheduling in order to test for correct results
        # To test scheduling, then test the manager
        if not self.test_mode:
            self.set_schedule()

    @staticmethod
    def alarm_action(curr_time: datetime, alarm_obj):
        """
        Do the alarmy-processing.

        At the end of this, the alarm notifies the Notification manager of the new updates.

        This also returns the data that would be used for notifications,
        and the tts, so that the Unit Tests can check it.

        :param alarm_obj:
        :type alarm_obj: .Alarm
        :param curr_time:
        :type curr_time: datetime.time
        :return: If Alarm.test_mode is True, it returns the information, and sentences
        """
        sentences = ["The time is {0}.".format(curr_time.strftime(
            "%H:%M")) if not alarm_obj.has_briefings else
                     "The time is {0}, here is your briefing:".format(
            curr_time.strftime("%H:%M"))]

        information = {}

        try:
            if alarm_obj.include_covid:
                nat_covid = CovidUpdate.populate()

                sentences.append(
                    "Regarding covid, nationally, there are {nn_cases:,} new cases,"
                    " and {nn_deaths:,} new deaths, "
                    "bringing the total deaths to {nc_deaths:,}.".format(
                        nn_cases=nat_covid.new_cases if nat_covid.new_cases > -1 else "no",
                        nn_deaths=nat_covid.new_deaths if nat_covid.new_deaths > -1 else "no",
                        nc_deaths=nat_covid.cum_deaths if nat_covid.cum_deaths > -1 else 0))

                local_covid = CovidUpdate.populate(local=True)

                sentences.append(
                    "Locally, there are {ln_cases:,} new cases,"
                    " and {ln_deaths:,} new deaths.".format(
                        ln_cases=local_covid.new_cases if local_covid.new_cases > -1 else "no",
                        ln_deaths=local_covid.new_deaths if local_covid.new_deaths > -1 else "no"))

                information["covid"] = {
                    "nationally": "{new_cases:,} new cases, {new_deaths:,} "
                                  "new deaths ({cum_deaths:,} total).".format(
                        new_cases=nat_covid.new_cases, new_deaths=nat_covid.new_deaths,
                        cum_deaths=nat_covid.cum_deaths, ),
                    "locally": "{new_cases:,} new cases, {new_deaths:,} new deaths.".format(
                        new_cases=local_covid.new_cases, new_deaths=local_covid.new_deaths, )}

            if alarm_obj.include_news:
                news_updates = NewsManager().get_stories(count=5)

                headlines = [article.title for article in
                             itertools.islice(news_updates, 0, 2)]  # For the TTS

                sentences.append("Your top two headlines are: {0}.".format(". ".join(headlines)))

                information["news"] = [item.serialize() for item in news_updates]

            if alarm_obj.include_weather:
                weather_update = WeatherUpdate().populate()

                sentences.append(
                    "Regarding the weather: Today will be: {description},"
                    " with a {precip_chance}% chance of rain, "
                    "and the average temperature will be {avg_temp} degrees celsius".format(
                        description=weather_update.description,
                        precip_chance=round(weather_update.precip_chance * 100),
                        avg_temp=weather_update.temp))

                information["weather"] = weather_update.serialize()

            if not alarm_obj.test_mode:
                requests.post(
                    "{0}{1}".format(os.getenv("COVCLOCK_SELF_BASE_URL", "http://127.0.0.1:5000"),
                                    url_for("alarm_post")),
                    json=information)  # Notify the notifications manager of an update

            # The TTS engine does not work on GitHub test pipelining system,
            # however it works locally
            if alarm_obj.announcement and not alarm_obj.test_mode:
                tts = pyttsx3.init()
                tts.setProperty("voice", "com.apple.speech.synthesis.voice.fiona")
                # noinspection PyBroadException
                try:
                    tts.endLoop()
                except Exception as exception:
                    logger.error(exception)
                    logger.error('PyTTSx3 Endloop error')
                tts.say(" ".join(sentences))
                tts.runAndWait()

        except Exception as exception:
            logging.error(exception)
            raise exception

        if alarm_obj.test_mode:
            return information, sentences

        return None, None

    def set_schedule(self):
        """
        Adds the alarm to the `sched` schedule.
        """
        self._time = datetime.today().replace(hour=self.time_obj.hour, minute=self.time_obj.minute,
                                              second=self.time_obj.second)
        for i in range(0, int(os.getenv("COVCLOCK_NUMBER_OF_DAYS", "50"))):
            new_time = self._time + timedelta(
                days=i)  # Add the i number of days to the current day, starting at 0
            self.event_objects.append(
                scheduler.enterabs(new_time.timestamp(), 1, Alarm.alarm_action,
                                   argument=(self.time, self)))

    def clear_schedule(self):
        """
        Clears all the `sched` events from the schedule,
        used when deleting the alarm. Prevents any extra alarms
        going off
        """
        # Remove today's event from the schedule
        if time.time() < self._time.timestamp():
            todays_event = self.event_objects.pop(0)
            # If the alarm hasn't gone off yet, then it is safe to remove from the queue
            scheduler.cancel(
                todays_event)

        # Remove the rest
        _ = (scheduler.cancel(e) for e in self.event_objects)

    @property
    def time(self):
        """
        Return the datetime.time object for pretty printing later

        :return: The time object
        :rtype: datetime.time
        """
        return self.time_obj

    @property
    def has_briefings(self):
        """
        Shortcut to check if the Alarm is going to notify and/or announce any information

        :return: Whether the Alarm has briefings
        :rtype: bool
        """
        return (self.include_covid or self.include_news or self.include_weather) is not None
