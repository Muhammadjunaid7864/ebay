import uuid
import re
import config

from utilities.helper import get_db_connection


class ebay_products:

    @classmethod
    def put_ebay_products(cls, data, request_id):
        try:
            connection, cursor = get_db_connection()

            inserting_data = []
            for product in data:
                price_match = re.search(r'\d+\.\d+', product.get("price"))
                inserting_data.append((str(uuid.uuid4()), product.get("product"), product.get("img"), product.get("condition"),
                                       (float(price_match.group()) if price_match else 0), product.get("location"), request_id))

            if len(inserting_data) > 0:
                cursor.executemany(f"""INSERT INTO (ebay_id,title,img_url`,condition,price,location,request_id) 
                                        VALUES (%s,%s,%s,%s,%s,%s,%s)""", inserting_data)
                connection.commit()
            return True
        except Exception as error:
            return error

    @classmethod
    def get_ebay_product(cls, request_id):
        try:
            connection, cursor = get_db_connection()
            cursor.execute(
                """SELECT ebay_id,title,img_url,condition,price,location,details_page_url FROM ebay_products WHERE request_id = %s""", (request_id,))
            row = cursor.fetchall()
            return row
        except Exception as error:
            return error
