"""
Tests for information modules

Written By: Sam Mason
Date: Nov 2020
"""

from alarm_clock.information.manager import NewsManager
from alarm_clock.information.models import CovidUpdate, WeatherUpdate


def test_covid_object():
    """
    Tests population of covid objects from web services
    :return: None
    """
    local_update = CovidUpdate.populate(local=True)
    national_update = CovidUpdate.populate(local=False)

    assert local_update is not None
    assert national_update is not None


def test_news_manager():
    """
    Tests population of news objects from web services
    :return: None
    """
    news_manager = NewsManager()
    news_manager.get_stories(count=5)

    assert len(news_manager.stories) <= 5  # The API may not supply enough stories (slow news day)


def test_weather_object():
    """
    Tests population of weather objects from web services
    :return: None
    """
    weather_update = WeatherUpdate.populate()

    assert weather_update is not None
