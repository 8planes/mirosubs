goog.provide('mirosubs.testing.StubVideoPlayer');

/**
 * @fileoverview This is for testing components that interact with 
 *     the video player.
 *
 */

mirosubs.testing.StubVideoPlayer = function() {
    mirosubs.AbstractVideoPlayer.call(this);
    /**
     * Can be set to artificial values for the purpose of unit 
     * testing components.
     */
    this.playheadTime = 0;
};
goog.inherits(mirosubs.testing.StubVideoPlayer, mirosubs.AbstractVideoPlayer);

mirosubs.testing.StubVideoPlayer.prototype.getPlayheadTime = function() {
    return this.playheadTime;
};