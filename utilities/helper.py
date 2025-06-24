from urllib.parse import urlencode

from flask import g, request, jsonify, session, redirect, url_for, Flask
from functools import wraps
import config

import psycopg2
import psycopg2.extras

# rds config
rds_host = config.db_host
port = config.db_port
username = config.db_username
password = config.db_password
database_name = config.db_name


def openDbconnection():
    try:
        connection = psycopg2.connect(
            database=database_name, user=username, password=password, host=rds_host, port=port)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return connection, cursor
    except Exception as e:
        print(e)
        return False


def closeDbconnection(connection):
    return connection.close()


def get_db_connection():
    if 'connection' not in g or 'cursor' not in g:
        g.connection, g.cursor = openDbconnection()
    return g.connection, g.cursor


def destroy_db_connection():
    connection = g.pop("connection", None)
    cursor = g.pop("cursor", None)
    if connection is not None:
        if connection.open:
            connection.close()


def create_ebay_request_url(requests):
    try:
        requests_data = []
        for request in requests:
            params_list = ["rt=nc", "_ipg=60", "rt=nc"]
            for key, value in request.items():
                if key == "condition_url_val":
                    params_list.append(
                        f"LH_ItemCondition={'|'.join(condition.strip() for condition in value.split(','))}")
                if key == "request_name":
                    params_list.append(f"_nkw={value}")
                if key == "location_url_val":
                    params_list.append(f"LH_PrefLoc={value}")
                if key == "min_price":
                    params_list.append(f"_udlo={value}")
                if key == "max_price":
                    params_list.append(f"_udhi={value}")
                if key == "buy_format_url_val" or "sold_item":
                    params_list.append(value)

            query_str = urlencode(params_list)
            requests_data.append({"request_id": request.get("request_id"),
                                  "locations": request.get("include_location"),
                                  "request_url": f"https://www.ebay.com/sch/i.html?{query_str}"})
    except Exception as error:
        return error


def success(resp=None, data=None):
    if resp is None:
        resp = jsonify({
            "message": "success",
            "type": "success",
            "status": 200,
            "data": data if not data else []
        })
    resp.status_code = 200
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    return resp


def login_required(f):
    try:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            app = Flask(__name__)
            # with app.app_context():
            #     logged_user = request.cookies.get('username')
            # if not logged_user:
            #     return redirect("/login")

            if session.get("username"):
                pass

            else:
                return redirect('/login')

            return f(*args, **kwargs)

        return decorated_function
    except Exception as e:
        return e


def add_log(event, msg, type='success'):
    try:
        connection, cursor = openDbconnection()
        cursor.execute(
            f"""INSERT INTO scraping_logs(event_name, msg, event_type) VALUES (%s, %s, %s);""", (event, msg, type))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print("add_log error: ", str(e))
        return False
