"""
Tests for notification modules

Written By: Sam Mason
Date: Nov 2020
"""

import json

from alarm_clock.notifications.manager import NotificationManager
from alarm_clock.notifications.models import Notification

sample_json = json.dumps({
    'covid': {'nationally': '000 new cases, 000 new deaths (000 total).',
              'locally': '00 new cases, 0 new deaths.'},
    'news': [
        {'title': "EXAMPLE_TITLE",
         'description': 'EXAMPLE_DESC',
         'url': 'EXAMPLE_URL',
         'image_src': 'EXAMPLE_IMG_SOURCE'}],
    'weather': {'description': 'EXAMPLE_DESC', 'temp': 0.00, 'precip_chance': 0}})


def test_creation():
    """
    Tests whether the notification manager creates correctly populated notifications

    :return: None
    """
    expected_notifications = [
        Notification('Covid Update',
                     "Nationally: 000 new cases, 000 new deaths (000 total). "
                     "Locally: 00 new cases, 0 new deaths.",
                     None, None),
        Notification('Weather Update',
                     "Example_Desc, with 0% chance of precipitation, "
                     "and an average temperature of 0.0ºC", None, None),
        Notification('News Update', "<h6 style='margin-bottom: 0px;'>EXAMPLE_TITLE</h6><hr>EXAMPLE_DESC", "EXAMPLE_URL",
                     "EXAMPLE_IMG_SOURCE"),
    ]
    notification_manager = NotificationManager()
    notification_manager.create_notifications(sample_json)

    generated_notifications = notification_manager.active_notification_list

    for index, value in enumerate(generated_notifications):
        assert value == expected_notifications[index]
