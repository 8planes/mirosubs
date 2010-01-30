goog.provide('mirosubs.CaptionDisplayWidget');

mirosubs.CaptionDisplayWidget = function(videoPlayer, videoID, 
                                         playheadFn) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    this.videoID_ = videoID;
    this.playheadFn_ = playheadFn;
};
goog.inherits(mirosubs.CaptionDisplayWidget, goog.ui.Component);
mirosubs.CaptionDisplayWidget.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createElement('div'));
};
mirosubs.CaptionDisplayWidget.prototype.decorateInternal = function(element) {
    mirosubs.CaptionDisplayWidget.superClass_.decorateInternal.call(this, element);
    this.captionMenu_ = new mirosubs.CaptionMenu(this.videoID_);
    this.addChild(this.captionMenu_, true);
    goog.events.listenOnce(this.captionMenu_, 
                           mirosubs.CaptionMenu.SELECTION_EVENT,
                           this.captionsSelected_,
                           false, this);
};
mirosubs.CaptionDisplayWidget.prototype.captionsSelected_ = function(event) {
    // for now we only have original language, so...
    this.removeChild(this.captionMenu_)
    this.getElement().appendChild(this.dom_.createDom('span', null, "Loading..."));
    var that = this;
    mirosubs.Rpc.call('fetch_captions', { 'video_id': that.videoID_ }, 
                      function(captions) {
                          that.captionsFetched_(captions);
                      });
};
mirosubs.CaptionDisplayWidget.prototype.captionsFetched_ = function(captions) {
    this.getElement().innerHTML = "";
    this.captionManager_ = new mirosubs.CaptionManager(this.playheadFn_);
    this.captionManager_.addCaptions(captions);
    var that = this;
    this.captionManager_.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                          function(jsonCaptionEvent) {
                                              var c = jsonCaptionEvent.caption;
                                              that.videoPlayer_.showCaptionText(c ? c['caption_text'] : '');
                                          });
    this.getElement().innerHTML = "Subtitles Active: Original Language&nbsp;";
};