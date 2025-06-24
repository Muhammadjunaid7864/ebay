import concurrent
import re
import ast
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask
import config
from utilities.helper import openDbconnection, add_log
from models.ebay_request_history_model import srcape_request_data
from urllib.error import HTTPError
from globals import socketio


def add_ebay_products_to_db(data, request_id=0):
    try:
        connection, cursor = openDbconnection()
        cursor.execute(
            'SELECT ebay_id from ebay_products where request_id =%s', (request_id,))
        existing_data_for_count = cursor.fetchall()
        cursor.execute(
            'SELECT ebay_id,request_id from ebay_products')
        existing_data = cursor.fetchall()
        existing_data_list = [item[0] for item in existing_data]
        request_id_list = [item[1] for item in existing_data]
        inserting_data = []
        for product in data:
            if product.get("price"):
                price_match = re.search(r'\d+\.\d+', product.get("price"))
                ebay_id = product.get('ebay_id')
                request_id = int(request_id)
                if request_id not in request_id_list:
                    inserting_data.append(
                        (product.get("ebay_id"), product.get("title"), product.get("img_url"), product.get("condition"),
                         (float(price_match.group()) if price_match else 0), product.get("location"), request_id, product.get('details_page_link')))
                else:
                    if ebay_id not in existing_data_list:
                        inserting_data.append(
                            (product.get("ebay_id"), product.get("title"), product.get("img_url"), product.get("condition"),
                             (float(price_match.group()) if price_match else 0), product.get("location"), request_id, product.get('details_page_link')))

        if len(inserting_data) > 0:
            cursor.executemany(f"""INSERT INTO ebay_products (ebay_id,title,img_url,condition,price,location,request_id,details_page_url) 
                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", inserting_data)
            connection.commit()
        cursor.execute(
            'SELECT ebay_id from ebay_products where request_id = %s', (request_id,))
        new_existing_data = cursor.fetchall()
        new_list_count = len(new_existing_data)-len(existing_data_for_count)
        cursor.execute(
            """INSERT INTO count_new_add_product_gap(request_id,count_gap) VALUES(%s,%s) ON CONFLICT (request_id) DO UPDATE SET request_id = EXCLUDED.request_id """, (request_id, new_list_count))
        connection.commit()
        return True
    except Exception as error:
        return add_log("add_ebay_products_to_db", f'/line number: {sys.exc_info()[2].tb_lineno} Exception: \n{str(error)}', type='error')


def parse_ebay_products(paremeters):
    try:
        product = paremeters[0]
        locations = paremeters[1]
        min_quantity = paremeters[2]
        max_quantity = paremeters[3]
        from_socket = paremeters[4]

        location = None
        ebay_id = product.attrib.get('id')
        img_url_element = product.xpath(
            "./div/div[contains(@class, 's-item__image-section')]/div/a/div/img")
        img_url = img_url_element[0].attrib.get(
            'src') if len(img_url_element) > 0 else None

        title_element = product.xpath(
            "./div/div[contains(@class, 's-item__info')]/a/div[contains(@class, 's-item__title')]/span/text()")
        title = title_element[0] if len(title_element) > 0 else None

        condition_element = product.xpath(
            "./div/div[contains(@class, 's-item__info')]/div[contains(@class, 's-item__subtitle')]/span[contains(@class, 'SECONDARY_INFO')]/text()")
        condition = condition_element[0] if len(
            condition_element) > 0 else None

        price_element = product.xpath(
            "./div/div[contains(@class, 's-item__info')]/div[contains(@class, 's-item__details ')]/div/span[contains(@class, 's-item__price')]/text()")
        price = price_element[0] if len(price_element) > 0 else None

        details_page_link_element = product.xpath(
            "./div/div[contains(@class, 's-item__info')]/a")
        details_page_link = details_page_link_element[0].attrib.get('href') if len(
            details_page_link_element) > 0 else None
        get_request_details = requests.get(
            f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={details_page_link}")
        soup_details = BeautifulSoup(get_request_details.text, 'html.parser')
        avaible_quantity = soup_details.find(
            'div', {'class', 'd-quantity__availability'})
        buy_it_now = soup_details.find(
            'span', {'class', 'ux-call-to-action__text'})

        if buy_it_now:
            if avaible_quantity:
                avaible_quantity_span = avaible_quantity.find(
                    'span', {'class', 'ux-textspans'})
                avaible_quantity_text = avaible_quantity_span.get_text()

                if avaible_quantity_text:
                    if avaible_quantity_text.lower() == 'last one' or avaible_quantity_text.lower() == 'limited quantity available' or buy_it_now:
                        avaible_quantity_text = '1'
                    else:
                        avaible_quantity_text = avaible_quantity_text
            else:
                avaible_quantity_text = '1'
            quantity = re.findall(r'\d+', avaible_quantity_text)
            quantity = int(quantity[0])
            if min_quantity and max_quantity:
                if quantity >= int(min_quantity) and quantity <= int(max_quantity):
                    resp = comman_code_in_parse_ebay_product(soup_details=soup_details, locations=locations, ebay_id=ebay_id, title=title,
                                                             details_page_link=details_page_link, img_url=img_url, condition=condition, price=price)
                    if from_socket == True:
                        socketio.emit('response_data', resp)
                    else:
                        return resp

            else:
                resp = comman_code_in_parse_ebay_product(soup_details=soup_details, locations=locations, ebay_id=ebay_id, title=title,
                                                         details_page_link=details_page_link, img_url=img_url, condition=condition, price=price)
                if from_socket == True:
                    socketio.emit('response_data', resp)
                else:
                    return resp
        return None
    except Exception as error:
        return add_log("parse_ebay_products", f'/line number: {sys.exc_info()[2].tb_lineno} Exception: \n{str(error)}', type='error')


def comman_code_in_parse_ebay_product(soup_details, locations, ebay_id, title, details_page_link, img_url, condition, price):
    location_page_link = soup_details.find(
        'div', {'class': 'ux-seller-section__item--seller'})
    if location_page_link:
        location_href = location_page_link.find('a')['href']
        get_location_page = requests.get(
            f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={location_href}")
        soup_location = BeautifulSoup(
            get_location_page.text, 'html.parser')
        section = soup_location.find(
            'section', {'class': 'str-about-description__seller-info'})
        if section:
            location = section.find(
                'span', {'class': 'str-text-span BOLD'}).text

            connection, cursor = openDbconnection()
            cursor.execute(
                """INSERT INTO locations(location) VALUES (%s) ON CONFLICT (location) DO UPDATE SET location = EXCLUDED.location""", (location,))
            connection.commit()

    location_check = re.findall(r'\d+', locations[0][0])
    location_check = (location_check[0])

    if int(location_check) == 1:
        input_string = locations[0]
        pattern = r'[^0-9]+'
        new_match_location = []
        for i in input_string:
            match_location = re.findall(pattern, i)
            for j in match_location:
                new_match_location.append(j)
        if not new_match_location:
            return {
                'ebay_id': ebay_id,
                'title': title,
                'details_page_link': details_page_link,
                'img_url': img_url,
                'condition': condition,
                'price': price,
                'location': location,
            }

        else:
            if location in new_match_location:
                return {
                    'ebay_id': ebay_id,
                    'title': title,
                    'details_page_link': details_page_link,
                    'img_url': img_url,
                    'condition': condition,
                    'price': price,
                    'location': location,
                }

    else:
        input_string = locations[0]
        # Match one or more characters that are not digits
        pattern = r'[^0-9]+'
        new_match_location = []
        for i in input_string:
            match_location = re.findall(pattern, i)
            for j in match_location:
                new_match_location.append(j)
        if location not in new_match_location:
            return {
                'ebay_id': ebay_id,
                'title': title,
                'details_page_link': details_page_link,
                'img_url': img_url,
                'condition': condition,
                'price': price,
                'location': location,
            }


def scrape_ebay_request(request_url, locations, min_quantity, max_quantity, request_id=0):
    try:
        if request_url:
            add_log("scrape_ebay_request",
                    f"scraping initiated at {datetime.datetime.utcnow()}")
            app = Flask(__name__)
            with app.app_context():
                srcape_request_data.update_scraping_status(
                    scraping_status="Scraping", created_at=datetime.datetime.now(), request_id=request_id)
            get_request = requests.get(request_url)
            get_request_text = get_request.text
            soup = BeautifulSoup(get_request_text, 'html.parser')
            dom = etree.HTML(str(soup))
            products = dom.xpath(
                "//div[contains(@class, 'srp-river-results')]/ul/li[contains(@class, 's-item')]")

            data = []
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for product in products:
                    futures.append(executor.submit(
                        parse_ebay_products, (product, locations, min_quantity, max_quantity, False)))
                for future in futures:
                    results.append(future.result())

                results = [result for result in results if result and not isinstance(
                    result, Exception)]
            if len(results) > 1:
                add_ebay_products_to_db(results, request_id)
                with app.app_context():
                    srcape_request_data.update_scraping_status(
                        scraping_status="Scraped", created_at=datetime.datetime.now(), request_id=request_id)

            add_log("scrape_ebay_request",
                    f"scraping end at {datetime.datetime.utcnow()}")

        return True
    except Exception as error:
        return add_log("scrape_ebay_request", f'/line number: {sys.exc_info()[2].tb_lineno} Exception: \n{str(error)}', type='error')


def get_url_and_scrape():
    try:
        print(
            f'get_url_and_scrape started at: {datetime.datetime.now()}')
        add_log("get_url_and_scrape",
                f"scraping main initiated at {datetime.datetime.now()}")
        if config.env == "local":
            data = srcape_request_data.get_pending_url()
            for row in data:
                condition_val = row.get('condition_url_val')
                condition_values = condition_val.strip("[]").split(', ')
                if len(condition_values) > 1:
                    condition_url_val = '|'.join(
                        [value.strip("'") for value in condition_values])
                    condition_url_val = condition_url_val.strip("'")
                    url = f"https://www.ebay.com/sch/i.html?_nkw={row.get('request_name')}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={row.get('location_url_val')}&{row.get('buy_format_url_val')}&rt=nc&_udlo={row.get('min_price')}&_udhi={row.get('max_price')}&LH_ItemCondition={condition_url_val}&{row.get('sold_item')}&rt=nc"
                elif condition_val:
                    condition_url_val = '|'.join(
                        [value.strip("'") for value in condition_values])
                    condition_url_val = condition_url_val.strip("'")
                    url = f"https://www.ebay.com/sch/i.html?_nkw={row.get('request_name')}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={row.get('location_url_val')}&{row.get('buy_format_url_val')}&rt=nc&_udlo={row.get('min_price')}&_udhi={row.get('max_price')}&LH_ItemCondition={condition_url_val}&{row.get('sold_item')}&rt=nc"
                else:
                    url = f"https://www.ebay.com/sch/i.html?_nkw={row.get('request_name')}&_sacat=&_ipg=60rt=nc&LH_PrefLoc={row.get('location_url_val')}&{row.get('buy_format_url_val')}&rt=nc&_udlo={row.get('min_price')}&_udhi={row.get('max_price')}&{row.get('sold_item')}&rt=nc"
                url = f"http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url={url}"
                urls = []
                urls.append(url)
                include_location = row.get('include_exclude_btn')
                include_location = [include_location]
                min_quantity = row.get('min_quantity')
                max_quantity = row.get('max_quantity')
                request_id = row.get('request_id')
                scheduler_time = row.get('scheduler_time')
                scrape_at = row.get('created_at')
                if scheduler_time:
                    scheduler_time = int(scheduler_time)
                    time_gap = datetime.datetime.now()-datetime.timedelta(hours=scheduler_time)
                    if time_gap >= scrape_at:
                        t = threading.Thread(target=scrape_ebay_request,
                                             args=(url, include_location, min_quantity, max_quantity, request_id))
                        t.start()
                        # results = []
                        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        #     futures = []
                        #     for urls in urls:
                        #         futures.append(executor.submit(
                        #             scrape_ebay_request, urls, include_location, min_quantity, max_quantity, request_id))
                        #     for future in futures:
                        #         results.append(future.result())

                        #     results = [result for result in results if result and not isinstance(
                        #         result, Exception)]
    except Exception as e:
        return add_log("get_url_and_scrape", f'/line number: {sys.exc_info()[2].tb_lineno} Exception: \n{str(e)}', type='error')
