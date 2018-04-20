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

function init_trust_modal() {
    $(".trust-modal").click(function (e) {
        $('#spin-modal').fadeIn();
        var profile_username = $(this).attr('data-profile-username');
        $("#profile-username").val(profile_username);
        var url = '/trust_ajax/' + profile_username;
        $.ajax({
            url: url,
            type: 'GET',
            cache: false,
            success: function (data) {
                if (data["data"]["stat"] == "error") {
                    $('#error-modal-alert').text(data["data"]["error_message"]);
                    $('#spin-modal').fadeOut();
                    $('#error-modal').modal("show");
                }
                else if (data["data"]["stat"] == "ok") {
                    $('#spin-modal').fadeOut();
                    $('#new-trust-heading').text('Trust ' + profile_username);
                    $("#new-trust-modal").modal("show");
                }
                else if (data["data"]["stat"] == "existing") {
                    $('#id_weight').val(data['data']['weight']);
                    $('#id_text').val(data['data']['text']);
                    debugger;
                    if (data["data"]["refer"]) {
                        $("#id_referral").prop('checked', true)
                    }
                    $('#spin-modal').fadeOut();
                    $('.trust-modal-title').text('Trust ' + profile_username);
                    $("#new-trust-modal").modal("show");
                }
            },
            error: function (data) {
                $('#spin-modal').fadeOut();
                showInternalServerError();
            }
        });
    });
}

function init_payment_modal() {
//     $(".payment-modal").click(function (e) {
//         $('#payment-error-modal-alert').html("<strong>Hold on,</strong> We are discovering trust pathways");
//         $('#payment-loading-modal').modal("show");
//         $('#spin-modal').fadeIn();
//         var profile_username = $(this).attr('data-profile-username');
//         $("#profile-username").val(profile_username);
//         var url = '/acknowledge_ajax/' + profile_username;
//         $.ajax({
//             url: url,
//             type: 'GET',
//             cache: false,
//             success: function (data) {
//                 if (data["data"]["stat"] != "ok") {
//                     $('#payment-error-modal-alert').text(data["data"]["stat"]);
//                     $('#spin-modal').fadeOut();
//                 }
//                 else if (!data['data']['can_ripple']) {
//                     $('label[for="id_ripple_0"]').closest('li').hide();
//                     $('#id_ripple_1').attr('checked', true);
//                     $('.ripple-hours').html("There are no available paths through the trust network to <strong>" + data['data']['recipient'] + "</strong>, so you can only send direct acknowledgement.")
//                     $('#spin-modal').fadeOut();
//                     $('#payment-loading-modal').modal("hide");
//                     $("#new-payment-modal").modal("show");
//                 } else if (data["data"]["can_ripple"]) {
//                     $('#id_ripple_0').attr('checked', true);
//                     $('.ripple-hours').html("You can send a trusted acknowledgement of up to " + data['data']['max_amount'] + " hour(s) or a direct acknowledgement of any amount.")
//                     $('#spin-modal').fadeOut();
//                     $('#payment-loading-modal').modal("hide");
//                     $("#new-payment-modal").modal("show");
//                 }
//             },
//
//             error: function (data) {
//                 debugger;
//                 $('#spin-modal').fadeOut();
//                 showInternalServerError();
//             }
//         });
//         e.preventDefault();
//     });
}

function init_contact_modal() {
    $(".contact-modal").click(function (e) {
        $('#spin-modal').fadeIn();
        var profile_username = $(this).attr('data-profile-username');
        var listing_title = $(this).attr('data-listing-title');
        $("#profile-username").val(profile_username);
        $("#listing-title").val(listing_title);
        $('#contact-modal-title').text('Contact ' + profile_username);
        $('#spin-modal').fadeOut();
        $("#new-contact-modal").modal("show");
    });

    $('.menu-group div').click(function () {
        var menu = $(this).parent().find('ul');
        menu.slideToggle();
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

function init_edit_post() {

    $('.my-profile').on('click', '.edit-post-button', function (e) {
    //     var postId = $(this).parents('.post-box').find('.post-cover').data().listingId;
    //     var url = '/get_listing_info/' + postId;
    //     var listing_picture_path = '/uploads/';
    //     var postModal = $('#add-posting-modal').find('.modal-content');
    //     // new Modal header
    //     $('#new-post-heading').text('Edit Post');
    //     $.ajax({
    //         url: url,
    //         type: 'GET',
    //         cache: false,
    //         success: function (data) {
    //             if (data["data"]["stat"] == "ok") {
    //                 postModal.find('#id_listing_type option')
    //                     .filter('option[value=' + data.data.listing_type + ']')
    //                     .attr('selected', true);
    //
    //                 postModal.find('#id_categories option')
    //                     .filter('option[value=' + data.data.listing_type + ']')
    //                     .attr('selected', true);
    //
    //                 postModal.find('#id_title')
    //                     .val(data.data.listing_title);
    //
    //                 postModal.find('#id_description')
    //                     .val(data.data.description);
    //             }
    //         },
    //         error: function (data) {
    //             $('#spin-modal').fadeOut();
    //             showInternalServerError();
    //         }
    //     });
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
        } else{
            $('.notification-dropdown-items').hide();
            $('.dropdown-no-items').show();
        }

    });
}


function init_modals() {
    $(document).on('click','.trust-button, .pay-button, .contact-button, .delete-post-button', function (e) {
        e.preventDefault();
        var url = $(this).attr('href');

        $.ajax({
            url: url,
            dataType: 'html',
            method: 'GET',

            success: function (data, status, xhr) {
                var modal = $('#base-modal'), html = $(data),
                    form = html.find('form');

                // disable recipient input
                form.find('input[name=contact_recipient_name]').attr('readonly', true);
                form.find('input[name=recipient_name]').attr('readonly', true);
                form.find('input[name=name]').attr('readonly', true);

                // fill modal window with content
                modal.find('.modal-body').html(form);

                init_modal_form(form, modal, url);
                modal.modal({
					'keyboard': false,
					'show': true
				});
            },
        });
    });
}


function init_modal_form(form, modal, url) {
    form.ajaxForm({
        url: url,
        dataType: 'html',

        'success': function(data, status, xhr) {
            var html = $(data), success_status = html.find('.messages'),
                newform = html.find('form');
            if (success_status.length > 0) {
                // close modal
                modal.modal('hide');
            } else {
                // initialize new form fields with errors
                modal.find('.modal-body').html(newform);
                init_modal_form(newform, modal, url);
            }
        }
    });
}


// function initModals () {
//     init_listing_modal();
//     init_contact_modal();
//     init_payment_modal();
//     init_trust_modal();
// }

$(document).ready(function () {
    init_feed_filter_form();
    init_instruction_input();
    init_feed_items();
    init_edit_post();
    init_notification_dropdown();
    init_listing_modal();
    init_modals();
});