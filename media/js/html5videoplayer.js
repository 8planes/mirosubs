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

/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.Html5VideoPlayer.prototype.showCaptionText = function(text) {
    if (text == null || text == "") {
        if (this.captionElem_ != null) {
            this.videoDiv_.removeChild(this.captionElem_);
            this.captionElem_ = null;
        }
    }
    else {
        if (this.captionElem_ == null) {
            this.captionElem_ = document.createElement("div");
            this.captionElem_.setAttribute("class", "mirosubs-captionDiv");
            var videoSize = goog.style.getSize(this.videoElem_);
            this.captionElem_.style.top = (videoSize.height - 60) + "px";
            this.videoDiv_.appendChild(this.captionElem_);
        }
        goog.dom.setTextContent(this.captionElem_, text);
    }
};

