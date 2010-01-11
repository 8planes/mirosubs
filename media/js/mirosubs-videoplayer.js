goog.provide('mirosubs.VideoPlayer');

mirosubs.VideoPlayer = function(videoElem) {
    this.videoElem_ = videoElem;
};

mirosubs.VideoPlayer.wrap = function(video_elem_id) {
    // in the future can be used to abstract flash player, etc.
    return new mirosubs.VideoPlayer(goog.dom.$(video_elem_id));
};

mirosubs.VideoPlayer.prototype.getPlayheadTime = function() {
    return this.videoElem_.currentTime;
};

/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.VideoPlayer.prototype.showCaptionText = function(text) {
};