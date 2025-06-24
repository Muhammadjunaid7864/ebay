var index = 0
var order = "asc"
var count_name = 0
var count_location = 0
var count_included = 0
var count_condition = 0
var count_buy_format = 0
var count_min_price = 0
var count_max_price = 0
var count_sold_item = 0
var count_scraped_at = 0
var count_status = 0
var count_scraped_records = 0
$(document).ready(function () {
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
    get_ebay_request_query_history()
    $('#datatables thead').on('click', '#name', function () {
        count_name++
        if (count_name % 2 == 0) {
            order = 'desc'
        }
        else if (count_name % 2 == 1) {
            order = 'asc'
        }
        index = 1
    });
    $('#datatables thead').on('click', '#location', function () {
        count_location++
        if (count_location % 2 == 0) {
            order = "desc"
        }
        else if (count_location % 2 == 1) {
            order = "asc"
        }
        index = 2
    });
    $('#datatables thead').on('click', '#included', function () {
        count_included++
        if (count_included % 2 == 0) {
            order = "desc"
        }
        else if (count_included % 2 == 1) {
            order = "asc"
        }
        index = 3
    });
    $('#datatables thead').on('click', '#condition', function () {
        count_condition++
        if (count_condition % 2 == 0) {
            order = "desc"
        }
        else if (count_condition % 2 == 1) {
            order = "asc"
        }
        index = 4
    });
    $('#datatables thead').on('click', '#buy_format', function () {
        count_buy_format++
        if (count_buy_format % 2 == 0) {
            order = "desc"
        }
        else if (count_buy_format % 2 == 1) {
            order = "asc"
        }
        index = 5
    });
    $('#datatables thead').on('click', '#min_price', function () {
        count_min_price++
        if (count_min_price % 2 == 0) {
            order = "desc"
        }
        else if (count_min_price % 2 == 1) {
            order = "asc"
        }
        index = 6
    });
    $('#datatables thead').on('click', '#max_price', function () {
        count_max_price++
        if (count_max_price % 2 == 0) {
            order = "desc"
        }
        else if (count_max_price % 2 == 1) {
            order = "asc"
        }
        index = 7
    });
    $('#datatables thead').on('click', '#sold_item', function () {
        count_sold_item++
        if (count_sold_item % 2 == 0) {
            order = "desc"
        }
        else if (count_sold_item % 2 == 1) {
            order = "asc"
        }
        index = 8
    });
    $('#datatables thead').on('click', '#scraped_record', function () {
        count_scraped_records++
        if (count_scraped_records % 2 == 0) {
            order = "desc"
        }
        else if (count_scraped_records % 2 == 1) {
            order = "asc"
        }
        index = 9
    });
    $('#datatables thead').on('click', '#scraped_at', function () {
        count_scraped_at++
        if (count_scraped_at % 2 == 0) {
            order = "desc"
        }
        else if (count_scraped_at % 2 == 1) {
            order = "asc"
        }
        index = 10
    });
    $('#datatables thead').on('click', '#status', function () {
        count_status++
        if (count_status % 2 == 0) {
            order = "desc"
        }
        else if (count_status % 2 == 1) {
            order = "asc"
        }
        index = 11
    });

})
function get_ebay_request_query_history() {
    if (index != 0) {
        console.log(index)
        $('#datatables').DataTable({
            ajax: {
                url: '/get_ebay_request_query_history',
                dataSrc: '',
            },
            aLengthMenu: [
                [25, 50, 100, 200, -1],
                [25, 50, 100, 200, "All"]
            ],
            order: [[index - 1, order]],
            iDisplayLength: 100,
            columns: [
                { data: 'name' },
                { data: 'location' },
                { data: 'excludedLocations' },
                { data: 'conditions' },
                { data: 'buyFormat' },
                { data: 'minPrice' },
                { data: 'maxPrice' },
                { data: 'soldItem' },
                { data: 'match_count' },
                { data: 'scheduler_time' },
                { data: 'scraped_at' },
                { data: 'status' },
                { data: 'count_gap' },
                {
                    render: function (data, type, row) {
                        return '<button class ="btn btn-default" type="button" id="' + row.id + '" onclick="editfun()"><a href="/?request=' + row.id + '"><i class="fa fa-eye"></a></i></button><button class ="btn btn-default del_btn ms-1" type="button" data-id="' + row.id + '"><i class="fa fa-trash"></i></button>'
                    },
                    orderable: false
                },
            ],
            "bDestroy": true,
        });
    }
    else {
        $('#datatables').DataTable({
            ajax: {
                url: '/get_ebay_request_query_history',
                dataSrc: '',
            },
            aLengthMenu: [
                [25, 50, 100, 200, -1],
                [25, 50, 100, 200, "All"]
            ],
            iDisplayLength: 100,
            columns: [
                { data: 'name' },
                { data: 'location' },
                { data: 'excludedLocations' },
                { data: 'conditions' },
                { data: 'buyFormat' },
                { data: 'minPrice' },
                { data: 'maxPrice' },
                { data: 'soldItem' },
                { data: 'match_count' },
                { data: 'scheduler_time' },
                { data: 'scraped_at' },
                { data: 'status' },
                { data: 'count_gap' },
                {
                    render: function (data, type, row) {
                        return '<button class ="btn btn-default" type="button" id="' + row.id + '" onclick="editfun()"><a href="/?request=' + row.id + '"><i class="fa fa-eye"></a></i></button><button class ="btn btn-default del_btn ms-1" type="button" data-id="' + row.id + '"><i class="fa fa-trash"></i></button>'
                    },
                    orderable: false
                },
            ],
            "bDestroy": true,
        });
    }
}
$('#datatables').on('click', '.del_btn', function () {
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: 'btn btn-success',
            cancelButton: 'btn btn-danger'
        },
        buttonsStyling: false
    })

    swalWithBootstrapButtons.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel!',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            id = $(this).data('id');
            $.ajax({
                type: 'POST',
                url: '/delete_request_history_according_to_id',
                data: { request_id: id },
                success: function () {
                    get_ebay_request_query_history()
                    toastr.success("Data Deleted Successfully");
                }
            })
            swalWithBootstrapButtons.fire(
                'Deleted!',
                'Your Data has been deleted.',
                'success'
            )
        } else if (
            /* Read more about handling dismissals below */
            result.dismiss === Swal.DismissReason.cancel
        ) {
            swalWithBootstrapButtons.fire(
                'Cancelled',
                'Your imaginary Data is safe :)',
                'error'
            )
        }
    })

});
function editfun() {
    $.ajax({
        type: 'POST',
        url: '/fetch_request_history_according_to_id',
    })
}

