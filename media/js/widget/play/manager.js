goog.provide('mirosubs.play.Manager');

mirosubs.play.Manager = function(videoPlayer, captions) {
    goog.Disposable.call(this);
    this.videoPlayer_ = videoPlayer;
    this.captionManager_ = new mirosubs.CaptionManager(videoPlayer.getPlayheadFn());
    this.captionManager_.addCaptions(captions);
    goog.events.listen(this.captionManager_,
                       mirosubs.CaptionManager.EventType.CAPTION,
                       this.captionReached_, false, this);
};
goog.inherits(mirosubs.play.Manager, goog.Disposable);
mirosubs.play.Manager.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.videoPlayer_.showCaptionText(c ? c['caption_text'] : '');
};
mirosubs.play.Manager.prototype.disposeInternal = function() {
    mirosubs.play.Manager.superClass_.disposeInternal.call(this);
    this.captionManager_.dispose();
};