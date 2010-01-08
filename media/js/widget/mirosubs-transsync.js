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
    /**
     * Always in correct order by time.
     * @type {Array.<mirosubs.trans.EditableCaption>}
     */ 
    this.captions_ = captions;
    /**
     * A map of caption_id to mirosubs.trans.SyncWidget.Caption_
     */
    this.captionWidgetMap_ = {};
    /**
     * The current mirosubs.trans.SyncWidget.Caption_ displayed, 
     * or null if no captions have been displayed yet, or if we are
     * in between captions.
     */
    this.currentCaptionWidget_ = null;

    this.playheadFn_ = playheadFn;
    this.captionManager_ = captionManager;
    this.captionManager_.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                          this.captionReached_,
                                          false, this);
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
        var captionWidget = new mirosubs.trans.SyncWidget.Caption_(this.captions_[i]);
        this.addChild(captionWidget, true);
        this.captionWidgetMap_[this.captions_[i].getCaptionID() + ''] = captionWidget;
    }
    this.keyHandler_ = new goog.events.KeyHandler(document);
    this.eventHandler_.listen(this.keyHandler_,
                              goog.events.KeyHandler.EventType.KEY,
                              this.handleKey_);
};
mirosubs.trans.SyncWidget.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE) {
        console.log("space clicked!");
        var playheadTime = this.playheadFn_();
        var lastCaption = null;
        console.log("this.currentCaptionWidget_ is " + this.currentCaptionWidget_);
        if (this.currentCaptionWidget_ != null) {
            lastCaption = this.currentCaptionWidget_.caption;
            if (lastCaption.getStartTime() != -1)
                lastCaption.setEndTime(playheadTime);
        }
        console.log("lastCaption is " + lastCaption);
        // TODO: get rid of this linear search in the future by getting 
        // another map in instance state.
        var nextIndex = lastCaption == null ? 
            0 : goog.array.indexOf(this.captions_, lastCaption) + 1;
        if (nextIndex < this.captions_.length) {
            var currentCaption = this.captions_[nextIndex];
            var isInManager = currentCaption.getStartTime() != -1;
            currentCaption.setStartTime(playheadTime);
            currentCaption.setEndTime(99999);
            if (!isInManager)
                this.captionManager_.addCaptions([currentCaption.jsonCaption]);
        }
    }
};
mirosubs.trans.SyncWidget.prototype.captionReached_ = function(jsonCaptionEvent) {
    var jsonCaption = jsonCaptionEvent.caption;
    console.log("captionReached. jsonCaption is " + jsonCaption);
    if (this.currentCaptionWidget_ != null)
        this.currentCaptionWidget_.setCurrent(false);
    if (jsonCaption != null) {
        var captionID = jsonCaption['caption_id'];
        console.log("captionID is " + captionID);
        this.currentCaptionWidget_ = this.captionWidgetMap_[captionID + ''];
        console.log("currentCaptionWidget_ is " + this.currentCaptionWidget_);
        this.currentCaptionWidget_.setCurrent(true);
    }
    else {
        this.currentCaptionWidget_ = null;
    }
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
    this.caption = caption;
    goog.ui.Component.call(this, opt_domHelper);
};
goog.inherits(mirosubs.trans.SyncWidget.Caption_, goog.ui.Component);
mirosubs.trans.SyncWidget.Caption_.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement("div"));
};
mirosubs.trans.SyncWidget.Caption_.prototype.decorateInternal = function(element) {
    mirosubs.trans.SyncWidget.Caption_.superClass_.decorateInternal.call(this, element);
    this.addChild(this.labelInput = new goog.ui.LabelInput("(silence)"), true);
    goog.events.listen(this.labelInput.getElement(),
                       goog.events.EventType.KEYUP,
                       this.keyUp_,
                       false, this);
    this.labelInput.setValue(this.caption.getText());
};
mirosubs.trans.SyncWidget.Caption_.prototype.keyUp_ = function(event) {
    this.caption.setText(this.labelInput.getValue());
};
mirosubs.trans.SyncWidget.Caption_.prototype.setCurrent = function(current) {
    var className = "mirosubs-activecaption-input-label";
    console.log("setCurrent called: " + current);
    if (current)
        goog.dom.classes.add(this.getElement(), className);
    else
        goog.dom.classes.remove(this.getElement(), className);
};