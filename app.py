import concurrent
import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask_session import Session
import config
import queue as que
from models.ebay_request_history_model import srcape_request_data
from routes.ebay_scrape_route import ebay_scrape_bp
from routes.auth_route import auth_bp
from utilities.background_function import scrape_ebay_request, get_url_and_scrape
from utilities.helper import create_ebay_request_url
from globals import app, socketio
from threading import Thread


app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def start_scraping_job():
    try:
        if config.env == "local":
            print('background scheduler start')
            background_thread = Thread(
                target=get_url_and_scrape)
            background_thread.start()
        else:
            que.enqueue(get_url_and_scrape, job_timeout="6h")
        print(
            f'scraping job added in redis queue at: {datetime.datetime.utcnow()}')
    except Exception as e:
        return e


# start_scraping_job()

scheduler = BackgroundScheduler(daemon=True)
if not scheduler.running:
    scheduler.add_job(func=start_scraping_job, trigger="interval", minutes=30)
    scheduler.start()
    print(f'schedular started at: {datetime.datetime.now()}')

app.register_blueprint(ebay_scrape_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    socketio.run(app)
