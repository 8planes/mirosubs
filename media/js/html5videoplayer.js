goog.provide('mirosubs.Html5VideoPlayer');

mirosubs.Html5VideoPlayer = function(videoElem) {
    mirosubs.AbstractVideoPlayer.call(this);
    this.videoElem_ = videoElem;
    this.videoDiv_ = videoElem.parentNode;
    this.captionElem_ = null;
};
goog.inherits(mirosubs.Html5VideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.Html5VideoPlayer.wrap = function(video_elem_id) {
    // in the future can be used to abstract flash player, etc.
    return new mirosubs.Html5VideoPlayer(goog.dom.$(video_elem_id));
};

mirosubs.Html5VideoPlayer.prototype.isPaused = function() {
    return this.videoElem_['paused'];
};

mirosubs.Html5VideoPlayer.prototype.videoEnded = function() {
    return this.videoElem_['ended'];
};

mirosubs.Html5VideoPlayer.prototype.isPlaying = function() {
    return (this.videoElem_['readyState']==3 /*HAVE_FUTURE_DATA*/ ||
            this.videoElem_['readyState']==4 /*HAVE_ENOUGH_DATA*/) &&
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
