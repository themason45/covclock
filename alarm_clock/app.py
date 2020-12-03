"""
The main application startup code.

Run with:

  python app.py

Written By: Sam Mason
Date: Nov 2020

"""
import logging
import os

from dotenv import load_dotenv
from flask import Flask

from alarm_clock.support import format_datetime, context_vars, context_funcs
from alarm_clock.views import create_alarm, delete_alarm, index, \
    run_scheduler, alarm_post, delete_notification

load_dotenv(dotenv_path='../.env')

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

logger = logging.getLogger(os.getenv("COVCLOCK_LOG_NAMESPACE"))
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(filename="applog.txt"))
logger.addHandler(logging.StreamHandler())

for f in context_funcs:
    app.add_template_global(f)

for k, v in context_vars.items():
    app.add_template_global(v, name=k)

app.add_template_filter(format_datetime)
app.add_url_rule('/', 'index', index)
app.add_url_rule('/alarm_post/', 'alarm_post', alarm_post, methods=["POST"])
app.add_url_rule('/run_scheduler', 'run_scheduler', run_scheduler)
app.add_url_rule('/set_alarm', 'set_alarm', create_alarm, methods=["POST"])
app.add_url_rule('/delete_alarm/<alarm_index>', 'delete_alarm', delete_alarm, methods=["DELETE"])
app.add_url_rule('/delete_notification/<notification_index>', 'delete_notification',
                 delete_notification, methods=["DELETE"])

if __name__ == '__main__':
    app.run(host="0.0.0.0")
