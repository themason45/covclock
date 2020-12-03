"""
This module contains the class for the alarm manager. This contains a list that persists for
 the lifetime of the app.

One handy thing that this allows for is much easier persistent storage in a database if required.

Written By: Sam Mason
Date: Nov 2020
"""
import logging
import os
from datetime import datetime

from alarm_clock.alarm.models import Alarm, scheduler

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))


# pylint: disable=W0703


class AlarmManager:
    """
    A simple object which solely maintains a list of alarms for the lifetime of the app instance
    """
    active_alarms = []  # type: list
    scheduler = scheduler  # type: scheduler.__class__
    trigger_refresh = False  # type: bool
    # Used by the views file. Dictates whether the browser should refresh to update info
    test_mode = False  # type: bool

    def __init__(self, add_placeholder_alarms=False, test_mode=False):
        if add_placeholder_alarms:
            self.active_alarms = [Alarm(datetime.now())]
        self.test_mode = test_mode

    def get(self):
        """
        Returns a list of all Alarm objects

        :return: List of :class:`.Alarm` instances
        """
        return self.active_alarms

    def set(self, time, include_covid=True, include_news=True, include_weather=True,
            is_audible=False):
        """
        Creates and sets alarm objects (including schedulers)

        :param is_audible: Is the alarm to be an audible announcement
        :param time: What time should the notification/announcement go off?

        Should the notification/announcement include:

        :param include_covid: COVID
        :param include_news: News
        :param include_weather: Weather
        :return: The index in the active alarm list
        :rtype: int
        """
        # noinspection PyBroadException
        try:
            alarm = Alarm(time, include_covid=include_covid, include_news=include_news,
                          include_weather=include_weather, announcement=is_audible,
                          test_mode=self.test_mode)
            self.active_alarms.append(alarm)
            return self.active_alarms.index(alarm)
        except Exception as exception:
            logger.error(exception)
            return -1

    def unset(self, index):
        """
        Remove the :class:`.Alarm` instance from the active_alarms list

        :param index: Index of the alarm in the active alarms list
        :return: The success status
        :rtype: bool
        """
        try:
            alarm = self.active_alarms[int(index)]
            if not self.test_mode:
                alarm.clear_schedule()
            self.active_alarms.pop(int(index))
            return True
        except IndexError:
            return False
