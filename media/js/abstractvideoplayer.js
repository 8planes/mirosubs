

goog.provide('mirosubs.AbstractVideoPlayer');

/**
 * Abstract base class for video player implementations. Any video player 
 * used with MiroSubs must implement the abstract methods defined by this 
 * class.
 * @constructor
 */
mirosubs.AbstractVideoPlayer = function() {};

mirosubs.AbstractVideoPlayer.prototype.getPlayheadFn = function() {
    return goog.bind(this.getPlayheadTime, this);
};
mirosubs.AbstractVideoPlayer.prototype.isPaused = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.videoEnded = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.play = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.pause = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.togglePause = function() {
    if (this.isPaused() || this.videoEnded())
        this.play();
    else
        this.pause();
};
mirosubs.AbstractVideoPlayer.prototype.getPlayheadTime = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    goog.abstractMethod();
};
mirosubs.AbstractVideoPlayer.prototype.showCaptionText = function(text) {
    goog.abstractMethod();
};
