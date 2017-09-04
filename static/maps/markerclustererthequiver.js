function MarkerClusterer(e, t, r, s, o, i, n) {
    this.extend(MarkerClusterer, google.maps.OverlayView), this.map_ = e, this.markers_ = [], this.markerContents_ = [], this.showingMarker_ = o, this.locale = i || "en", this.infowindow_ = s, this.clusters_ = [], this.sizes = [53, 56, 66, 78, 90], this.styles_ = [], this.ready_ = !1;
    var a = n || {};
    this.gridSize_ = a.gridSize || 60, this.minClusterSize_ = a.minimumClusterSize || 2, this.maxZoom_ = a.maxZoom || null, this.styles_ = a.styles || [], this.imagePath_ = a.imagePath || this.MARKER_CLUSTER_IMAGE_PATH_, this.imageExtension_ = a.imageExtension || this.MARKER_CLUSTER_IMAGE_EXTENSION_, this.zoomOnClick_ = !0, a.zoomOnClick != undefined && (this.zoomOnClick_ = a.zoomOnClick), this.averageCenter_ = !1, a.averageCenter != undefined && (this.averageCenter_ = a.averageCenter), this.setupStyles_(), this.setMap(e), this.prevZoom_ = this.map_.getZoom();
    var u = this;
    google.maps.event.addListener(this.map_, "zoom_changed", function() {
        var e = u.map_.mapTypes[u.map_.getMapTypeId()].maxZoom,
            t = u.map_.getZoom();
        t < 0 || t > e || u.prevZoom_ != t && (u.prevZoom_ = u.map_.getZoom(), u.resetViewport())
    }), google.maps.event.addListener(this.map_, "idle", function() {
        u.redraw()
    }), t && t.length && this.addMarkers(t, r, !1)
}

function Cluster(e) {
    this.markerClusterer_ = e, this.map_ = e.getMap(), this.gridSize_ = e.getGridSize(), this.minClusterSize_ = e.getMinClusterSize(), this.averageCenter_ = e.isAverageCenter(), this.center_ = null, this.markers_ = [], this.markerIndex_ = [], this.bounds_ = null, this.clusterIcon_ = new ClusterIcon(this, e.getStyles(), e.getGridSize())
}

function ClusterIcon(e, t, r) {
    e.getMarkerClusterer().extend(ClusterIcon, google.maps.OverlayView), this.styles_ = t, this.padding_ = r || 0, this.cluster_ = e, this.center_ = null, this.map_ = e.getMap(), this.div_ = null, this.sums_ = null, this.visible_ = !1, this.showingInfo_ = !1, this.setMap(this.map_);
    var s = this;
    google.maps.event.addListener(this.map_, "mousedown", function() {
        s.showingInfo_ && (s.cluster_.markerClusterer_.infowindow_.close(), s.cluster_.markerClusterer_.showingMarker_ = "", s.showingInfo_ = !1)
    })
}
MarkerClusterer.prototype.MARKER_CLUSTER_IMAGE_PATH_ = "/static/maps/m1-5118720be739d6eaaa6c5e9dfce3c6ba3f15838ba5aa5dfec6687bc24bc4413e.png".replace(/\.png$/, ""), MarkerClusterer.prototype.MARKER_CLUSTER_IMAGE_EXTENSION_ = "png", MarkerClusterer.prototype.extend = function(e, t) {
    return function(e) {
        for (var t in e.prototype) this.prototype[t] = e.prototype[t];
        return this
    }.apply(e, [t])
}, MarkerClusterer.prototype.onAdd = function() {
    this.setReady_(!0)
}, MarkerClusterer.prototype.draw = function() {}, MarkerClusterer.prototype.setupStyles_ = function() {
    if (!this.styles_.length)
        for (var e = 0; this.sizes[e]; e++) this.styles_.push({
            url: this.imagePath_ + "." + this.imageExtension_,
            width: 53,
            height: 52
        })
}, MarkerClusterer.prototype.fitMapToMarkers = function() {
    for (var e, t = this.getMarkers(), r = new google.maps.LatLngBounds, s = 0; e = t[s]; s++) r.extend(e.getPosition());
    this.map_.fitBounds(r)
}, MarkerClusterer.prototype.setStyles = function(e) {
    this.styles_ = e
}, MarkerClusterer.prototype.getStyles = function() {
    return this.styles_
}, MarkerClusterer.prototype.isZoomOnClick = function() {
    return this.zoomOnClick_
}, MarkerClusterer.prototype.isAverageCenter = function() {
    return this.averageCenter_
}, MarkerClusterer.prototype.getMarkers = function() {
    return this.markers_
}, MarkerClusterer.prototype.getTotalMarkers = function() {
    return this.markers_.length
}, MarkerClusterer.prototype.setMaxZoom = function(e) {
    this.maxZoom_ = e
}, MarkerClusterer.prototype.getMaxZoom = function() {
    return this.maxZoom_ || this.map_.mapTypes[this.map_.getMapTypeId()].maxZoom
}, MarkerClusterer.prototype.calculator_ = function(e, t) {
    for (var r = 0, s = e.length, o = s; 0 !== o;) o = parseInt(o / 10, 10), r++;
    return r = Math.min(r, t), {
        text: s,
        index: r
    }
}, MarkerClusterer.prototype.setCalculator = function(e) {
    this.calculator_ = e
}, MarkerClusterer.prototype.getCalculator = function() {
    return this.calculator_
}, MarkerClusterer.prototype.addMarkers = function(e, t, r) {
    for (var s, o = 0; s = e[o]; o++) this.pushMarkerTo_(s, t[o]);
    r || this.redraw()
}, MarkerClusterer.prototype.pushMarkerTo_ = function(e, t) {
    if (e.isAdded = !1, e.draggable) {
        var r = this;
        google.maps.event.addListener(e, "dragend", function() {
            e.isAdded = !1, r.repaint()
        })
    }
    this.markers_.push(e), this.markerContents_.push(t)
}, MarkerClusterer.prototype.addMarker = function(e, t) {
    this.pushMarkerTo_(e), t || this.redraw()
}, MarkerClusterer.prototype.removeMarker_ = function(e) {
    var t = -1;
    if (this.markers_.indexOf) t = this.markers_.indexOf(e);
    else
        for (var r, s = 0; r = this.markers_[s]; s++)
            if (r == e) {
                t = s;
                break
            } return -1 != t && (this.markers_.splice(t, 1), this.markerContents_.splice(t, 1), !0)
}, MarkerClusterer.prototype.removeMarker = function(e, t) {
    var r = this.removeMarker_(e);
    return !(t || !r) && (this.resetViewport(), this.redraw(), !0)
}, MarkerClusterer.prototype.removeMarkers = function(e, t) {
    for (var r, s = !1, o = 0; r = e[o]; o++) {
        var i = this.removeMarker_(r);
        s = s || i
    }
    if (!t && s) return this.resetViewport(), this.redraw(), !0
}, MarkerClusterer.prototype.setReady_ = function(e) {
    this.ready_ || (this.ready_ = e, this.createClusters_())
}, MarkerClusterer.prototype.getTotalClusters = function() {
    return this.clusters_.length
}, MarkerClusterer.prototype.getMap = function() {
    return this.map_
}, MarkerClusterer.prototype.setMap = function(e) {
    this.map_ = e
}, MarkerClusterer.prototype.getGridSize = function() {
    return this.gridSize_
}, MarkerClusterer.prototype.setGridSize = function(e) {
    this.gridSize_ = e
}, MarkerClusterer.prototype.getMinClusterSize = function() {
    return this.minClusterSize_
}, MarkerClusterer.prototype.setMinClusterSize = function(e) {
    this.minClusterSize_ = e
}, MarkerClusterer.prototype.getExtendedBounds = function(e) {
    var t = this.getProjection(),
        r = new google.maps.LatLng(e.getNorthEast().lat(), e.getNorthEast().lng()),
        s = new google.maps.LatLng(e.getSouthWest().lat(), e.getSouthWest().lng()),
        o = t.fromLatLngToDivPixel(r);
    o.x += this.gridSize_, o.y -= this.gridSize_;
    var i = t.fromLatLngToDivPixel(s);
    i.x -= this.gridSize_, i.y += this.gridSize_;
    var n = t.fromDivPixelToLatLng(o),
        a = t.fromDivPixelToLatLng(i);
    return e.extend(n), e.extend(a), e
}, MarkerClusterer.prototype.isMarkerInBounds_ = function(e, t) {
    return t.contains(e.getPosition())
}, MarkerClusterer.prototype.clearMarkers = function() {
    this.resetViewport(!0), this.markers_ = [], this.markerContents_ = []
}, MarkerClusterer.prototype.resetViewport = function(e) {
    for (var t, r = 0; t = this.clusters_[r]; r++) t.remove();
    for (var s, r = 0; s = this.markers_[r]; r++) s.isAdded = !1, e && s.setMap(null);
    this.clusters_ = []
}, MarkerClusterer.prototype.repaint = function() {
    var e = this.clusters_.slice();
    this.clusters_.length = 0, this.resetViewport(), this.redraw(), window.setTimeout(function() {
        for (var t, r = 0; t = e[r]; r++) t.remove()
    }, 0)
}, MarkerClusterer.prototype.redraw = function() {
    this.createClusters_()
}, MarkerClusterer.prototype.distanceBetweenPoints_ = function(e, t) {
    if (!e || !t) return 0;
    var r = (t.lat() - e.lat()) * Math.PI / 180,
        s = (t.lng() - e.lng()) * Math.PI / 180,
        o = Math.sin(r / 2) * Math.sin(r / 2) + Math.cos(e.lat() * Math.PI / 180) * Math.cos(t.lat() * Math.PI / 180) * Math.sin(s / 2) * Math.sin(s / 2);
    return 2 * Math.atan2(Math.sqrt(o), Math.sqrt(1 - o)) * 6371
}, MarkerClusterer.prototype.addToClosestCluster_ = function(e, t) {
    for (var r, s = 4e4, o = null, i = (e.getPosition(), 0); r = this.clusters_[i]; i++) {
        var n = r.getCenter();
        if (n) {
            var a = this.distanceBetweenPoints_(n, e.getPosition());
            a < s && (s = a, o = r)
        }
    }
    if (o && o.isMarkerInClusterBounds(e)) o.addMarker(e, t);
    else {
        var r = new Cluster(this);
        r.addMarker(e, t), this.clusters_.push(r)
    }
}, MarkerClusterer.prototype.createClusters_ = function() {
    if (this.ready_)
        for (var e, t = new google.maps.LatLngBounds(this.map_.getBounds().getSouthWest(), this.map_.getBounds().getNorthEast()), r = this.getExtendedBounds(t), s = 0; e = this.markers_[s]; s++) !e.isAdded && this.isMarkerInBounds_(e, r) && showingMarker != e.getTitle() && this.addToClosestCluster_(e, s)
}, Cluster.prototype.isMarkerAlreadyAdded = function(e) {
    if (this.markers_.indexOf) return -1 != this.markers_.indexOf(e);
    for (var t, r = 0; t = this.markers_[r]; r++)
        if (t == e) return !0;
    return !1
}, Cluster.prototype.addMarker = function(e, t) {
    if (this.isMarkerAlreadyAdded(e)) return !1;
    if (this.center_) {
        if (this.averageCenter_) {
            var r = this.markers_.length + 1,
                s = (this.center_.lat() * (r - 1) + e.getPosition().lat()) / r,
                o = (this.center_.lng() * (r - 1) + e.getPosition().lng()) / r;
            this.center_ = new google.maps.LatLng(s, o), this.calculateBounds_()
        }
    } else this.center_ = e.getPosition(), this.calculateBounds_();
    e.isAdded = !0, this.markers_.push(e), this.markerIndex_.push(t);
    var i = this.markers_.length;
    if (i < this.minClusterSize_ && e.getMap() != this.map_ && (e.setMap(this.map_), e.set("label", "")), i == this.minClusterSize_)
        for (var n = 0; n < i; n++) this.markers_[n].set("label", ""), this.markers_[n].setMap(null);
    return i >= this.minClusterSize_ && (e.setMap(null), e.set("label", "")), this.updateIcon(), !0
}, Cluster.prototype.getMarkerClusterer = function() {
    return this.markerClusterer_
}, Cluster.prototype.getBounds = function() {
    for (var e, t = new google.maps.LatLngBounds(this.center_, this.center_), r = this.getMarkers(), s = 0; e = r[s]; s++) t.extend(e.getPosition());
    return t
}, Cluster.prototype.remove = function() {
    this.clusterIcon_.remove(), this.markers_.length = 0, delete this.markers_, delete this.markerIndex_
}, Cluster.prototype.getSize = function() {
    return this.markers_.length
}, Cluster.prototype.getMarkers = function() {
    return this.markers_
}, Cluster.prototype.getCenter = function() {
    return this.center_
}, Cluster.prototype.calculateBounds_ = function() {
    var e = new google.maps.LatLngBounds(this.center_, this.center_);
    this.bounds_ = this.markerClusterer_.getExtendedBounds(e)
}, Cluster.prototype.isMarkerInClusterBounds = function(e) {
    return this.bounds_.contains(e.getPosition())
}, Cluster.prototype.getMap = function() {
    return this.map_
}, Cluster.prototype.updateIcon = function() {
    if (this.map_.getZoom() > this.markerClusterer_.getMaxZoom())
        for (var e, t = 0; e = this.markers_[t]; t++) e.setMap(this.map_);
    else {
        if (this.markers_.length < this.minClusterSize_) return void this.clusterIcon_.hide();
        var r = this.markerClusterer_.getStyles().length,
            s = this.markerClusterer_.getCalculator()(this.markers_, r);
        this.clusterIcon_.setCenter(this.center_), this.clusterIcon_.setSums(s), this.clusterIcon_.show()
    }
}, ClusterIcon.prototype.triggerClusterClick = function() {
    var e = function(e) {
            return e.getZoom() >= e.maxZoom
        },
        t = function(e, t) {
            var r = e[0];
            return e.every(function(e) {
                return t(r, e)
            })
        },
        r = function(e) {
            var r = e.map(function(e) {
                return e.getPosition()
            });
            return t(r, function(e, t) {
                return e.equals(t)
            })
        },
        s = this.cluster_.getMarkerClusterer(),
        o = s.locale || "en";
    google.maps.event.trigger(s, "clusterclick", this.cluster_);
    var i = this.cluster_.getMarkers();
    if (r(i) || e(this.map_))
        if (this.showingInfo_) this.cluster_.markerClusterer_.infowindow_.close(), this.cluster_.markerClusterer_.showingMarker_ = "", this.showingInfo_ = !1;
        else {
            this.cluster_.markerClusterer_.showingMarker_ = i[0].getTitle(), this.showingInfo_ = !0;
            var n = "<div id='map_bubble'><img class='bubble-loader-gif' src='https://s3.amazonaws.com/sharetribe/assets/ajax-loader-grey.gif'></div>";
            this.cluster_.markerClusterer_.infowindow_.setContent(n);
            for (var a = [], u = 0; i[u]; u++) a.push(this.cluster_.markerClusterer_.markerContents_[this.cluster_.markerIndex_[u]]);
            $.get("/" + o + "/listing_bubble_multiple/" + a.join(","), function(e) {
                function t(e, t, r, s) {
                    e > 0 ? r.removeClass("disabled") : r.addClass("disabled"), e < t - 1 ? s.removeClass("disabled") : s.addClass("disabled")
                }

                function r(e) {
                    _.text(e + 1)
                }

                function s(e, t, r) {
                    r.css({
                        left: -1 * e * t + "px"
                    })
                }

                function o(e, o, i, n, a) {
                    return function(u) {
                        t(u, e, i, n), s(u, o, a), r(u)
                    }
                }
                $("#map_bubble").html(e);
                var n = 0,
                    u = i.length,
                    l = $(".bubble-navi-left"),
                    h = $(".bubble-navi-right"),
                    p = $(".bubble-multi-content"),
                    _ = $(".buble-navi-selected-item");
                $(".buble-navi-total-items").text(a.length);
                var c = 200;
                p.width(c * u);
                var d = o(u, c, l, h, p);
                l.on("click", function() {
                    n = Math.max(n - 1, 0), d(n)
                }), h.on("click", function() {
                    var e = u - 1;
                    n = Math.min(n + 1, e), d(n)
                }), d(n, u, c, l, h, p)
            }), this.cluster_.markerClusterer_.infowindow_.setMaxHeight(180), this.cluster_.markerClusterer_.infowindow_.setMinHeight(180), this.cluster_.markerClusterer_.infowindow_.open(this.map_, i[0])
        }
    else if (s.isZoomOnClick()) {
        var l = this.map_.getZoom();
        this.map_.fitBounds(this.cluster_.getBounds()), this.map_.getZoom() - l > 2 && this.map_.setZoom(l + 2)
    }
}, ClusterIcon.prototype.onAdd = function() {
    if (this.div_ = document.createElement("DIV"), this.visible_) {
        var e = this.getPosFromLatLng_(this.center_);
        this.div_.style.cssText = this.createCss(e), this.div_.innerHTML = this.sums_.text
    }
    this.getPanes().overlayMouseTarget.appendChild(this.div_);
    var t = this;
    google.maps.event.addDomListener(this.div_, "click", function() {
        t.triggerClusterClick()
    })
}, ClusterIcon.prototype.getPosFromLatLng_ = function(e) {
    var t = this.getProjection().fromLatLngToDivPixel(e);
    return t.x -= parseInt(this.width_ / 2, 10), t.y -= parseInt(this.height_ / 2, 10), t
}, ClusterIcon.prototype.draw = function() {
    if (this.visible_) {
        var e = this.getPosFromLatLng_(this.center_);
        this.div_.style.top = e.y + "px", this.div_.style.left = e.x + "px"
    }
}, ClusterIcon.prototype.hide = function() {
    this.div_ && (this.div_.style.display = "none"), this.visible_ = !1
}, ClusterIcon.prototype.show = function() {
    if (this.div_) {
        var e = this.getPosFromLatLng_(this.center_);
        this.div_.style.cssText = this.createCss(e), this.div_.style.display = ""
    }
    this.visible_ = !0
}, ClusterIcon.prototype.remove = function() {
    this.setMap(null)
}, ClusterIcon.prototype.onRemove = function() {
    this.div_ && this.div_.parentNode && (this.hide(), this.div_.parentNode.removeChild(this.div_), this.div_ = null)
}, ClusterIcon.prototype.setSums = function(e) {
    this.sums_ = e, this.text_ = e.text, this.index_ = e.index, this.div_ && (this.div_.innerHTML = e.text), this.useStyle()
}, ClusterIcon.prototype.useStyle = function() {
    var e = Math.max(0, this.sums_.index - 1);
    e = Math.min(this.styles_.length - 1, e);
    var t = this.styles_[e];
    this.url_ = t.url, this.height_ = t.height, this.width_ = t.width, this.textColor_ = t.textColor, this.anchor_ = t.anchor, this.textSize_ = t.textSize, this.backgroundPosition_ = t.backgroundPosition
}, ClusterIcon.prototype.setCenter = function(e) {
    this.center_ = e
}, ClusterIcon.prototype.createCss = function(e) {
    var t = [];
    t.push("background-image:url(" + this.url_ + ");");
    var r = this.backgroundPosition_ ? this.backgroundPosition_ : "0 0";
    t.push("background-position:" + r + ";"), "object" == typeof this.anchor_ ? ("number" == typeof this.anchor_[0] && this.anchor_[0] > 0 && this.anchor_[0] < this.height_ ? t.push("height:" + (this.height_ - this.anchor_[0]) + "px; padding-top:" + this.anchor_[0] + "px;") : t.push("height:" + this.height_ + "px; line-height:" + this.height_ + "px;"), "number" == typeof this.anchor_[1] && this.anchor_[1] > 0 && this.anchor_[1] < this.width_ ? t.push("width:" + (this.width_ - this.anchor_[1]) + "px; padding-left:" + this.anchor_[1] + "px;") : t.push("width:" + this.width_ + "px; text-align:center;")) : t.push("height:" + this.height_ + "px; line-height:" + this.height_ + "px; width:" + this.width_ + "px; text-align:center;");
    var s = this.textColor_ ? this.textColor_ : "white",
        o = this.textSize_ ? this.textSize_ : 11;
    return t.push("cursor:pointer; top:" + e.y + "px; left:" + e.x + "px; color:" + s + "; position:absolute; font-size:" + o + "px; font-family:Arial,sans-serif; font-weight:bold"), t.join("")
}, window.MarkerClusterer = MarkerClusterer, MarkerClusterer.prototype.addMarker = MarkerClusterer.prototype.addMarker, MarkerClusterer.prototype.addMarkers = MarkerClusterer.prototype.addMarkers, MarkerClusterer.prototype.clearMarkers = MarkerClusterer.prototype.clearMarkers, MarkerClusterer.prototype.fitMapToMarkers = MarkerClusterer.prototype.fitMapToMarkers, MarkerClusterer.prototype.getCalculator = MarkerClusterer.prototype.getCalculator, MarkerClusterer.prototype.getGridSize = MarkerClusterer.prototype.getGridSize, MarkerClusterer.prototype.getExtendedBounds = MarkerClusterer.prototype.getExtendedBounds, MarkerClusterer.prototype.getMap = MarkerClusterer.prototype.getMap, MarkerClusterer.prototype.getMarkers = MarkerClusterer.prototype.getMarkers, MarkerClusterer.prototype.getMaxZoom = MarkerClusterer.prototype.getMaxZoom, MarkerClusterer.prototype.getStyles = MarkerClusterer.prototype.getStyles, MarkerClusterer.prototype.getTotalClusters = MarkerClusterer.prototype.getTotalClusters, MarkerClusterer.prototype.getTotalMarkers = MarkerClusterer.prototype.getTotalMarkers, MarkerClusterer.prototype.redraw = MarkerClusterer.prototype.redraw, MarkerClusterer.prototype.removeMarker = MarkerClusterer.prototype.removeMarker, MarkerClusterer.prototype.removeMarkers = MarkerClusterer.prototype.removeMarkers, MarkerClusterer.prototype.resetViewport = MarkerClusterer.prototype.resetViewport, MarkerClusterer.prototype.repaint = MarkerClusterer.prototype.repaint, MarkerClusterer.prototype.setCalculator = MarkerClusterer.prototype.setCalculator, MarkerClusterer.prototype.setGridSize = MarkerClusterer.prototype.setGridSize, MarkerClusterer.prototype.setMaxZoom = MarkerClusterer.prototype.setMaxZoom, MarkerClusterer.prototype.onAdd = MarkerClusterer.prototype.onAdd, MarkerClusterer.prototype.draw = MarkerClusterer.prototype.draw, Cluster.prototype.getCenter = Cluster.prototype.getCenter, Cluster.prototype.getSize = Cluster.prototype.getSize, Cluster.prototype.getMarkers = Cluster.prototype.getMarkers, ClusterIcon.prototype.onAdd = ClusterIcon.prototype.onAdd, ClusterIcon.prototype.draw = ClusterIcon.prototype.draw, ClusterIcon.prototype.onRemove = ClusterIcon.prototype.onRemove;
