
$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
    initMap();
});

var map;

function initMap() {
    var pos = {lat: 21.289373, lng: -157.917480};
    map = new google.maps.Map(document.getElementById('map'), {
        center: pos,
        zoom: 12
    });
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            pos = {lat: position.coords.latitude, lng: position.coords.longitude};
            map.setCenter(pos);
            map.setZoom(15);
            call_area_map();
            add_listener_map();
        }, function() {
            showErrorMessage('Error: The Geolocation service failed.');
            add_listener_map();
        });
    } else {
        // Browser doesn't support Geolocation
        showWarningMessage('Error: Your browser doesn\'t support geolocation.');
        add_listener_map();
    }

}

function call_area_map() {
    var value = $('#input_search').val();
    var area_map = {
        lat_min: map.getBounds().getSouthWest().lat(),
        lat_max: map.getBounds().getNorthEast().lat(),
        lng_min: map.getBounds().getSouthWest().lng(),
        lng_max: map.getBounds().getNorthEast().lng(),
        query: value
    };
    get_wifi_data(area_map)
}

function add_listener_map() {
    map.addListener('dragend', call_area_map);
    map.addListener('zoom_changed',  function () {
        delay(call_area_map, 500 );
    });
}

$('#search_wifi').on('click keypress', function (e) {
    e.preventDefault();
    call_area_map()
});

function get_wifi_data(area_map) {
    $.ajax({
        url: '/search/',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(area_map),
        method: 'POST',
        success: function (data) {
            var locations = [];
            $.each(data['listing_locations'], function (index, element) {
                var latlong = {
                    lat: parseFloat(element['lat']),
                    lng: parseFloat(element['lng']),
                    seller: element['seller'],
                    price: element['price'],
                    title: element['title']
                };
                locations.push(latlong);
            });

            // Add wifi points on map
            var markers = locations.map(function(location) {
                var marker_content = new google.maps.Marker({
                    position: {lat: location['lat'], lng: location['lng']},
                    map: map,
                    title: 'See details'

                });
                marker_content.seller = location['seller'];
                marker_content.price = location['price'];
                marker_content.title = location['title'];
                return marker_content
            });

            // Create wifi groups
            var markerCluster = new MarkerClusterer(map, markers,
                {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});

            // Add function get_wifi_details in each wifi marker in map
            $.each(markers, function (index, element) {

                var marker_content = {
                    seller: element['seller'],
                    price: element['price'],
                    title: element['title']
                };

                var infowindow = new google.maps.InfoWindow({
                    content: " "
                });

                element.addListener('click', function () {
                    infowindow.setContent('<p>Seller: '+this.seller+'</p>' +
                    '<p>Price: '+this.price+'</p>' +
                    '<p>Title: '+this.title+'</p>');
                    // get_wifi_details(element);
                infowindow.open(map, this);
                });
            });
        },
        error: function (e) {
            console.log(e);
        }
    });
}
//
function get_wifi_details(element){
    debugger;
    var content = {
        name: element['seller'],
        address: element['price'],
        ssid: element['title']
    };
    var template = Handlebars.compile($('#wifi_info').html());
    $('#card_block').html(template(content));
}

function get_wifi_password(list) {
    var password_list = [];
    $.each(list, function (index, element) {
        if (element['password']){
            var password_data = {
                password: element['password'],
                created_at: element['created_at']
            };
            password_list.push(password_data);
        }
    });
    return password_list;
}

// Add delay on zoom_changed in map
var delay = (function(){
    var timer = 0;
    return function(callback, ms){
        clearTimeout (timer);
        timer = setTimeout(callback, ms);
    };
})();
