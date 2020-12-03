"""
This contains a model for a notification, and a method to render this notification in html
"""
from flask import render_template


class Notification:
    """
    A Notification object and associated methods
    """
    title = ""  # type: str
    image_src = ""  # type: str
    content = ""  # type: str
    action = ""  # type: str

    def __init__(self, title, content, action, image_src=""):
        self.title = title
        self.content = content
        self.action = action
        self.image_src = image_src if image_src else ""

    def render_notification(self, index) -> str:
        """
        Render the notification's list item, and return the HTML string

        :param index: Notification index
        :return str: HTML string
        """
        return render_template("sections/notification_row.html", item=self, index=index)

    @property
    def has_image(self) -> bool:
        """
        Return whether the Notification has an image source

        :return bool:
        """
        return len(self.image_src) > 0

    def __eq__(self, other):
        return (self.title == other.title) and (self.image_src == other.image_src) and \
            (self.content == other.content) and (self.action == other.action)
