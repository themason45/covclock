"""
Defines the views for the application

Written By: Sam Mason
Date: Nov 2020

"""
import logging
import os
from datetime import datetime

from flask import render_template, request

from alarm_clock.alarm.manager import AlarmManager
from alarm_clock.notifications.manager import NotificationManager

am = AlarmManager(add_placeholder_alarms=True)
nm = NotificationManager(add_placeholders=False)

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))

# pylint: disable=W0703


def index():
    """
    Loads the home page - home.html file
    :return: the rendered page
    """
    logger.info("Loaded index")
    return render_template('home.html', alarms=am.get(),
                           notification_manager=nm)


def run_scheduler():
    """
    Runs a new scheduler

    :return: The status of the sheduled event
    """
    refresh_after = am.trigger_refresh
    am.trigger_refresh = False
    try:
        am.scheduler.run(blocking=False)
    except AttributeError as exception:
        # Sometimes it throws an error when it tries calling scheduler.run while its
        # midway through already running the scheduled action. This just ignores that error
        logger.info('Ignored: %s', exception)

    # If an alarm has recently gone off, notify the front end, and it will refresh the page, to
    # accommodate the new notification
    return {'status': "success",
            "should_reset": refresh_after}


def alarm_post():
    """
    When an alarm goes off, tell the notification manager

    :return: status of the function
    """
    data = request.get_data()
    try:
        nm.clear_notifications()
        nm.create_notifications(data)

        am.trigger_refresh = True
        logger.info("Notification manager updated")
        return {'status': "success"}
    except ValueError as exception:
        logger.error(data)
        logger.error(exception)
        return {'status': "failed"}
    except Exception as exception:
        logger.error(data)
        logger.error(exception)
        return {'status': "failed"}


def create_alarm():
    """
    Creates a new Alarm

    :return: The status of the alarm create
    """
    data = request.form
    selected_time = datetime.strptime(data.get("time"), "%H:%M")
    status = am.set(selected_time,
                    include_covid=data.get("select_covid", "false") == "true",
                    include_news=data.get("select_news", "false") == "true",
                    include_weather=data.get("select_weather", "false") == "true",
                    is_audible=data.get("audible_announcement", "false") == "true")
    logger.info("Alarm created" if status > -1 else "Alarm creation failed")
    return {'status': "success" if status > -1 else "failed"}


def delete_alarm(alarm_index):
    """
    Deletes an alarm given its index

    :param alarm_index:
    :return: Status of the delete
    """
    successful = am.unset(alarm_index)
    logger.info("Alarm deleted" if successful else "Alarm deletion failed")
    return {'status': "success" if successful else "failed"}


def delete_notification(notification_index):
    """
    Delete a notification given its index

    :param notification_index:
    :return: Status of the delete
    """
    successful = nm.delete_notification(notification_index)
    logger.info("Notification deleted" if successful else "Notification deletion failed")
    return {'status': "success" if successful else "failed"}
