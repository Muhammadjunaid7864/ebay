from utilities.helper import get_db_connection
from flask import flash


class auth:
    @classmethod
    def login(cls, username):
        connection, cursor = get_db_connection()
        error = None
        try:
            cursor.execute(
                """SELECT * From auth WHERE username = %s""", (username,))
            row = cursor.fetchone()
            if row:
                return row
            else:
                error = "no"
                return error
        except Exception as e:
            return e

    @classmethod
    def signup(cls, name, username, email, password):
        connection, cursor = get_db_connection()
        error = None
        if error is None:
            try:
                cursor.execute(
                    """SELECT * From auth WHERE username = %s""", (username,))
                row = cursor.fetchone()
                if row:
                    error = "User already Exits"
                else:
                    cursor.execute(
                        """INSERT INTO auth (name,username,password,email) VALUES(%s,%s,%s,%s)""", (name, username, password, email))
                    connection.commit()
            except Exception as e:
                return e
        return error
