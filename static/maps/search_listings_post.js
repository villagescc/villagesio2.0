

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
    initMap();
});

var map;

function initMap() {
    var pos = {lat: 21.289373, lng: -157.917480};
    map = new google.maps.Map(document.getElementById('map'), {
        center: pos,
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP
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
        min_price: priceSlider.slider('getValue')[0],
        max_price: priceSlider.slider('getValue')[1],
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
                    seller_username: element['seller_username'],
                    listing_id: element['listing_id'],
                    listing_img: element['listing_img'],
                    profile_img: element['profile_img'],
                    price: element['price'],
                    title: element['title']
                };
                locations.push(latlong);
            });

            // Add wifi points on map
            // for (var i = 0, len = locations.length; i < len; i++) {
            //     (function() {
            //         var markerData = locations[i];
            //         var marker - new google.maps.Marker({})
            //     }
            // }

            var markers_array = [];
            var markers = locations.map(function(location) {
                var marker_content = new google.maps.Marker({
                    position: {lat: location['lat'], lng: location['lng']},
                    map: map,
                    title: 'See details'
                });
                markers_array.push(marker);

                marker_content.seller = location['seller'];
                marker_content.seller_username = location['seller_username'];
                marker_content.price = location['price'];
                marker_content.title = location['title'];
                marker_content.listing_img = location['listing_img'];
                marker_content.profile_img = location['profile_img'];
                marker_content.listing_id = location['listing_id'];
                return marker_content
            });

            // var mcOptions = {
            //     infoOnClick: true,
            //     infoOnClickZoom: 7,
            //     imagePath: '../static/maps/MarkerClusterer/images/m'
            // };
            //
            // // Create wifi groups
            // var markerCluster = new MarkerClusterer(map, markers, mcOptions,
            //     {imagePath: ''});

            var oms = new OverlappingMarkerSpiderfier(map, {
                markersWontMove: true,
                markersWontHide: true,
                basicFormatEvents: true
            });

            // Add function get_wifi_details in each wifi marker in map
            $.each(markers, function (index, element) {

                var infowindow = new google.maps.InfoWindow({
                    maxWidth: 400,
                    content: " "
                });

                var item_content =
                         '<div style="overflow-x: hidden; overflow-y: hidden; position: relative; padding-right: 6px; padding-left: 6px; top: 1px; width: 0; opacity: 0.5"></div>'
                        + '<img src="https://maps.gstatic.com/intl/en_us/mapfiles/iw_close.gif" style="position: absolute; width: 12px; height: 12px; border: 0px; z-index: 101; cursor: pointer; right: 3px; top: 3px; display: none;">'
                        + '<div style="overflow-y: hidden; overflow-x: hidden; cursor: default; clear: both; position: relative; border-radius: 5px; border-width: 1px; padding: 0px; background-color: rgb(255, 255, 255); border-color: rgb(204, 204, 204); border-style: solid; width: 237px; height: 213px;">'
                        + '<div>'
                        + '<div id="map_bubble"><div class="bubble-navi-container">'
                        + '<div class="bubble-navi-container">'
                        + '<div class="bubble-navi"><a>'
                        + '<i class="ss-navigateleft bubble-navi-left disabled"></i></a>'
                        + '<div class="bubble-navi-header">'
                        + '</div>'
                        + '<a><i class="ss-navigateright bubble-navi-right"></i></a></div>'
                        + '<div class="bubble-multi-content" style="width: 100px; left: 0px;">'
                        + '<div class="bubble-item">'
                        + '<div class="bubble-image-container">'
                        + '<a href="/listing_details/'+ this.listing_id + '"><img alt="For sale: '+ this.title +'"src="'+this.listing_img+'"></a></div>'
                        + '<a class="bubble-overlay" href="/listing_details/'+ this.listing_id + '"><span class="bubble-title-link">' + this.title + '</span></a>'
                        + '<div class="bubble-title">'
                        + '<div class="bubble-avatar">'
                        + '<a href="http://villages.io/profiles/' + this.seller_username +'"><img src="'+this.profile_img+'" alt="Image"></a></div>'
                        + '<div class="bubble-details">'
                        + '<div class="bubble-author">'
                        + '<a title="'+this.seller_username+'" href="http://villages.io/profiles/'+this.seller_username+'">'+this.seller+'</a></div>'
                        + '<div class="bubble-price" title="'+this.price+'">'+ this.price + '<span class="bubble-price-quantity"></span>'
                        + '</div></div></div></div>'
                        + '<div class="bubble-item">'
                        + '<div class="bubble-image-container">'
                        + '<a href="/listing_details/'+this.listing_id+'"><img alt="For Sale: '+ this.title + 'src="'+ this.listing_img + '"></a></div>'
                        + '<a class="bubble-overlay" href="/listing_details/'+this.listing_id+'">'
                        + '<span class="bubble-title-link">' + this.title + '</span></a>'
                        + '<div class="bubble-title">'
                        + '<div class="bubble-avatar">'
                        + '<a href="http://villages.io/profiles/' + this.seller_username +'"><img src="'+this.profile_img+'" alt="Image"></a></div>'
                        + '<div class="bubble-details">'
                        + '<div class="bubble-author"><a title="'+this.seller+'" href="http://villages.io/profiles/' + this.seller_username +'">'+this.seller+'</a></div>'
                        + '<div class="bubble-price" title="'+this.title+'">'+this.title+'<span class="bubble-price-quantity"></span></div>'
                        + '</div></div></div></div></div>'
                        + '</div></div></div>'
                        + '<div style="position: relative; margin-top: -1px;">'
                        + '<div style="position: absolute; left: 30%; height: 0; width: 0; margin-left: -15px; border-width: 15px 15px 0; border-color: rgb(204, 204, 204) transparent transparent; border-style: solid;"></div><div style="position: absolute; left: 30%; height: 0px; width: 0px; border-top: 14px solid rgb(255, 255, 255); border-left: 14px solid transparent; border-right: 14px solid transparent; margin-left: -14px; border-bottom-color: transparent; border-bottom-style: solid;">'
                        + '</div></div></div></div>';

                // element.addListener('click', function () {
                //     infowindow.setContent(item_content);
                // infowindow.open(map, this);
                // });

                element.addListener('spider_click', function () {
                    infowindow.setContent(item_content);
                infowindow.open(map, this);
                });
                oms.addMarker(element);
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


