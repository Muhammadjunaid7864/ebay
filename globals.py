from flask import Flask
from flask_socketio import SocketIO

import config


# init flask and session
app = Flask(__name__)
# app.secret_key = '656c0adda3bb3f990a6f'
# app.config['SESSION_TYPE'] = 'filesystem'
# app.debug = True

socketio = SocketIO(app, manage_session=False)

if config.env == "production":
    from rq import Queue
    from worker import conn
    print("creating queue")
    que = Queue(connection=conn)
