goog.provide('mirosubs.Html5VideoPlayer');

mirosubs.Html5VideoPlayer = function(videoElem) {
    mirosubs.AbstractVideoPlayer.call(this);
    this.videoElem_ = videoElem;
    this.videoDiv_ = videoElem.parentNode;
    this.captionElem_ = null;
    this.videoEventHandler_ = new goog.events.EventHandler(this);
    this.videoEventHandler_.listen(this.videoElem_, 'play', this.videoPlaying_);
    this.videoEventHandler_.listen(this.videoElem_, 'pause', this.videoPaused_);
};
goog.inherits(mirosubs.Html5VideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.Html5VideoPlayer.wrap = function(video_elem_id) {
    // in the future can be used to abstract flash player, etc.
    return new mirosubs.Html5VideoPlayer(goog.dom.$(video_elem_id));
};

mirosubs.Html5VideoPlayer.prototype.videoPlaying_ = function(event) {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PLAY);
};

mirosubs.Html5VideoPlayer.prototype.videoPaused_ = function(event) {
    this.dispatchEvent(mirosubs.AbstractVideoPlayer.EventType.PAUSE);    
};

mirosubs.Html5VideoPlayer.prototype.isPaused = function() {
    return this.videoElem_['paused'];
};

mirosubs.Html5VideoPlayer.prototype.videoEnded = function() {
    return this.videoElem_['ended'];
};

mirosubs.Html5VideoPlayer.prototype.isPlaying = function() {
    var readyState = this.getReadyState_();
    var RS = mirosubs.Html5VideoPlayer.ReadyState_;
    return (readyState == RS.HAVE_FUTURE_DATA ||
            readyState == RS.HAVE_ENOUGH_DATA) &&
           !this.isPaused() && !this.videoEnded();
};

mirosubs.Html5VideoPlayer.prototype.play = function() {
    this.videoElem_['play']();
};

mirosubs.Html5VideoPlayer.prototype.pause = function() {
    this.videoElem_['pause']();
};

mirosubs.Html5VideoPlayer.prototype.getPlayheadTime = function() {
    return this.videoElem_["currentTime"];
};

mirosubs.Html5VideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    this.videoElem_["currentTime"] = playheadTime;
};

mirosubs.Html5VideoPlayer.prototype.getVideoSize = function() {
    return goog.style.getSize(this.videoElem_)
};

mirosubs.Html5VideoPlayer.prototype.getVideoContainerElem = function() {
    return this.videoDiv_;
};

mirosubs.Html5VideoPlayer.prototype.getReadyState_ = function() {
    return this.videoElem_["readyState"];
};

mirosubs.Html5VideoPlayer.prototype.disposeInternal = function() {
    mirosubs.Html5VideoPlayer.superClass_.disposeInternal();
    this.videoEventHandler_.dispose();
};

/**
 * See http://www.w3.org/TR/html5/video.html#dom-media-have_nothing
 * @enum
 */
mirosubs.Html5VideoPlayer.ReadyState_ = {
    HAVE_NOTHING  : 0,
    HAVE_METADATA : 1,
    HAVE_CURRENT_DATA : 2,
    HAVE_FUTURE_DATA : 3,
    HAVE_ENOUGH_DATA : 4
};