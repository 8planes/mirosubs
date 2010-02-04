goog.provide('mirosubs.subtitle.MainPanel');
goog.provide('mirosubs.subtitle.MainPanel.EventType');

/**
 * @fileoverview In this class, the three states {0, 1, 2} correspond to 
 *     { transcribe, sync, review }.
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
    this.showingInterPanel_ = false;
};
goog.inherits(mirosubs.subtitle.MainPanel, goog.ui.Component);

mirosubs.subtitle.MainPanel.EventType = {
    FINISHED: "finishedediting"
};

mirosubs.subtitle.MainPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.subtitle.MainPanel.prototype.handleKey_ = function(event) {
//TODO: listen to control key
    if (event.keyCode == goog.events.KeyCodes.CTRL ||
				event.keyCode == goog.events.KeyCodes.B) {
			var now = this.videoPlayer_.getPlayheadTime();
			this.videoPlayer_.setPlayheadTime(now>3 ? now-3 : 0);
		}

    if (event.keyCode == goog.events.KeyCodes.BACKSLASH) {
			if (this.videoPlayer_.videoElem_.paused || this.videoPlayer_.videoElem_.ended){
				this.videoPlayer_.videoElem_.play();
			} else {
				this.videoPlayer_.videoElem_.pause();
			}
		}
};

mirosubs.subtitle.MainPanel.prototype.createDom = function() {
    mirosubs.subtitle.MainPanel.superClass_.createDom.call(this);

    var that = this;
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    el.appendChild(this.contentElem_ = $d('div'));
    el.appendChild($d('div', { 'className': 'mirosubs-nextStep' },
                      this.nextMessageSpan_ = $d('span'),
                      this.nextStepLink_ = $d('a', { 'href': '#'})));
    this.getHandler().listen(this.nextStepLink_, 'click', 
                             this.nextStepClicked_, false, this);
    this.tabs_ = this.createTabElems_()
    el.appendChild($d('ul', { 'className' : 'mirosubs-nav' }, this.tabs_));
    this.setState_(0);
    this.keyHandler_ = new goog.events.KeyHandler(document);
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_);
};

mirosubs.subtitle.MainPanel.prototype.setNextStepText = 
    function(messageText, buttonText) {
    var $c = goog.dom.setTextContent;
    $c(this.nextMessageSpan_, messageText);
    $c(this.nextStepLink_, buttonText);
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
    if (this.showingInterPanel_ || state == 0) {
        this.showingInterPanel_ = false;
        this.disposeCurrentWidget_();
        if (state < 3) {
            this.removeChildren(true);
            this.state_ = state;
            this.videoPlayer_.setPlayheadTime(0);
            this.selectTab_(state);
            this.addChild(this.makeNextWidget_(state), true);
            this.setNextStepText("When you're done, click here", "Next Step");
        }
        else
            this.finishEditing_();
    }
    else {
        this.removeChildren(true);
        this.showingInterPanel_ = true;
        this.addChild(this.makeInterPanel_(state), true);
        if (state == 3)
            this.setNextStepText("Click close to finish", "Close");
    }
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
            this.captions_, this.unitOfWork_);
    else if (state == 1)
        this.currentWidget_ = new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.captionManager_);
    else if (state == 2)
        this.currentWidget_ = new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.captionManager_);    
    return this.currentWidget_;
};

mirosubs.subtitle.MainPanel.prototype.makeInterPanel_ = function(state) {
    if (state < 3)
        return new mirosubs.subtitle.InterPanel("Great job, carry on!");
    else
        return new mirosubs.subtitle
            .InterPanel("Thank you, click close to end the session",
                        "finished");
};

mirosubs.subtitle.MainPanel.prototype.finishEditing_ = function() {
    var that = this;
    // TODO: show loading
    this.serverModel_.finish(function() {
            // TODO: hide loading.
            that.dispatchEvent(mirosubs.subtitle.MainPanel
                               .EventType.FINISHED);
            that.dispose();
        });
};

mirosubs.subtitle.MainPanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.MainPanel.superClass_.disposeInternal.call(this);
    this.disposeCurrentWidget_();
    this.serverModel_.dispose();
    this.captionManager_.dispose();
};

