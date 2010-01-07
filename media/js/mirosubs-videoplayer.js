goog.provide('mirosubs.VideoPlayer');

mirosubs.VideoPlayer = function(video_elem) {
    this.video_elem = video_elem;
};

mirosubs.VideoPlayer.wrap = function(video_elem_id) {
    // in the future can be used to abstract flash player, etc.
    return new mirosubs.VideoPlayer(goog.dom.$(video_elem_id));
};

mirosubs.VideoPlayer.prototype.getPlayheadTime = function() {
    return this.video_elem.currentTime;
};

/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.VideoPlayer.prototype.showCaptionText = function(text) {
};