from flask import Blueprint
from controllers.auth_controller import login, sign_up, logout
auth_bp = Blueprint('auth_bp', __name__)

auth_bp.route('/login', methods=['POST', 'GET'])(login)
auth_bp.route('/sign_up', methods=['POST', 'GET'])(sign_up)
auth_bp.route('/logout', methods=['POST', 'GET'])(logout)
