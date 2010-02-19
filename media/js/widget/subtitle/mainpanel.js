goog.provide('mirosubs.subtitle.MainPanel');
goog.provide('mirosubs.subtitle.MainPanel.EventType');

/**
 * @fileoverview In this class, the three states {0, 1, 2, 3} correspond to 
 *     { transcribe, sync, review, finished }.
 */

/**
 * 
 * @param {mirosubs.subtitle.ServerModel} serverModel
 * @param {Array.<Object.<string, *>>} existingCaptions existing captions in 
 *     json object format.
 */
mirosubs.subtitle.MainPanel = function(videoPlayer, 
                                       serverModel, 
                                       existingCaptions) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    var uw = this.unitOfWork_ = new mirosubs.UnitOfWork();
    /**
     * Array of captions.
     * @type {Array.<mirosubs.subtitle.EditableCaption>}
     */
    this.captions_ = 
        goog.array.map(existingCaptions, 
                       function(caption) { 
                           return new mirosubs.subtitle.EditableCaption(uw, caption);
                       });
    this.captionManager_ = 
        new mirosubs.CaptionManager(videoPlayer.getPlayheadFn());
    this.captionManager_.addCaptions(existingCaptions);
    this.getHandler().listen(this.captionManager_,
                             mirosubs.CaptionManager.EventType.CAPTION,
                             this.captionReached_, false, this);
    this.serverModel_ = serverModel;
    this.serverModel_.init(uw);
    this.tabs_ = [];
    this.state_ = -1; // dom not created yet.
};
goog.inherits(mirosubs.subtitle.MainPanel, goog.ui.Component);

mirosubs.subtitle.MainPanel.EventType = {
    FINISHED: "finishedediting"
};

mirosubs.subtitle.MainPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.subtitle.MainPanel.prototype.handleKeyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.CTRL) {
        var now = this.videoPlayer_.getPlayheadTime();
        this.videoPlayer_.setPlayheadTime(Math.max(now - 3, 0));
        this.videoPlayer_.play();
    }
    if (event.keyCode == goog.events.KeyCodes.TAB){
        //TODO: this violates accessibility guidelines. Use another key instead of TAB!
        this.videoPlayer_.togglePause();
        event.preventDefault();
    }
};

mirosubs.subtitle.MainPanel.prototype.createDom = function() {
    mirosubs.subtitle.MainPanel.superClass_.createDom.call(this);

    var that = this;
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    el.appendChild(this.contentElem_ = $d('div'));
    var nextStepAnchorElem;
    el.appendChild($d('div', { 'className': 'mirosubs-nextStep' },
                      nextStepAnchorElem = $d('a', { 'href': '#'}, 
                         "Done? ",
                         this.nextStepLink_ = 
                         $d('strong', null, 'Next Step'))));
    this.getHandler().listen(nextStepAnchorElem, 'click', 
                             this.nextStepClicked_);
    this.tabs_ = this.createTabElems_()
    el.appendChild($d('ul', { 'className' : 'mirosubs-nav' }, this.tabs_));
    this.setState_(0);
    this.getHandler().listen(document,
                             goog.events.EventType.KEYDOWN,
                             this.handleKeyDown_, false, this);
};

mirosubs.subtitle.MainPanel.prototype.setNextStepText_ = function(buttonText) {
    goog.dom.setTextContent(this.nextStepLink_, buttonText);
};

mirosubs.subtitle.MainPanel.prototype.createTabElems_ = function() {
    var that = this;
    var h = this.getHandler();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    return goog.array.map(["Transcribe", "Sync", "Review"],
                          function(label, index) {
                              var a = $d('a', { 'href': '#' }, label);
                              h.listen(a, 'click', 
                                       function(event) {
                                           that.setState_(index);
                                           event.preventDefault();
                                       });
                              return $d('li', 
                                        {'className': 'mirosubs-nav' + label}, 
                                        a);
                          });
};
mirosubs.subtitle.MainPanel.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.videoPlayer_.showCaptionText(c ? c['caption_text'] : '');
};
mirosubs.subtitle.MainPanel.prototype.nextStepClicked_ = function(event) {
    this.setState_(this.state_ + 1);
    event.preventDefault();
};
mirosubs.subtitle.MainPanel.prototype.setState_ = function(state) {
    if (state == this.state_)
        return;
    if (state == 3) {
        this.submitWorkThenProgressToFinishedState_();
        return;
    }
    else
        this.progressToState_(state);
};
mirosubs.subtitle.MainPanel.prototype.progressToState_ = function(state) {
    this.state_ = state;
    if (state < 4) {
        this.disposeCurrentWidget_();
        this.removeChildren(true);
        this.videoPlayer_.setPlayheadTime(0);
        this.selectTab_(state);
        this.addChild(this.makeNextWidget_(state), true);
        var nextStepText;
        if (state < 2)
            nextStepText = "Next Step";
        else if (state == 2)
            nextStepText = "Submit Work";
        else
            nextStepText = "Finish";
        this.setNextStepText_(nextStepText);
    }
    else
        this.finishEditing_();
};
mirosubs.subtitle.MainPanel.prototype.selectTab_ = function(state) {
    var c = goog.dom.classes;
    for (var i = 0; i < this.tabs_.length; i++) {
        if (i == state)
            c.add(this.tabs_[i], 'active');
        else
            c.remove(this.tabs_[i], 'active');
    }
};

mirosubs.subtitle.MainPanel.prototype.disposeCurrentWidget_ = function() {
    if (this.currentWidget_) {
        this.currentWidget_.dispose();
        this.currentWidget_ = null;
    }
};

mirosubs.subtitle.MainPanel.prototype.makeNextWidget_ = function(state) {
    if (state == 0)
        this.currentWidget_ = new mirosubs.subtitle.TranscribePanel(
            this.captions_, this.unitOfWork_, this.videoPlayer_);
    else if (state == 1)
        this.currentWidget_ = new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.videoPlayer_.getIsPlayingFn(),
            this.captionManager_);
    else if (state == 2)
        this.currentWidget_ = new mirosubs.subtitle.ReviewPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.videoPlayer_.getIsPlayingFn(),
            this.captionManager_);    
    else
        this.currentWidget_ = 
            new mirosubs.subtitle.FinishedPanel(this.serverModel_);
    return this.currentWidget_;
};

mirosubs.subtitle.MainPanel.prototype.submitWorkThenProgressToFinishedState_ =
    function() {
    var that = this;
    // TODO: show loading
    this.serverModel_.finish(function() {
            // TODO: hide loading
            that.progressToState_(3);
        });
};

mirosubs.subtitle.MainPanel.prototype.finishEditing_ = function() {
    this.dispatchEvent(mirosubs.subtitle.MainPanel
                       .EventType.FINISHED);
    this.dispose();
};

mirosubs.subtitle.MainPanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.MainPanel.superClass_.disposeInternal.call(this);
    this.disposeCurrentWidget_();
    this.serverModel_.dispose();
    this.captionManager_.dispose();
    this.videoPlayer_.showCaptionText('');
};

