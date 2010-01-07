goog.provide('mirosubs.trans.SyncWidget');

/**
 *
 * @param {Array.<mirosubs.trans.EditableCaption>} captions The captions for the video, so far.
 * @param {Function} playheadFn Function that returns current playhead time for video.
 * @param {mirosubs.CaptionManager} Caption manager, already containing captions with 
 *     start_time set.
 */
mirosubs.trans.SyncWidget = function(captions, playheadFn, captionManager, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    this.captions_ = captions;
    /**
     * A map of caption_id to Caption_ widget.
     */
    this.captionWidgetMap_ = {};
    this.playheadFn = playheadFn;
    this.captionManager_ = captionManager;
    this.captionManager_.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                          this.captionReached_,
                                          false, this);
    this.lastCaptionIndex_ = -1;
    this.eventHandler_ = new goog.events.EventHandler(this);
    this.keyHandler_ = null;
};
goog.inherits(mirosubs.trans.SyncWidget, goog.ui.Component);
mirosubs.trans.SyncWidget.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement('div'));
};
mirosubs.trans.SyncWidget.prototype.decorateInternal = function(element) {
    mirosubs.trans.SyncWidget.superClass_.decorateInternal.call(this, element);
    for (var i = 0; i < this.captions_.length; i++) {
        
        this.addChild(new mirosubs.trans.SyncWidget.Caption_(this.captions_[i]));
    }
    this.keyHandler_ = new goog.events.KeyHandler(document);
    this.eventHandler_.listen(this.keyHandler_,
                              goog.events.KeyHandler.EventType.KEY,
                              this.handleKey_);
};
mirosubs.trans.SyncWidget.prototype.handleKey_ = function(event) {
    if (event.keyCode == keyCodes.SPACE) {
        
    }
};
mirosubs.trans.SyncWidget.prototype.captionReached_ = function(jsonCaptionEvent) {
    var jsonCaption = jsonCaptionEvent.caption;
    
};
mirosubs.trans.SyncWidget.prototype.disposeInternal = function() {
    mirosubs.trans.SyncWidget.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
    if (this.keyHandler_)
        this.keyHandler_.dispose();
    this.captionManager_.removeEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                             this.captionReached_,
                                             false, this);
};

/**
 * @param {JSONCaption} caption The caption for this Caption widget.
 */
mirosubs.trans.SyncWidget.Caption_ = function(caption, opt_domHelper) {
    this.caption_ = caption;
    goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(mirosubs.trans.SyncWidget.Caption_, goog.ui.Component);
mirosubs.trans.SyncWidget.Caption_.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement("div"));
};
mirosubs.trans.SyncWidget.Caption_.prototype.decorateInternal = function(element) {
    mirosubs.trans.SyncWidget.Caption_.superClass_.decorateInternal.call(this, element);
    this.addChild(this.labelInput = new goog.ui.LabelInput("(silence)"), true);
    
};