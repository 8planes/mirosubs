goog.provide('mirosubs.subtitle.SyncPanel');

/**
 *
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions The captions 
 *     for the video, so far.
 * @param {Function} playheadFn Function that returns current playhead time for video.
 * @param {mirosubs.CaptionManager} Caption manager, already containing captions with 
 *     start_time set.
 */
mirosubs.subtitle.SyncPanel = function(captions, playheadFn, captionManager) {
    goog.ui.Component.call(this);
    /**
     * Always in correct order by time.
     * @type {Array.<mirosubs.subtitle.EditableCaption>}
     */ 
    this.captions_ = captions;
    /**
     * A map of caption_id to mirosubs.subtitle.SyncPanel.Caption_
     */
    this.captionWidgetMap_ = {};
    /**
     * The current mirosubs.subtitle.SyncPanel.Caption_ displayed, 
     * or null if no captions have been displayed yet, or if we are
     * in between captions.
     */
    this.currentCaptionWidget_ = null;

    this.playheadFn_ = playheadFn;
    this.captionManager_ = captionManager;
    this.getHandler().listen(captionManager,
                             mirosubs.CaptionManager.EventType.CAPTION,
                             this.captionReached_,
                             false, this);
    this.keyHandler_ = null;
};
goog.inherits(mirosubs.subtitle.SyncPanel, goog.ui.Component);
mirosubs.subtitle.SyncPanel.prototype.createDom = function() {
    mirosubs.subtitle.SyncPanel.superClass_.createDom.call(this);
    for (var i = 0; i < this.captions_.length; i++) {
        var captionWidget = new mirosubs.subtitle.SyncPanel.Caption_(this.captions_[i]);
        this.addChild(captionWidget, true);
        this.captionWidgetMap_[this.captions_[i].getCaptionID() + ''] = captionWidget;
    }
    this.keyHandler_ = new goog.events.KeyHandler(document);
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_);
};
mirosubs.subtitle.SyncPanel.prototype.handleKey_ = function(event) {
    // I'm using the N key here instead of space because space pauses the 
    // video.
    if (event.keyCode == goog.events.KeyCodes.N) {
        var playheadTime = this.playheadFn_();
        var lastCaption = null;
        if (this.currentCaptionWidget_ != null) {
            lastCaption = this.currentCaptionWidget_.caption;
            if (lastCaption.getStartTime() != -1)
                lastCaption.setEndTime(playheadTime);
        }
        // TODO: get rid of this linear search in the future by getting 
        // another map in instance state.
        var nextIndex = lastCaption == null ? 
            0 : goog.array.indexOf(this.captions_, lastCaption) + 1;
        if (nextIndex < this.captions_.length) {
            var currentCaption = this.captions_[nextIndex];
            var isInManager = currentCaption.getStartTime() != -1;
            currentCaption.setStartTime(playheadTime);
            currentCaption.setEndTime(99999);
            console.log("adding to caption mgr!");
            if (!isInManager)
                this.captionManager_.addCaptions([currentCaption.jsonCaption]);
        }
    }
};
mirosubs.subtitle.SyncPanel.prototype.captionReached_ = function(jsonCaptionEvent) {
    var jsonCaption = jsonCaptionEvent.caption;
    if (this.currentCaptionWidget_ != null)
        this.currentCaptionWidget_.setCurrent(false);
    if (jsonCaption != null) {
        var captionID = jsonCaption['caption_id'];
        this.currentCaptionWidget_ = this.captionWidgetMap_[captionID + ''];
        this.currentCaptionWidget_.setCurrent(true);
    }
    else {
        this.currentCaptionWidget_ = null;
    }
};
mirosubs.subtitle.SyncPanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.SyncPanel.superClass_.disposeInternal.call(this);
    if (this.keyHandler_)
        this.keyHandler_.dispose();
};

/**
 * @param {JSONCaption} caption The caption for this Caption widget.
 */
mirosubs.subtitle.SyncPanel.Caption_ = function(caption, opt_domHelper) {
    this.caption = caption;
    goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(mirosubs.subtitle.SyncPanel.Caption_, goog.ui.Component);
mirosubs.subtitle.SyncPanel.Caption_.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement("div"));
};
mirosubs.subtitle.SyncPanel.Caption_.prototype.decorateInternal = function(element) {
    mirosubs.subtitle.SyncPanel.Caption_.superClass_.decorateInternal.call(this, element);
    this.addChild(this.labelInput = new goog.ui.LabelInput("(silence)"), true);
    goog.events.listen(this.labelInput.getElement(),
                       goog.events.EventType.KEYUP,
                       this.keyUp_,
                       false, this);
    this.labelInput.setValue(this.caption.getText());
};
mirosubs.subtitle.SyncPanel.Caption_.prototype.keyUp_ = function(event) {
    this.caption.setText(this.labelInput.getValue());
};
mirosubs.subtitle.SyncPanel.Caption_.prototype.setCurrent = function(current) {
    var className = "mirosubs-activecaption-input-label";
    if (current)
        goog.dom.classes.add(this.getElement(), className);
    else
        goog.dom.classes.remove(this.getElement(), className);
};