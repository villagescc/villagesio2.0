/**
 * Created by filipe on 26/04/17.
 */
function isMalicious(classificationId) {
    if (5 <= classificationId && classificationId <= 17) {
        return true;
    }
    else if (classificationId === 29) {
        return true;
    }
    return false;
}

function isTrusted(classificationId) {
    return (0 < classificationId < 5) || (18 <= classificationId <= 28)
}

var errorsTimeout = null;
function showFormErrors(errors) {
    var temporaryClass = 'timeout-fadeout';
    Object.keys(errors).forEach(function (key) {
        var message = errors[key];
        if ($.isArray(message)) {
            message = message.join("<br>");
        } else if ($.isPlainObject(message)) {
            var messages = [];
            $.each(message, function(key, value) {
                if (isNaN(parseInt(key))) {
                    messages.push(key + " - " + value);
                } else {
                    // In case the key is a number, we are dealing with an array position.
                    // Let's show the appropriate message.
                    messages.push(key + "° : " + value);
                }
            });
            message = messages.join("<br>");
        }
        var errorElement = $('#error_' + key);
        errorElement.html(message);
        errorElement.fadeIn();
        errorElement.addClass(temporaryClass);
    });
    if (errorsTimeout !== null) {
        clearTimeout(errorsTimeout);
    }
    setTimeout(function () {
        $('.' + temporaryClass).fadeOut(500, function () {
            $('.' + temporaryClass).removeClass(temporaryClass);
        });
    }, 3000);
}

function formToJSON(selector) {
    var formArray = selector.serializeArray();
    var returnArray = {};
    for (var i = 0; i < formArray.length; i++) {
        var value = formArray[i]['value'];
        if (value === 'false') {
            returnArray[formArray[i]['name']] = false;
        } else if (value === 'true') {
            returnArray[formArray[i]['name']] = true;
        } else {
            returnArray[formArray[i]['name']] = value;
        }
    }
    return returnArray;
}

function showInternalServerError() {
    $('#internalServerErrorModal').modal();
}

function callVillages(options) {

    // Starting NProgress
    if (options['beforeSend']) {
        var originalBeforeSend = options['beforeSend'];
        options['beforeSend'] = function() {
            originalBeforeSend();
            NProgress.start();
        }
    } else {
        options['beforeSend'] = function() {
            NProgress.start();
        }
    }

    // Stopping NProgress.
    if (options['complete']) {
        var originalComplete = options['complete'];
        options['complete'] = function() {
            originalComplete();
            NProgress.done();
        }
    } else {
        options['complete'] = function() {
            NProgress.done();
        }
    }

    if (options['error']) {
        var originalError = options['error'];
        options['error'] = function(e) {
            if (e.status === 500) {
                showInternalServerError();
            }
            originalError(e);
        }
    } else {
        options['error'] = function() {
            showInternalServerError();
        }
    }
    return $.ajax(options);
}

function callVillagesCustom(options) {

    // Starting NProgress
    debugger;
    if (options['beforeSend']) {
        var originalBeforeSend = options['beforeSend'];
        options['beforeSend'] = function() {
            originalBeforeSend();
            NProgress.start();
        }
    } else {
        options['beforeSend'] = function() {
            NProgress.start();
        }
    }

    // Stopping NProgress.
    if (options['complete']) {
        var originalComplete = options['complete'];
        options['complete'] = function() {
            originalComplete();
            NProgress.done();
        }
    } else {
        options['complete'] = function() {
            NProgress.done();
        }
    }

    if (options['error']) {
        var originalError = options['error'];
        options['error'] = function(e) {
            if (e.status === 500) {
                showInternalServerError();
            }
            originalError(e);
        }
    } else {
        options['error'] = function() {
            showInternalServerError();
        }
    }
    return $.ajax(options);
}

function showSuccessMessage(message) {
    $('#inner-flex-container').prepend(message);
}

// Sets CSRFToken on every Ajax call.
$(document).ajaxSend(
    function (event, xhr, settings) {
        if (settings.type === 'POST' || settings.type === 'PUT' || settings.type === 'DELETE') {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            console.log(settings.url);
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });