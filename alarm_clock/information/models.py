"""
This module contains classes for all the API response related items.
It contains one struct for news items, and two objects for Covid and Weather updates,
which self populate with the API response.

"""
import logging
import os

import requests

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))


# Data structures, the API has different available data depending on whether it is national,
# or local data
# See: https://coronavirus.data.gov.uk/details/developers-guide#structure-metrics

# pylint: disable=R0903,W0703
class NewsItem:
    """
    Stores the data for a single News Item
    """
    title = ""  # type: str
    description = ""  # type: str
    url = ""  # type: str
    source_name = ""  # type: str
    img_source = ""  # type: str

    def __init__(self, i_json):
        self.title = i_json.get("title", "")
        self.description = i_json.get("description", "")
        self.url = i_json.get("url", "")
        self.source_name = i_json.get("source", {}).get("name")
        self.img_source = i_json.get("urlToImage", "")

    def serialize(self):
        """
        Make the NewsItem JSON readable

        :return: A serialized version of the instance
        :rtype: dict
        """
        return {"title": self.title, "description": self.description, "url": self.url,
            "image_src": self.img_source}


class WeatherUpdate:
    """
    Stores the data for a single Weather Update
    """
    description = ""  # type: str
    temp = 0.0  # type: float
    precip_chance = 0.0  # type: float

    @staticmethod
    def populate():
        """
        Create a WeatherUpdate instance with data straight from the API, and return this object
        """
        # pylint: disable=C0301
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units={units}".format(
                city_name=os.getenv("COVCLOCK_WEATHER_CITY"),
                api_key=os.getenv("COVCLOCK_WEATHER_API_KEY"),
                units=os.getenv("COVCLOCK_WEATHER_UNIT")))

        if resp.status_code == 200:
            json_resp = resp.json()
            try:
                data = json_resp.get("list")[0]

                wu_object = WeatherUpdate()
                wu_object.description = data.get("weather", [])[0].get("description", "")
                wu_object.temp = data.get("main", {}).get("temp", 0)
                wu_object.precip_chance = data.get("pop", 0.0)

                return wu_object
            except IndexError:
                return None

            except Exception as exception:
                logger.error(exception)
        else:
            return None

    def serialize(self):
        """
            Make the WeatherUpdate JSON readable
        """
        return {"description": self.description, "temp": self.temp,
                "precip_chance": self.precip_chance}


class CovidUpdate:
    """
    Stores the data for a single COVID Update
    """
    local = False  # type: bool
    new_deaths = -1  # type: int
    cum_deaths = -1  # type: int
    new_cases = -1  # type: int
    cum_cases = -1  # type: int

    LOCAL_PAYLOAD = {"areaType": os.getenv("COVCLOCK_AREA_TYPE", "utla"),
        "areaCode": os.getenv("COVCLOCK_AREA_CODE", "E10000008"),
        "metric": ["newCasesByPublishDate", "cumDeaths28DaysByPublishDate",
                   "newDeaths28DaysByPublishDate"], "format": "json"}  # type: dict

    NATIONAL_PAYLOAD = {"areaType": "overview",
        "metric": ["newCasesByPublishDate", "cumDeaths28DaysByPublishDate",
                   "newDeaths28DaysByPublishDate"], "format": "json"}  # type: dict

    @staticmethod
    def populate(local=False):
        """
            Create a CovidUpdate instance with data straight from the API, and return this object.

            :return: A populated :class:`.CovidUpdate` instance
            :rtype: CovidUpdate
        """
        if local:
            payload = CovidUpdate.LOCAL_PAYLOAD
        else:
            payload = CovidUpdate.NATIONAL_PAYLOAD

        resp = requests.get(
            os.getenv("COVCLOCK_COVID_API_URL_ROOT", "https://api.coronavirus.data.gov.uk/v2/data"),
            params=payload)

        if resp.status_code == 200:
            resp_data = resp.json()
            body = resp_data.get("body", [None])
            # day_before_cum = body[1].get("cumDeathsByDeathDate", 0)
            #    if body[1].get("cumDeathsByDeathDate", 0) else 0

            data = body[0]
            # today_deaths = data.get("newDeathsByDeathDate", 0)
            #    if data.get("newDeathsByDeathDate", 0) else 0
            # cum_deaths = day_before_cum + today_deaths

            cu_object = CovidUpdate()
            cu_object.new_cases = data.get("newCasesByPublishDate", 0) if data.get(
                "newCasesByPublishDate", 0) else 0
            cu_object.new_deaths = data.get("newDeaths28DaysByPublishDate", 0) if data.get(
                "newDeaths28DaysByPublishDate", 0) else 0
            cu_object.cum_deaths = data.get("cumDeaths28DaysByPublishDate", 0) if data.get(
                "cumDeaths28DaysByPublishDate", 0) else 0
            cu_object.local = local
            return cu_object

        return None
