from utilities.helper import get_db_connection
import datetime
from flask import Flask


class srcape_request_data:

    @classmethod
    def put_request_history(cls, request_name, location_url_val, location_text, exclude_location, include_location_val, condition_url_val, buy_format_url_val, buy_format_text, min_price, max_price, sold_item, condition_text, min_quantity, max_quantity, include_exclude_btn, scheduler_time):
        connection, cursor = get_db_connection()
        cursor.execute("""INSERT INTO save_ebay_request_history(request_name,location_url_val,location_text_name,exclude_location,included_location_val,condition_url_val,buy_format_url_val,buy_format_text_name,min_price,max_price,sold_item,condition_text_name,min_quantity,max_quantity,include_exclude_btn,scheduler_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (request_name, location_url_val, location_text, exclude_location, include_location_val, condition_url_val, buy_format_url_val, buy_format_text, min_price, max_price, sold_item, condition_text, min_quantity, max_quantity, include_exclude_btn, scheduler_time))

        connection.commit()

    @classmethod
    def get_request_history(cls):
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""SELECT serh.*, 
                                (SELECT COUNT(*) 
                                FROM ebay_products ep 
                                WHERE serh.request_id = ep.request_id) AS matching_count,
								(SELECT count_gap FROM count_new_add_product_gap as cg WHERE serh.request_id = cg.request_id) AS count_gap 
                                FROM save_ebay_request_history serh;""")
            data = cursor.fetchall()
            return [dict(row) for row in data]
        except Exception as e:
            return e

    @classmethod
    def fatch_request_history_according_to_id(cls, request_id):
        connection, cursor = get_db_connection()
        cursor.execute('SELECT request_name,location_url_val,location_text_name,condition_url_val,exclude_location,included_location_val,buy_format_url_val,buy_format_text_name,min_price,max_price,sold_item,condition_text_name,min_quantity,max_quantity,include_exclude_btn From save_ebay_request_history WHERE request_id = %s', (request_id,))
        data = cursor.fetchone()
        return dict(data)

    @classmethod
    def get_location(cls):
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""SELECT location from locations""")
            location = cursor.fetchall()
            return [dict(row) for row in location]
        except Exception as error:
            return error

    @classmethod
    def delete_request_history_according_to_id(cls, request_id):
        connection, cursor = get_db_connection()
        cursor.execute(
            'Delete FROM save_ebay_request_history WHERE request_id = %s', (request_id,))
        connection.commit()

    @classmethod
    def update_request_history_according_to_id(cls, request_name, location_url_val, location_text, exclude_location, include_location_val, condition_url_val, buy_format_url_val, buy_format_text_name, min_price, max_price, sold_item, condition_text, min_quantity, max_quantity, include_exclude_btn, request_id):
        connection, cursor = get_db_connection()
        cursor.execute(
            """UPDATE save_ebay_request_history SET request_name = %s,location_url_val=%s, location_text_name=%s, exclude_location=%s,included_location_val =%s,condition_url_val=%s,buy_format_url_val=%s,buy_format_text_name=%s,min_price=%s,max_price=%s, sold_item=%s,condition_text_name=%s,min_quantity=%s,max_quantity=%s,include_exclude_btn=%s WHERE request_id = %s""", (request_name, location_url_val, location_text, exclude_location, include_location_val, condition_url_val,  buy_format_url_val, buy_format_text_name, min_price, max_price, sold_item, condition_text, min_quantity, max_quantity, include_exclude_btn, request_id))
        connection.commit()

    @classmethod
    def update_scraping_status(cls, request_id, scraping_status, created_at):
        try:
            app = Flask(__name__)
            with app.app_context():

                connection, cursor = get_db_connection()
                cursor.execute("""UPDATE save_ebay_request_history SET status = %s,  created_at = %s WHERE request_id = %s""",
                               (scraping_status, created_at, request_id))
                connection.commit()
        except Exception as e:
            return e

    @classmethod
    def get_last_request_id(cls):
        connection, cursor = get_db_connection()
        cursor.execute(
            """SELECT request_id From save_ebay_request_history ORDER BY request_id DESC LIMIT 1""")
        data = cursor.fetchone()
        for data in data:
            data = data
        return data

    @classmethod
    def get_pending_url(cls):
        try:
            app = Flask(__name__)
            with app.app_context():
                connection, cursor = get_db_connection()
                cursor.execute(
                    """SELECT * from save_ebay_request_history where status ='Scraped' """)
                data = cursor.fetchall()
                return [dict(row) for row in data]
        except Exception as e:
            return e

    @classmethod
    def lock_filter(cls, lock_location, lock_include_location, lock_condition, lock_buying_format, lock_min_price, lock_max_price, lock_min_qty, lock_max_qty, lock_sold_item, lock_request_name, include_location_check_val):
        try:
            connection, cursor = get_db_connection()
            cursor.execute("""
            INSERT INTO lock_filter (lock_location, lock_include_location, lock_condition, lock_buying_format, lock_min_price, lock_max_price, lock_min_qty, lock_max_qty, lock_sold_item, lock_request_name,include_location_check_val)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)""",
                           (lock_location, lock_include_location, lock_condition, lock_buying_format, lock_min_price, lock_max_price, lock_min_qty, lock_max_qty, lock_sold_item, lock_request_name, include_location_check_val))
            connection.commit()
        except Exception as error:
            return error

    @classmethod
    def get_filter_data(cls):
        connection, cursor = get_db_connection()
        cursor.execute(
            """SELECT lock_location,lock_include_location,lock_condition,lock_buying_format,lock_min_price,lock_max_price,lock_min_qty,lock_max_qty,lock_sold_item,lock_request_name,include_location_check_val from lock_filter ORDER BY lock_id DESC LIMIT 1""")
        lock_data = cursor.fetchone()
        return [row for row in lock_data]

    @classmethod
    def update_count_gap(cls, request_id):
        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """UPDATE count_new_add_product_gap SET count_gap = 0 where request_id=%s """, (request_id,))
            connection.commit()
        except Exception as error:
            return error
