/* JS functions available on every page. */

function init_instruction_input() {
    /* Allow search boxes to give instructions that disappear when selected. */
    $('.instruction_input').each(function (index) {
        // Input instruction goes in 'help' attribute.
        var orig_text = $(this).attr('help');

        // Only apply help instruction if blank.
        if ($(this).val() == '')
            $(this).val(orig_text);

        $(this).focus(function () {  // Remove instruction on focus.
            if ($(this).val() == orig_text) {
                $(this).val('');
            }
        }).blur(function () {  // Restore on blur if nothing entered.
            if ($(this).val() == '') {
                $(this).val(orig_text);
            }
        });

        // Remove help on form submit.
        input = $(this);  // Inside form submit handler, $(this) = form.
        input.closest('form').submit(function () {
            if (input.val() == orig_text) {
                input.val('');
            }
        });
    });
}

function init_feed_items() {
    /* Make feed item container divs clickable links. */
    $('.feed_item').click(function () {
        window.location = $(this).attr('href');
    }).hover(function () {
        $(this).addClass('hover')
    }, function () {
        $(this).removeClass('hover')
    });
}

$(function () {
    var referral = localStorage.referral === "true";
    $("#id_referral_filter").prop('checked', referral);

    var balance_high = localStorage.balance_high === "true";
    $("#balance-high").prop('checked', balance_high);

    var balance_low = localStorage.balance_low === "true";
    $("#balance-low").prop('checked', balance_low);
});

function init_feed_filter_form() {
    /* Make form submit on change. */
    $('#id_radius').change(function () {
        $(this).closest('form').submit();
    });
    $('#id_trusted').change(function () {
        $(this).closest('form').submit();
    });
    $('#id_referral_filter').change(function () {
        localStorage.referral = $(this).is(':checked');
        $(this).closest('form').submit();
    });
    $('#inputListingType').change(function () {
        $(this).closest('form').submit();
    });
    $('#balance-low').change(function () {
        localStorage.balance_low = $(this).is(':checked');
        $(this).closest('form').submit();
    });
    $('#balance-high').change(function () {
        localStorage.balance_high = $(this).is(':checked');
        $(this).closest('form').submit();
    });
    $('#id_clear').click(function () {
        $('.feed_filter_form #id_q').val('');
        $(this).closest('form').submit();
    });
}

function init_listing_modal() {
    $("#product_list").on('click', '.listing-modal', function (e) {
        $('#spin-modal').fadeIn();
        var listing_id = $(this).attr('data-listing-id');
        var url = '/get_listing_info/' + listing_id;
        var listing_picture_path = '/uploads/';
        $.ajax({
            url: url,
            type: 'GET',
            cache: false,
            success: function (data) {
                if (data["data"]["stat"] == "ok") {
                    $('#listing-id').val(listing_id);
                    $('.listing-modal-title').text(data["data"]["listing_title"]);
                    if (data["data"]["listing_photo"]) {
                        $('.listing-img').attr("src", listing_picture_path + data["data"]["listing_photo"]);
                        $('.listing-img').show();
                    } else {
                        $('.listing-img').hide();
                    }
                    $('#label-listing-type').text(data["data"]["listing_type"]);
                    $('#label-price').text(data["data"]["listing_price"]);
                    $('#label-profile-name').text(data["data"]["profile_name"]);
                    $('#profile-location').text(data["data"]["profile_location"]);
                    $('#listing-created-at').text(data["data"]["created_at"]);
                    $('#listing-created-at').attr("href", "/listing_details/" + listing_id);
                    $('#label-description').text(data["data"]["description"]);
                    $('#listing-profile-username').text(data["data"]["username"]);
                    $("#listing-profile-username").attr("href", "/profiles/" + data["data"]["username"]);
                    $('#label-profile-balance').text(data["data"]["balance"]);
                    $('#label-profile-occupation').text(data["data"]["job"]);
                    $('#trust-btn').attr('data-profile-username', data["data"]["username"]);
                    $('#payment-btn').attr('data-profile-username', data["data"]["username"]);
                    $('#contact-btn').attr('data-profile-username', data["data"]["username"]);
                    $('#spin-modal').fadeOut();
                    $("#listing-modal").modal("show");
                }
            },
            error: function (data) {
                $('#spin-modal').fadeOut();
                showInternalServerError();
            }
        });
    });
}

function init_notification_dropdown() {
    $(".notification-dropdown").click(function () {
        var new_notifications = parseInt($("#new-notifications-count").text());

        if (new_notifications) {
            $.ajax({
                url: "/notifications/new/",
                dataType: 'html',
                method: 'GET',
                success: function (data, status, xhr) {
                    $('.dropdown-no-items').hide();
                    $('.notification-dropdown-items').html(data);
                }
            });
            $('.count').removeClass('full').text(0);
        } else {
            $('.notification-dropdown-items').hide();
            $('.dropdown-no-items').show();
        }

    });
}

function init_auth_modals() {
    $(document).on('click', '.auth-button', function (e) {
        e.preventDefault();
        var $btn = $(this),
            url = $btn.attr('href');

        $.ajax({
            url: url,
            dataType: 'html',
            method: 'GET',

            success: function (data, status, xhr) {
                var modal = $('#base-modal'), html = $(data),
                    form = html.find('form');

                // fill modal window with content
                modal.find('.modal-body').html(form);
                init_auth_modal_form(form, modal, url);

                modal.modal({
                    'keyboard': false,
                    'show': true
                });
            },
        });
    });
}

function init_auth_modal_form(form, modal, url) {
    form.ajaxForm({
        url: url,
        dataType: 'html',

        'success': function (data, status, xhr) {
            // console.log(this.url);

            var html = $(data),
                success_status = html.find('.messages'),
                newform = html.find('form');
            if (success_status.length > 0) {
                if (~success_status.text().indexOf('Welcome')) {
                    location.href = '/home';
                } else {
                    modal.find('.modal-body').html(success_status);
                    setTimeout(function () {
                        modal.modal('hide');
                    }, 4000);
                }

            } else {
                // initialize new form fields with errors
                modal.find('.modal-body').html(newform);
                init_auth_modal_form(newform, modal, url);
            }
        }
    });
}


function init_modals() {
    $(document).on('click', '.trust-button, .pay-button, .contact-button, .delete-post-button', function (e) {
        e.preventDefault();
        var $btn = $(this),
            url = $btn.attr('href');

        $.ajax({
            url: url,
            dataType: 'html',
            method: 'GET',

            success: function (data, status, xhr) {
                var modal = $('#base-modal'), html = $(data),
                    form = html.find('form');

                // fill modal window with content
                modal.find('.modal-body').html(form);
                init_modal_form(form, modal, url);

                // disable recipient input
                if ($btn.hasClass('trust-button')) {
                    modal.find('.form-group:first label').text('Trust receiver');
                    modal.find('#id_recipient_name').hide();
                } else if ($btn.hasClass('pay-button')) {
                    modal.find('.id_recipient .form-group:first label').text('Payment receiver');
                    form.find('input[name=recipient]').attr('readonly', true);
                } else if ($btn.hasClass('contact-button')) {
                    form.find('input[name=contact_recipient_name]').hide();
                }

                modal.modal({
                    'keyboard': false,
                    'show': true
                });
            },
        });
    });
}

function init_modal_form(form, modal, url) {
    // show spinner over the form
    var spinner = $('#spin-modal');

    form.ajaxForm({
        url: url,
        dataType: 'html',
        beforeSend: function () {
            spinner.find('.back-spin').css('z-index', 1051);
            spinner.fadeIn();
        },
        'success': function (data, status, xhr) {
            var html = $(data),
                success_status = html.find('.messages'),
                newform = html.find('form');
            if (success_status.length > 0) {
                // close modal
                modal.modal('hide');
            } else {
                // initialize new form fields with errors
                modal.find('.modal-body').html(newform);
                init_modal_form(newform, modal, url);
            }
        },
        complete: function () {
            spinner.find('.back-spin').css('z-index', 9);
            spinner.fadeOut();
        }
    });
}


$(document).ready(function () {
    init_feed_filter_form();
    init_instruction_input();
    init_feed_items();
    init_notification_dropdown();
    init_listing_modal();
    init_modals();
    init_auth_modals();
});