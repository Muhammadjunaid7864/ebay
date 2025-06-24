from flask import Blueprint

from controllers.ebay_scrape_controller import ebay_scrape_data, ebay_scrape_request_history, get_ebay_request_history, request_history, fetch_request_history_according_id, delete_request_history_according_id, update_history_according_to_id, product_csv_file, get_scraped_product_data_on_view, post_lock_filter, get_lock_filter_data


ebay_scrape_bp = Blueprint('ebay_scrape_bp', __name__)

ebay_scrape_bp.route('/', methods=["GET", "POST"])(ebay_scrape_data)
ebay_scrape_bp.route('/ebay_scrape_request_history',
                     methods=['GET', 'POST'])(ebay_scrape_request_history)
ebay_scrape_bp.route('/get_ebay_request_query_history', methods=[
                     "GET", "POST"])(get_ebay_request_history)
ebay_scrape_bp.route('/get_request_history',
                     methods=['GET', 'POST'])(request_history)

ebay_scrape_bp.route('/fetch_request_history_according_to_id',
                     methods=['GET', 'POST'])(fetch_request_history_according_id)
ebay_scrape_bp.route('/delete_request_history_according_to_id',
                     methods=['POST'])(delete_request_history_according_id)
ebay_scrape_bp.route('/update_request_history_according_to_id',
                     methods=['POST', 'GET'])(update_history_according_to_id)
ebay_scrape_bp.route('/get_product_csv',
                     methods=['POST', 'GET'])(product_csv_file)
ebay_scrape_bp.route('/get_scraped_data_on_view',
                     methods=['POST', 'GET'])(get_scraped_product_data_on_view)
ebay_scrape_bp.route('/post_filter_lock',
                     methods=['POST', 'GET'])(post_lock_filter)
ebay_scrape_bp.route('/get_lock_filter',
                     methods=['POST', 'GET'])(get_lock_filter_data)
