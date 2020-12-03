"""
This module just contains some extra functions that can be useful around the app

Written By: Sam Mason
Date: Nov 2020

"""
import os
from datetime import datetime, timedelta


def format_datetime(value):
    """
    This is a jinja2 filter that makes the date look good on the screen. As seen by:
    `app.add_template_filter(format_datetime)` \n
    :param value:
    :return:
    """
    return value.strftime("%H:%M")


def current_time():
    """
    This is a context object, it is passed to all templates by default.
    :return:
    """
    return format_datetime(datetime.now())


def shifted_time():
    """
    This is a context object, it is passed to all templates by default, this one just passes
    the time +1 for the alarm form.
    :return:
    """
    return format_datetime(datetime.now() + timedelta(minutes=1))


context_funcs = [current_time, shifted_time]
context_vars = {
    "number_of_days": int(os.getenv("COVCLOCK_NUMBER_OF_DAYS", "50")),
    "refresh_delay": int(os.getenv("COVCLOCK_REFRESH_DELAY", "3600"))
}
