"""
Runs highest level tests on Alarms and Notifications


Written By: Sam Mason
Date: Nov 2020

"""

import json
from datetime import datetime

from alarm_clock.alarm.manager import AlarmManager
from alarm_clock.alarm.models import Alarm
from alarm_clock.notifications.manager import NotificationManager


def test_all():
    """
    Tests alarm and notification objects
    :return: None
    """
    # Generate the managers
    alarm_manager = AlarmManager(test_mode=True)
    notification_manager = NotificationManager()

    # Set an example alarm
    alarm_manager.set(datetime.now(), include_covid=True, include_news=True,
                      include_weather=True, is_audible=True)

    assert len(alarm_manager.active_alarms) > 0  # Check that the alarm was created properly

    information, _ = Alarm.alarm_action(datetime.now(),
                                        alarm_manager.active_alarms[0])  # Perform the alarm action

    notification_manager.create_notifications(json.dumps(information))
    # Check that enough notifications have been added to the list
    assert len(
        notification_manager.active_notification_list) > 3
