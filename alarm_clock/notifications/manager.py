"""
This module contains the class for the notification manager. This contains a list that persists for
the lifetime of the app.

One handy thing that this allows for is much easier persistent storage in a database if required.

Written by Sam Mason, Nov 2020
"""
import json
import logging
import os

from alarm_clock.notifications.models import Notification

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))


class NotificationManager:
    """
    A class which encapsulates the functions around the alarm clock Notifications
    """
    active_notification_list = []

    def __init__(self, add_placeholders=False):
        if add_placeholders:
            self.active_notification_list.append(
                Notification(title="Test title", content="Some fancy ass text right here",
                             action="https://bbc.co.uk"))
            self.active_notification_list.append(
                Notification(title="Test title", content="Some fancy ass text right here",
                             action="https://bbc.co.uk"))

    def create_notifications(self, json_input):
        """
        Take a JSON input, and create a notification from it

        :param json_input: JSON input string
        """
        # Covid Notifications
        data = json.loads(json_input)
        if "covid" in data:
            covid_data = data.get("covid")
            self.active_notification_list.append(Notification(
                title="Covid Update",
                content="Nationally: {0} Locally: {1}".format(covid_data.get("nationally"), covid_data.get("locally")),
                action=None))

        if "weather" in data:
            weather_data = data.get("weather")
            self.active_notification_list.append(
                Notification(title="Weather Update",
                             content="{description}, with {precip_chance}% chance of precipitation, "
                                     "and an average temperature of {avg_temp}ºC"
                             .format(
                                 description=weather_data.get("description").title(),
                                 precip_chance=round(float(weather_data.get("precip_chance")) * 100),
                                 avg_temp=weather_data.get("temp")), action=None))

        if "news" in data:
            news_data = data.get("news")
            for item in news_data:
                has_description = len(item.get("description", "")) > 0 if item.get(
                    "description") is not None else False
                content = "<h6 style='margin-bottom: 0px;'>{0}</h6>{1}".format(
                    item.get("title"), "<hr>{0}".format(item.get("description")) if has_description else "")
                self.active_notification_list.append(
                    Notification(title="News Update", content=content, action=item.get("url"),
                                 image_src=item.get("image_src")))

    def render(self):
        """
        Return a list of all active notifications HTML string

        :return list: List of HTML strings
        """
        return [item.render_notification(index=index) for index, item in
                enumerate(self.active_notification_list)]

    def delete_notification(self, notification_index):
        """
        Delete a notification from the list of active notifications

        :return bool: Returns success status
        """
        # noinspection PyBroadException
        try:
            self.active_notification_list.pop(int(notification_index))
            return True
        # pylint: disable=W0703
        except Exception as exception:
            logger.error(exception)
            print(exception)
            return False

    def clear_notifications(self):
        """
        Clear all notifications from the active list
        """
        self.active_notification_list = []
