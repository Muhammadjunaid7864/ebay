# MYSQL_HOST = 'localhost'
# MYSQL_PORT = 3306
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'root'
# MYSQL_DB = 'ebayscrape'

import os

DATABASE_URL = os.environ.get('DATABASE_URL', None)

# DATABASE_URL = "postgres://zpnnjmyoygprxh:6efc3e6a7f94d509b40844ce3726173a409684ed6dd5347bc698599f4aa46737@ec2-54-211-177-159.compute-1.amazonaws.com:5432/d16bn63aq952mp"
env = "local"
# env = "production"
# postgre config
print("DATABASE_URL => ", DATABASE_URL)
db_cred_part = DATABASE_URL.replace("postgres://", "").split("@")[0]
db_username = db_cred_part.split(':')[0]
db_password = db_cred_part.split(':')[1]

db_res_part = DATABASE_URL.replace("postgres://", "").split("@")[1]
db_host = db_res_part.split('/')[0].split(':')[0]
db_port = db_res_part.split('/')[0].split(':')[1]
db_name = db_res_part.split('/')[1]
schema = "public"
