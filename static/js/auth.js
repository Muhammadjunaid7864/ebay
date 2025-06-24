$(document).ready(function () {
    console.log('done')
})
$('#btn_create_account').on('click', function () {
    debugger
    if ($('#name').val() == "") {
        $('#error_show_name').text("* Please enter Name")
    }
    else if ($('#username').val() == "") {
        $('#error_show_username').text("* Please enter userame")
    }
    else if ($('#email').val() == "") {
        $('#error_show_email').text("* please enter email")
    }
    else if ($('#password').val() == "") {
        $('#error_show_password').text("* please enter password")
    }
    else if ($('#password_comfirm').val() == "") {
        $('#error_show_comfirm').text("* please enter comfirm password")
    }
    else if ($('#password').val() != $('#password_comfirm').val()) {
        $('#error_show_main').text("* Password and Comfirm passowrd don't match")
    }
    else {
        $.ajax({
            type: "POST",
            url: 'sign_up',
            data: {
                name: $('#name').val(),
                username: $('#username').val(),
                email: $('#email').val(),
                password: $('#password').val()
            },
            success: function (response) {
                if (response.message == "success") {
                    window.location.href = '/login'
                }

                else if (response.message == "fail") {
                    toastr.error("User already Exits");
                }

            },
        })
    }
})

$('#btn_login').on('click', function () {
    $.ajax({
        type: "POST",
        url: 'login',
        data: {
            username: $('#username').val(),
            password: $('#password').val()
        },
        success: function (response) {
            if (response.message == "success") {
                window.location.href = '/'
            }
            else if (response.message == "no") {
                toastr.error("User does not exist ");
            }
            else if (response.message == "fail") {
                toastr.error("Credential does not match ")
            }
        }
    })
})