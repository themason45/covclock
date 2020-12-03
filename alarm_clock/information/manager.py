"""
This module contains the manager for NewsItems. This creates,
and returns a list of the latest news stories.
However, this is not persistent for the lifetime of the app.

In order to make it more efficient overall a persistent local cache
of news items could be created, however, it would
be difficult to keep track of which stories have already been collected.
"""
import os

import requests

from alarm_clock.information.models import NewsItem


# pylint: disable=R0903
class NewsManager:
    """
    Manages news stories, retrieving them from an open web service
    """
    stories = []

    def get_stories(self, count=5):
        """
        Get a list of news stories from the news api, then create NewItem objects based on them.

        :return: List of :class:`alarm_clock.information.models.NewsItem` instances
        :rtype: list
        """
        self.stories.clear()
        resp = requests.get(
            "{0}?country={1}&apiKey={2}".format(os.getenv("COVCLOCK_NEWS_API_URL_ROOT"),
                os.getenv("COVCLOCK_NEWS_API_COUNTRY"), os.getenv("COVCLOCK_NEWS_API_KEY")))

        if resp.status_code == 200:
            all_stories = resp.json().get("articles")
            for i in range(0, count):
                try:
                    self.stories.append(NewsItem(all_stories[i]))
                except IndexError:
                    pass  # If there are fewer than the count, then pass softly

            return self.stories
        return []
