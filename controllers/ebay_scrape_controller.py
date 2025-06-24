import ast
import sys
import re
from flask import render_template, jsonify, request, redirect, url_for, Response
import requests
from globals import socketio
import io
import csv
import datetime
from utilities.background_function import parse_ebay_products, scrape_ebay_request
from models.ebay_request_history_model import srcape_request_data
from models.ebay_products import ebay_products
from bs4 import BeautifulSoup
import threading
import concurrent
from lxml import etree
from utilities.helper import success, login_required, add_log
import shutil
thread_pool_executor = None
submitted_tasks = []
products = None
# scrape_flag_thread = True
scrape_thread = None
event = None


def cancel_all_scraping_threads():
    global thread_pool_executor
    global submitted_tasks
    global scrape_event
    global scrape_thread

    if scrape_thread:
        scrape_event.set()

    if thread_pool_executor:
        for task in submitted_tasks:
            task.cancel()
        thread_pool_executor.shutdown(cancel_futures=True)

        thread_pool_executor = None
        submitted_tasks = []


@login_required
def ebay_scrape_data():
    try:
        if request.method == 'POST':
            request_id = request.args.get("request")
            location_val = request.form.get('location')
            exclude_location_val = request.form.getlist('exclude_location[]')
            condition_val = request.form.getlist('condition[]')
            buy_format_val = request.form.get('buy_format')
            min_val = request.form.get('min')
            max_val = request.form.get('max')
            min_quanity = request.form.get('min_quantity')
            max_quanity = request.form.get('max_quantity')
            item_sold_val = request.form.get('item_sold')
            search_box = request.form.get('searchtext')
            btn_off_on = request.form.get('btn_on_off')

            new_list = []
            if btn_off_on == "on":
                for item in exclude_location_val:
                    countries = item.split(',')
                    new_countries = [country + '1' for country in countries]
                    new_list.extend(new_countries)
            else:
                for item in exclude_location_val:
                    countries = item.split(',')
                    new_countries = [country + '2' for country in countries]
                    new_list.extend(new_countries)

            condition_list = []
            if len(condition_val) > 1:
                for condition_val in condition_val:
                    condition_val = '|'+condition_val
                    condition_list.append(condition_val)
                item = ''.join(str(item) for item in condition_list)
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_box}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_val}&{buy_format_val}&rt=nc&_udlo={min_val}&_udhi={max_val}&LH_ItemCondition={item}&{item_sold_val}&rt=nc"

            elif condition_val:
                for condition_val in condition_val:
                    condition_val = condition_val
                    url = f"https://www.ebay.com/sch/i.html?_nkw={search_box}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_val}&{buy_format_val}&rt=nc&_udlo={min_val}&_udhi={max_val}&LH_ItemCondition={condition_val}&{item_sold_val}&rt=nc"
            else:
                url = f"https://www.ebay.com/sch/i.html?_nkw={search_box}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_val}&{buy_format_val}&rt=nc&_udlo={min_val}&_udhi={max_val}&{item_sold_val}&rt=nc"
            url = f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={url}"

            get_request = requests.get(url)
            get_request_text = get_request.text
            soup = BeautifulSoup(get_request_text, 'html.parser')
            results = soup.find(
                'h1', {'class': 'srp-controls__count-heading'}).find('span', {'class', 'BOLD'})
            results_count_text = results.get_text()

            results_count = int(re.sub(r',', '', results_count_text))
            results_count = 10000 if results_count > 10000 else results_count
            page_num_for_append_url = results_count/60

            cancel_all_scraping_threads()

            global scrape_thread
            global scrape_event
            scrape_event = threading.Event()
            scrape_thread = threading.Thread(target=main_fun_scrape_ebay_data, args=(
                url, new_list, min_quanity, max_quanity, page_num_for_append_url, scrape_event))
            scrape_thread.start()

            return success(data={"msg": "Scraping has been started"})

        else:
            request_id = request.args.get("request")

            if request_id:
                cancel_all_scraping_threads()
                request_id = request.args.get("request")
                location = srcape_request_data.get_location()
                location_list = []
                for i in range(len(location)):
                    location_data = {
                        'location': location[i]['location']
                    }
                    location_list.append(location_data)
                data = srcape_request_data.fatch_request_history_according_to_id(
                    request_id=request_id)
                request_history_data = {
                    'request_id': request_id,
                    'request_name': data['request_name'],
                    'location': data['location_text_name'],
                    'location_url': data['location_url_val'],
                    'exclude_location': data['exclude_location'],
                    'included_location_val': data['included_location_val'],
                    'condition': data['condition_text_name'],
                    'condition_url_val': data['condition_url_val'],
                    'buy_format': data['buy_format_text_name'],
                    'buy_format_url_val': data['buy_format_url_val'],
                    'min_price': data['min_price'],
                    'max_price': data['max_price'],
                    'min_quantity': data['min_quantity'],
                    'max_quantity': data['max_quantity'],
                    'sold_item': data['sold_item'],
                    'include_exclude_btn': data['include_exclude_btn']
                }
                return render_template('tables.html', request_data=request_history_data, location_list=location_list)
            else:
                cancel_all_scraping_threads()
                location = srcape_request_data.get_location()
                location_list = []
                for i in range(len(location)):
                    location_data = {
                        'location': location[i]['location']
                    }
                    location_list.append(location_data)
                return render_template('tables.html', location_list=location_list)
    except Exception as error:
        return error


def main_fun_scrape_ebay_data(url, location, min_quantity, max_quanity, page_num_for_Append_url, event):
    global thread_pool_executor
    global submitted_tasks

    thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=10)

    for page_num in range(1, int(page_num_for_Append_url)):
        if event.is_set():
            break

        request_url = f"{url}&_pgn={page_num}"
        get_request = requests.get(request_url)
        get_request_text = get_request.text
        soup = BeautifulSoup(get_request_text, 'html.parser')

        dom = etree.HTML(str(soup))
        products = dom.xpath(
            "//div[contains(@class, 'srp-river-results')]/ul/li[contains(@class, 's-item')]")

        locations = [location]
        for product in products:
            if event.is_set():
                break
            task = thread_pool_executor.submit(
                parse_ebay_products, (product, locations, min_quantity, max_quanity, True))
            submitted_tasks.append(task)


def ebay_scrape_request_history():
    if request.method == 'POST':
        location_url_val = request.form.get('location_url_val')
        location_text = request.form.get('location_text')
        exclude_location_val = str(request.form.getlist('exclude_location[]'))
        include_location_val = str(
            request.form.getlist('exclude_location_val[]')),
        condition_url_val = str(request.form.getlist('condition_url_val[]'))
        condition_text = str(request.form.getlist('condition_text[]'))
        buy_format_url = request.form.get('buy_format_url_val')
        buy_format_text = request.form.get('buy_format')
        min_price = request.form.get('min')
        max_price = request.form.get('max')
        min_quantity = request.form.get('min_quantity')
        max_quantity = request.form.get('max_quantity')
        sold_item_val = request.form.get('item_sold')
        search_text_val = request.form.get('searchtext')
        condition_url_val = condition_url_val
        include_location = request.form.get("include_location_val")
        scheduler_time = request.form.get('scheduler_time')
        include_exclude_btn = request.form.get('include_location_val')

        new_list = []
        if include_exclude_btn == "on":
            for item in include_location_val:
                countries = item.split(',')
                new_countries = [country + '1' for country in countries]
                new_list.extend(new_countries)
        else:
            for item in include_location_val:
                countries = item.split(',')
                new_countries = [country + '2' for country in countries]
                new_list.extend(new_countries)

        srcape_request_data.put_request_history(
            request_name=search_text_val, location_url_val=location_url_val, location_text=location_text, exclude_location=exclude_location_val, include_location_val=include_location_val, condition_url_val=condition_url_val, buy_format_url_val=buy_format_url, buy_format_text=buy_format_text, min_price=min_price, max_price=max_price, sold_item=sold_item_val, condition_text=condition_text, min_quantity=min_quantity, max_quantity=max_quantity, include_exclude_btn=include_location, scheduler_time=scheduler_time)
        include_location = [include_location]
        condition_val = request.form.getlist('condition[]')
        condition_list = []
        if len(condition_val) > 1:
            for condition_val in condition_val:
                condition_val = '|'+condition_val
                condition_list.append(condition_val)
            item = ''.join(str(item) for item in condition_list)
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&LH_ItemCondition={item}&{sold_item_val}&rt=nc"

        elif condition_val:
            # for condition_val in condition_val:
            #     condition_val = condition_val
            condition_val = condition_val[0]
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&LH_ItemCondition={item}&{sold_item_val}&rt=nc"

        else:
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&{sold_item_val}&rt=nc"
        url = f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={url}"
        request_id = srcape_request_data.get_last_request_id()
        t = threading.Thread(target=scrape_ebay_request,
                             args=(url, new_list, min_quantity, max_quantity, request_id))
        t.start()
    return 'OK'


@login_required
def get_ebay_request_history():
    data = srcape_request_data.get_request_history()
    new_data = [{
        "serial": index+1,
        "id": row.get("request_id"),
        "name": row.get("request_name"),
        "location": row.get("location_text_name"),
        "excludedLocations": ", ".join(ast.literal_eval(row.get("exclude_location"))) if row.get("exclude_location") and row.get("exclude_location").strip() != '' else "",
        "conditions": ", ".join(ast.literal_eval(row.get("condition_text_name"))) if row.get("condition_text_name") and row.get("condition_text_name").strip() != '' else "",
        "buyFormat": row.get("buy_format_text_name"),
        "minPrice": row.get("min_price"),
        "maxPrice": row.get("max_price"),
        "soldItem": "Yes" if row.get("sold_item") == "LH_Sold=1" else "No",
        "scraped_at": row.get('created_at'),
        "status": row.get('status'),
        'match_count': row.get('matching_count'),
        'scheduler_time': row.get('scheduler_time'),
        'count_gap': row.get('count_gap')
    } for index, row in enumerate(data)]

    return jsonify(new_data)


@login_required
def request_history():
    return render_template('ebayscraphistory.html')


@login_required
def fetch_request_history_according_id():
    request_id = request.form.get('request_id')

    return 'OK'


@login_required
def delete_request_history_according_id():
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        srcape_request_data.delete_request_history_according_to_id(
            request_id=request_id)

    return 'OK'


@login_required
def update_history_according_to_id():
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        if request_id:
            request_id = request.form.get('request_id')
            location_url_val = request.form.get('location_url')
            location_text = request.form.get('location_text')
            exclude_location_val = str(
                request.form.getlist('exclude_location[]'))
            include_location_val = str(
                request.form.getlist('exclude_location_val[]')),
            condition_url_val = str(
                request.form.getlist('condition_url_val[]'))
            condition_text = str(request.form.getlist('condition_text[]'))
            buy_format_url = request.form.get('buy_format_url_val')
            buy_format_text = request.form.get('buy_format')
            min_price = request.form.get('min')
            max_price = request.form.get('max')
            min_quantity = request.form.get('min_quantity')
            max_quantity = request.form.get('max_quantity')
            sold_item_val = request.form.get('item_sold')
            search_text_val = request.form.get('searchtext')
            include_exclude_btn = request.form.get('include_location_val')
            srcape_request_data.update_request_history_according_to_id(
                request_name=search_text_val, location_url_val=location_url_val, location_text=location_text, exclude_location=exclude_location_val, include_location_val=include_location_val, condition_url_val=condition_url_val, buy_format_url_val=buy_format_url, buy_format_text_name=buy_format_text, min_price=min_price, max_price=max_price, sold_item=sold_item_val, condition_text=condition_text, min_quantity=min_quantity, max_quantity=max_quantity, include_exclude_btn=include_exclude_btn, request_id=request_id)

            include_location_val = request.form.getlist(
                'exclude_location_val[]')
            new_list = []
            if include_exclude_btn == "on":
                for item in include_location_val:
                    countries = item.split(',')
                    new_countries = [country + '1' for country in countries]
                    new_list.extend(new_countries)
            else:
                for item in include_location_val:
                    countries = item.split(',')
                    new_countries = [country + '2' for country in countries]
                    new_list.extend(new_countries)
        condition_val = request.form.getlist('condition[]')
        condition_list = []
        if len(condition_val) > 1:
            for condition_val in condition_val:
                condition_val = '|'+condition_val
                condition_list.append(condition_val)
            item = ''.join(str(item) for item in condition_list)
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&LH_ItemCondition={item}&{sold_item_val}&rt=nc&_sop=12"

        elif condition_val:
            # for condition_val in condition_val:
            #     condition_val = condition_val
            condition_val = condition_val[0]
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&LH_ItemCondition={item}&{sold_item_val}&rt=nc&_sop=12"

        else:
            url = f"https://www.ebay.com/sch/i.html?_nkw={search_text_val}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={location_url_val}&{buy_format_url}&rt=nc&_udlo={min_price}&_udhi={max_price}&{sold_item_val}&rt=nc&_sop=12"
        url = f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={url}"
        t = threading.Thread(target=scrape_ebay_request,
                             args=(url, new_list, min_quantity, max_quantity, request_id))
        t.start()
    return 'OK'


@login_required
def product_csv_file():
    try:
        request_id = request.args.get("request")
        request_id = int(request_id)
        data = ebay_products.get_ebay_product(request_id=request_id)
        output = io.StringIO()
        write = csv.writer(output)
        header_row = ['ID', 'Title', 'Image url',
                      'Conditions', 'Price', 'Location']
        write.writerow(header_row)

        for row in data:
            line = [row['ebay_id'], row['title'], row['img_url'],
                    row['condition'], str(row['price']), row['location']]
            write.writerow(line)

        output.seek(0)
        return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename=scraped_data-{datetime.datetime.utcnow().strftime('%H%M%S')}.csv"})
    except Exception as error:
        return error


@login_required
def get_scraped_product_data_on_view():
    try:
        request_id = request.args.get("request")
        new_data = []
        if request_id:
            request_id = request.args.get("request")
            data = ebay_products.get_ebay_product(request_id=request_id)
            for i in range(len(data)):
                dict_data = {
                    'img_url': data[i][2],
                    'title': data[i][1],
                    'price': data[i][4],
                    'condition': data[i][3],
                    'location': data[i][5],
                    'details_page_link': data[i][6]
                }
                new_data.append(dict_data)
                srcape_request_data.update_count_gap(request_id=request_id)

            return jsonify(new_data)

        return True
    except Exception as error:
        return add_log("scrape_ebay_request", f'/line number: {sys.exc_info()[2].tb_lineno} Exception: \n{str(error)}', type='error')


@login_required
def post_lock_filter():
    try:
        if request.method == 'POST':
            lock_location = request.form.get('lock_location')
            lock_included_location = request.form.getlist(
                'lock_included_location[]')
            lock_condition = request.form.getlist('lock_condition[]')
            lock_buy_format = request.form.get('lock_buy_format')
            lock_min_price = request.form.get('lock_min_price')
            lock_max_price = request.form.get('lock_max_price')
            lock_min_qty = request.form.get('lock_min_qty')
            lock_max_qty = request.form.get('lock_max_qty')
            lock_sold_item = request.form.get('lock_sold_item')
            lock_request_name = request.form.get('lock_request_name')
            include_location_check_val = request.form.get(
                'lock_include_location_check')

            srcape_request_data.lock_filter(
                lock_location=lock_location, lock_include_location=lock_included_location, lock_condition=lock_condition, lock_buying_format=lock_buy_format, lock_min_price=lock_min_price, lock_max_price=lock_max_price, lock_min_qty=lock_min_qty, lock_max_qty=lock_max_qty, lock_sold_item=lock_sold_item, lock_request_name=lock_request_name, include_location_check_val=include_location_check_val)
            return 'OK'
    except Exception as error:
        return error


@login_required
def get_lock_filter_data():
    try:
        lock_filter_data = srcape_request_data.get_filter_data()
        return jsonify(lock_filter_data)
    except Exception as error:
        return error
