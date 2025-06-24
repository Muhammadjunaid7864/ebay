var item_sold_val = ""
var include_location_check_val = ""
var condition_text_val = ""
var exclude_location_val = ""
var exclude_location_text_val = ""
var lock_location_data = "";
var lock_include_location = "";
var lock_condition_data = "";
var lock_buying_format_data = "";
var lock_min_price_data = "";
var lock_max_price_data = "";
var lock_min_qty_data = "";
var lock_max_qty_data = "";
var lock_sold_item_data = "";
var lock_request_name_data = "";
var lock_include_location_check_data = "";
var btn_on_off = ""
var productsTable = null;
const socket = io.connect('http://' + document.domain + ':' + location.port);
// Initial data received from the server
socket.on("response", function (data) {
    toastr.success(data);
})
socket.on('response_data', function (data) {
    $("#datatables").show()
    $("#product-table-loading").hide();
    // var productsTable = $('#datatables').DataTable({
    //     'aaData': [],  // Initialize with empty data
    //     // ... your DataTable initialization options
    // });
    // productsTable = $('#datatables').DataTable({
    //     // 'aaData': data,
    //     // aLengthMenu: [
    //     //     [25, 50, 100, 200, -1],
    //     //     [25, 50, 100, 200, "All"]
    //     // ],
    //     // iDisplayLength: 100,
    //     // 'columns': [

    //     //     {
    //     //         data: 'img_url', render: function (data) {
    //     //             return '<img src="' + data + '" width="100" height="100">'
    //     //         }
    //     //     },
    //     //     {
    //     //         data: 'title',
    //     //         data: 'details_page_link', render: function (data, type, row) {
    //     //             return `<a href =${row.details_page_link} target ="_blank" style = "text-decoration: none; color:black"><b>${row.title}</b></a>`
    //     //         }
    //     //     },
    //     //     { data: 'price' },
    //     //     { data: 'condition' },
    //     //     { data: 'location' },
    //     // ],
    //     // "bDestroy": true,
    // })
    // var isDataPresent = productsTable
    //     .rows()
    //     .data()
    //     .toArray()
    //     .some(function (existingRow) {
    //         // Compare each field of the existing row with the new data
    //         return (
    //             existingRow.img_url === data.img_url &&
    //             existingRow.title === data.title &&
    //             existingRow.price === data.price &&
    //             existingRow.condition === data.condition &&
    //             existingRow.location === data.location
    //             // Add more comparisons for other columns if needed
    //         );
    //     });

    // // If the data is not already present, add it to the DataTable
    // if (!isDataPresent) {
    // Create the HTML for the 'img_url' column
    var imgHtml = '<img src="' + data.img_url + '" width="100" height="100">';

    // Create the HTML for the 'title' column
    var titleHtml = `<a href="${data.details_page_link}" target="_blank" style="text-decoration: none; color: black;"><b>${data.title}</b></a>`;

    // Create an array for the new row data
    var newRowData = [
        imgHtml,
        titleHtml,
        data.price,
        data.condition,
        data.location
    ];

    // Add the new row to DataTable
    var productsTable = $('#datatables').DataTable();
    productsTable.row.add(newRowData).draw();
    $('#datatables_info').css('margin-top', '');
    $('#datatables_paginate').css('margin-top', '');
})

$(document).ready(function () {
    var urlParams = new URLSearchParams(window.location.search);
    var requestParam = urlParams.get("request");
    if ($('#item_sold').is(':checked')) {
        item_sold_val = $('#item_sold').val()
    }
    function processdata(data) {
        lock_location_data = data[0]
        lock_include_location = data[1]
        lock_condition_data = data[2]
        lock_buying_format_data = data[3]
        lock_min_price_data = data[4]
        lock_max_price_data = data[5]
        lock_min_qty_data = data[6]
        lock_max_qty_data = data[7]
        lock_sold_item_data = data[8]
        lock_request_name_data = data[9]
        lock_include_location_check_data = data[10]

    }
    $.ajax({
        url: '/get_lock_filter',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            processdata(data)
            if (lock_location_data == '98') {
                $('#location').val('98').trigger('change');

            }
            else {
                $('#location').val('1').trigger('change')

            }
            if (lock_include_location != '' && lock_include_location != "{}") {
                lock_include_location = lock_include_location.substring(1, lock_include_location.length - 1).split(',')

                var lock_include_location_arr = [];
                // Iterate through the parsed array to clean up values and push into the new array
                for (var i = 0; i < lock_include_location.length; i++) {
                    var cleanedValue = lock_include_location[i].replace(/"/g, ''); // Remove double quotes
                    lock_include_location_arr.push(cleanedValue);
                }
                $('#exclude_location').val(lock_include_location_arr).trigger('change')

                // for (var j = 0; i <= lock_include_location_arr.length; j++) {
                // }

            }
            else if (lock_include_location == '{\"United States\"}') {
                lock_include_location = JSON.parse(lock_include_location)[0]
            }
            if (lock_buying_format_data == 'LH_All=1') {
                $('#buy_format').val('LH_All=1').trigger('change');
            }
            else if (lock_buying_format_data == 'LH_Auction=1') {
                $('#buy_format').val('LH_Auction=1').trigger('change');
            }
            else {
                $('#buy_format').val('LH_BIN=1').trigger('change');
            }
            if (lock_condition_data != '' && lock_condition_data != "{}") {

                lock_condition_data = lock_condition_data.substring(1, lock_condition_data.length - 1).split(',')
                var lock_condition_arr = [];
                // Iterate through the parsed array to clean up values and push into the new array
                for (var i = 0; i < lock_condition_data.length; i++) {
                    var cleanedValue = lock_condition_data[i].replace(/"/g, ''); // Remove double quotes
                    lock_condition_arr.push(cleanedValue);
                }
                $('#condition').val(lock_condition_arr).trigger('change')
            }
            if (lock_min_price_data != '') {
                $('#min').val(lock_min_price_data)
            }
            if (lock_max_price_data != '') {
                $('#max').val(lock_max_price_data)
            }
            if (lock_min_qty_data != '') {
                $('#min_quantity').val(lock_min_qty_data)
            }
            if (lock_max_qty_data != '') {
                $('#max_quantity').val(lock_max_qty_data)
            }
            if (lock_sold_item_data == "LH_Sold=1") {
                $('#item_sold').prop('checked', true)
            }
            else {
                $('#item_sold').prop('checked', false)
            }
            if (lock_request_name_data != '') {
                $('#search_input').val(lock_request_name_data)
            }
            if (lock_include_location_check_data == 'on') {
                $('#switchincluded').prop('checked', true)
            }
            else if (lock_include_location_check_data == 'off') {
                $('#switchincluded').prop('checked', false)
            }
            var empty = false;
            $('#search_input').each(function () {
                if ($(this).val().length == 0) {
                    empty = true;
                }
            });

            if (empty) {
                $('#btnNavbarSearch').addClass('disabled');
                $('#btn_submit_search').addClass('disabled')
                $('#btn_update_search').addClass('disabled')
            } else {
                $('#btnNavbarSearch').removeClass('disabled');
                $('#btn_submit_search').removeClass('disabled')
                $('#btn_update_search').removeClass('disabled')
            }
        }
    })
    $('#location,#exclude_location,#condition,#buy_format,#min,#max,#min_quantity,#max_quantity,#item_sold,#search_input,#switchincluded').on('change', function () {
        if ($('#item_sold').is(':checked')) {
            item_sold_val = $('#item_sold').val()
        }
        else {
            item_sold_val = "off"
        }
        if ($('#switchincluded').is(':checked')) {
            include_location_check_val = $('#switchincluded').val()
        }
        else {
            include_location_check_val = "off"
        }
        $.ajax({
            url: 'post_filter_lock',
            type: 'POST',
            data: {
                lock_location: $('#location').val(),
                lock_included_location: $('#exclude_location').select2("val"),
                lock_condition: $('#condition').val(),
                lock_buy_format: $('#buy_format').val(),
                lock_min_price: $('#min').val(),
                lock_max_price: $('#max').val(),
                lock_min_qty: $('#min_quantity').val(),
                lock_max_qty: $('#max_quantity').val(),
                lock_sold_item: item_sold_val,
                lock_request_name: $('#search_input').val(),
                lock_include_location_check: include_location_check_val
            }
        })
    })

    $('#datatables').dataTable({
        "oLanguage": {
            "sEmptyTable": "No Data Found"
        },
        aLengthMenu: [
            [25, 50, 100, 200, -1],
            [25, 50, 100, 200, "All"]
        ],
        iDisplayLength: 100,
    });
    if (requestParam != null) {
        $('#scraped_data').text("Scraped Products")
        $('#btnNavbarSearch').on('click', function () {
            $('#datatables').dataTable({
                ajax: {
                    url: `/get_scraped_data_on_view?request=${requestParam}`,
                    dataSrc: '',
                },
                "oLanguage": {
                    "sEmptyTable": "No Data Found"
                },
                aLengthMenu: [
                    [25, 50, 100, 200, -1],
                    [25, 50, 100, 200, "All"]
                ],
                iDisplayLength: 100,
                "bDestroy": true,
            });
        })

        $('#datatables').dataTable({
            ajax: {
                url: `/get_scraped_data_on_view?request=${requestParam}`,
                dataSrc: '',
            },
            "oLanguage": {
                "sEmptyTable": "No Data Found"
            },
            aLengthMenu: [
                [25, 50, 100, 200, -1],
                [25, 50, 100, 200, "All"]
            ],
            iDisplayLength: 100,
            'columns': [
                {
                    data: 'img_url', render: function (data) {
                        return '<img src="' + data + '" width="100" height="100">'
                    }
                },
                {
                    data: 'title',
                    data: 'details_page_link', render: function (data, type, row) {
                        return `<a href =${row.details_page_link} target ="_blank" style = "text-decoration: none; color:black"><b>${row.title}</b></a>`
                    }
                },
                { data: 'price' },
                { data: 'condition' },
                { data: 'location' },
            ],
            "bDestroy": true,
        });
    }

    $('#search_input').keyup(function () {

        var empty = false;
        $('#search_input').each(function () {
            if ($(this).val().length == 0) {
                empty = true;
            }
        });

        if (empty) {
            $('#btnNavbarSearch').addClass('disabled');
            $('#btn_submit_search').addClass('disabled')
            $('#btn_update_search').addClass('disabled')
        } else {
            $('#btnNavbarSearch').removeClass('disabled');
            $('#btn_submit_search').removeClass('disabled')
            $('#btn_update_search').removeClass('disabled')
        }
    });
    $(".item_location").select2()
    $('.item_buy_format').select2()
    $('.exclude_location').select2()
    $(".item_condition").select2({
        tags: true,
        // tokenSeparators: [',', ' ']
    })
    $(".exclude_location").select2({
        tags: true,
        // tokenSeparators: [',', '\n']
    })

    $(".item_buy_format").select2
    $.ajax({
        type: 'GET',
        url: '/fetch_request_history_according_to_id',
        dataSrc: "",
        data: { request_id: 'request_id' },

    })

    $('#condition_after').val(JSON.parse($('#condtion_val').text().replaceAll('\'', '"'))).trigger('change')
    $('#exclude_location_after').val(JSON.parse($('#included_location_val_id').text().replaceAll('\'', '"'))).trigger('change')

})

$('#btnNavbarSearch').on('click', function () {
    $('.dataTables_info, .dataTables_paginate').css('margin-top', '30rem')
    if ($('#item_sold').is(':checked')) {
        item_sold_val = $('#item_sold').val()
    }
    if ($('#switchincluded').is(':checked')) {
        exclude_location_val = $('#exclude_location').select2('val')
        if (exclude_location_val) {
            console.log('have')
        }
        else {
            exclude_location_val = $('#exclude_location_after').select2('val')
        }
        btn_on_off = "on"

    }
    else {
        exclude_location_val = $('#exclude_location').select2('val')
        if (exclude_location_val) {
            console.log('have')
        }
        else {
            exclude_location_val = $('#exclude_location_after').select2('val')
        }
        btn_on_off = "off"

    }
    $.ajax({
        url: '/',
        type: 'POST',
        data: {
            location: $('#location').val(),
            exclude_location: exclude_location_val,
            condition: $('#condition').val(),
            buy_format: $('#buy_format').val(),
            min: $('#min').val(),
            max: $('#max').val(),
            min_quantity: $('#min_quantity').val(),
            max_quantity: $('#max_quantity').val(),
            item_sold: item_sold_val,
            searchtext: $('#search_input').val(),
            btn_on_off: btn_on_off

        },
        dataType: 'json',
    })
    if (productsTable != null) {
        productsTable.destroy();
    }
    $("#datatables").hide()
    $("#product-table-loading").show()

})

$('#btn_modal_save').on('click', function () {

    if ($('#item_sold').is(':checked')) {
        var item_sold_val = $('#item_sold').val()
    }
    if ($('#switchincluded').is(':checked')) {
        exclude_location_val = $('#exclude_location').select2('val')
        btn_on_off = "on"
    }
    else {
        exclude_location_val = $('#exclude_location').select2('val')
        btn_on_off = "off"
    }
    $.ajax({
        type: 'POST',
        url: '/ebay_scrape_request_history',
        data: {
            location_url_val: $('#location').val(),
            location_text: $('#location :selected').text(),
            exclude_location: $('#exclude_location').select2("data").map((item) => { return item.text }),
            exclude_location_val: exclude_location_val,
            include_location_val: btn_on_off,
            condition_url_val: $('#condition').select2("val"),
            condition_text: $('#condition').select2("data").map((item) => { return item.text }),
            buy_format_url_val: $('#buy_format').val(),
            buy_format: $('#buy_format :selected').text(),
            min: $('#min').val(),
            max: $('#max').val(),
            min_quantity: $('#min_quantity').val(),
            max_quantity: $('#max_quantity').val(),
            item_sold: item_sold_val,
            searchtext: $('#search_input').val(),
            scheduler_time: $('#scheduler_time').val()
        },
        dataType: 'json',
    })
    toastr.success("Data Saved Successfully");
    $('#btn_save_link').attr('href', '/get_request_history')
})
$('#btn_view_search').on('click', function () {
    var condition_url_val = $('#condition').select2("val")
    comman_code_in_view_url(condition_url_val)
})
$('#btn_view_search_after').on('click', function () {
    var condition_url_val = $('#condition_after').select2("val")
    comman_code_in_view_url(condition_url_val)
})
function comman_code_in_view_url(condition_url_val) {
    var item_sold_val = ""
    var location_url_val = $('#location').val()
    var buy_format_url_val = $('#buy_format').val()
    var min = $('#min').val()
    var max = $('#max').val()
    var searchtext = $('#search_input').val()
    if ($('#item_sold').is(':checked')) {
        item_sold_val = $('#item_sold').val()
    }
    condition = []
    if (condition_url_val.length > 1) {

        condition_url_val.forEach(condition_url_val => {
            var condition_url_val = condition_url_val
            condition.push(condition_url_val)
            var item = condition.join('|')
            var new_item = item.replace(/['"]+/g)
            console.log(new_item)
            url = `http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url=https://www.ebay.com/sch/i.html?_nkw=${searchtext}&_sacat=&_ipg=60rt=nc&LH_PrefLoc=${location_url_val}&${buy_format_url_val}&rt=nc&_udlo=${min}&_udhi=${max}&LH_ItemCondition=${new_item}&${item_sold_val}&rt=nc`
        });
    }
    else if (condition_url_val.length == 1) {
        condition_url_val.forEach(condition_url_val => {
            condition.push(condition_url_val)
            var item = condition.join('|')
            var new_item = item.replace(/['"]+/g)
            url = `http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url=https://www.ebay.com/sch/i.html?_nkw=${searchtext}&_sacat=&_ipg=60rt=nc&LH_PrefLoc=${location_url_val}&${buy_format_url_val}&rt=nc&_udlo=${min}&_udhi=${max}&LH_ItemCondition=${new_item}&${item_sold_val}&rt=nc`
        });
    }
    else {
        url = `http://api.scraperapi.com/?country_code=us&api_key=c2f1512745b1ea789c1048dc927484f9&url=https://www.ebay.com/sch/i.html?_nkw=${searchtext}&_sacat=&_ipg=60rt=nc&LH_PrefLoc=${location_url_val}&${buy_format_url_val}&rt=nc&_udlo=${min}&_udhi=${max}&${item_sold_val}&rt=nc`
    }

    $('#view_anchor_tag_after').attr('href', url)

}
$('#btn_update_search').on('click', function () {
    if ($('#item_sold').is(':checked')) {
        var item_sold_val = $('#item_sold').val()
    }
    if ($('#switchincluded').is(':checked')) {
        exclude_location_val = $('#exclude_location_after').select2('val')
        btn_on_off = "on"

    }
    else {
        exclude_location_val = $('#exclude_location_after').select2('val')
        btn_on_off = "off"
    }
    $.ajax({
        type: 'POST',
        url: '/update_request_history_according_to_id',
        data: {
            request_id: $('#hidden_request_id').text(),
            location_url: $('#location').val(),
            location_text: $('#location :selected').text(),
            exclude_location: $('#exclude_location_after').select2("data").map((item) => { return item.text }),
            exclude_location_val: exclude_location_val,
            condition_url_val: $('#condition_after').select2("val"),
            include_location_val: btn_on_off,
            condition_text: $('#condition_after').select2("data").map((item) => { return item.text }),
            buy_format_url_val: $('#buy_format').val(),
            buy_format: $('#buy_format :selected').text(),
            min: $('#min').val(),
            max: $('#max').val(),
            min_quantity: $('#min_quantity').val(),
            max_quantity: $('#max_quantity').val(),
            item_sold: item_sold_val,
            searchtext: $('#search_input').val(),
        },
        dataType: 'json',
    })
    toastr.success("Data Update Successfully");
})

$('#btn_export_data').on('click', function () {
    var urlParams = new URLSearchParams(window.location.search);
    var requestParam = urlParams.get("request");
    var href = $('#export_href').attr('href', `/get_product_csv?request=${requestParam}`)
})
