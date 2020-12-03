"""
Tests for alarm modules

Written By: Sam Mason
Date: Nov 2020
"""

from datetime import datetime

from alarm_clock.alarm.models import Alarm


def test_alarm_action():
    """
    Tests all the data types of an Alarm
    :return: None
    """
    alarm = Alarm(selected_time=datetime.now(), include_covid=True,
                  include_news=True, include_weather=True,
                  announcement=True, test_mode=True)

    information, sentences = Alarm.alarm_action(datetime.now(), alarm)

    # Check that its bundled the info without any errors
    assert information.get("covid") is not None
    assert "nationally" and "locally" in information.get("covid").keys()

    assert information.get("news") is not None
    assert isinstance(information.get("news"), list)

    assert information.get("weather") is not None
    assert isinstance(information.get("weather"), dict)

    # Check that there are enough sentences
    assert len(sentences) >= 5
