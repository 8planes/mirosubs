goog.provide('mirosubs.subtitle.MainPanel');

/**
 * @fileoverview In this class, the three states {0, 1, 2} correspond to 
 *     { transcribe, sync, review }.
 */

/**
 * 
 * 
 * @param {int} editVersion The caption version we're editing.
 * @param {Array.<Object.<string, *>>} existingCaptions existing captions in 
 *     json object format.
 */
mirosubs.subtitle.MainPanel = function(videoPlayer, 
                                       videoID, 
                                       editVersion, 
                                       existingCaptions) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    this.videoID_ = videoID;
    var uw = this.unitOfWork_ = new mirosubs.UnitOfWork();
    this.editVersion_ = editVersion;
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
    this.saveManager_ = this.createSaveManager_(videoID, editVersion, uw);
    this.lockManager_ = new mirosubs.subtitle.LockManager(
        'update_video_lock', { 'video_id' : videoID });
    this.tabs_ = [];
};
goog.inherits(mirosubs.subtitle.MainPanel, goog.ui.Component);

mirosubs.subtitle.MainPanel.prototype.createSaveManager_ = 
    function(videoID, editVersion, unitOfWork) {
    var toJsonCaptions = function(arr) {
        return goog.array.map(arr, function(editableCaption) {
                return editableCaption.jsonCaption;
            });
    };
    return new mirosubs.subtitle.SaveManager(
        unitOfWork, "save_captions", function(work) {
            return {
                "video_id" : videoID,
                "version_no" : editVersion,
                "deleted" : toJsonCaptions(work.deleted),
                "inserted" : toJsonCaptions(work.neu),
                "updated" : toJsonCaptions(work.updated)
            };
        });
};

mirosubs.subtitle.MainPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.subtitle.MainPanel.prototype.enterDocument = function() {
    mirosubs.subtitle.MainPanel.superClass_.enterDocument.call(this);

    var that = this;
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    el.appendChild(this.contentElem_ = $d('div'));
    el.appendChild($d('div', { 'class': 'MiroSubs-nextStep' },
                      this.nextMessageSpan_ = $d('span'),
                      this.nextStepLink_ = $d('a', { 'href': '#'})));
    this.getHandler().listen(this.nextStepLink_, 'click', 
                             function(event) {
                                 that.setState_(that.state_ + 1);
                                 event.preventDefault();
                             });
    this.tabs_ = this.createTabElems_()
    el.appendChild($d('ul', { 'class' : 'MiroSubs-nav' }, this.tabs_));

    this.addChild(this.subtitleMain_ = new goog.ui.Component(), true);
    this.setState_(0);
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
                                        {'class': 'MiroSubs-nav' + label}, 
                                        a);
                          });
};
mirosubs.subtitle.MainPanel.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.videoPlayer_.showCaptionText(c ? c['caption_text'] : '');
};
mirosubs.subtitle.MainPanel.prototype.setState_ = function(state) {
    var nextWidget;
    if (state == 0)
        nextWidget = new mirosubs.subtitle.TranscribePanel(
            this.captions_, this.unitOfWork_);
    else if (state == 1)
        nextWidget = new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.captionManager_);
    else if (state == 2)
        nextWidget = new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.videoPlayer_.getPlayheadFn(), 
            this.captionManager_);
    this.showInterPanel_(state, nextWidget);
};

mirosubs.subtitle.MainPanel.prototype.showInterPanel_ = function(state, nextWidget) {
    var that = this;
    var finishFn = function() {
        that.subtitleMain_.removeChildren();
        if (that.currentWidget_ != null)
            that.currentWidget_.dispose();
        if (state < 3) {
            that.videoPlayer_.setPlayheadTime(0);
            var c = goog.dom.classes;
            for (var i = 0; i < that.tabs_.length; i++) {
                if (i == state)
                    c.add(that.tabs_[i], 'active');
                else
                    c.remove(that.tabs_[i], 'active');
            }
            that.currentWidget_ = nextWidget;
            that.subtitleMain_.addChild(that.currentWidget_, true);
            that.state_ = state;
        }
        else
            that.finishEditing_();
    };
    finishFn();
};

mirosubs.subtitle.MainPanel.prototype.finishEditing_ = function() {
    var that = this;
    var loadingImg = goog.dom.$(this.uuid_ + "_finishedLoading");
    loadingImg.style.display = '';
    this.saveManager_.saveNow(function() {
            mirosubs.Rpc.call("finished_captions", {
                    "video_id" : that.videoID_
                }, function() {
                    loadingImg.style.display = 'none';
                    that.dispatchEvent(mirosubs.subtitle.MainPanel
                                       .EventType.FINISHED_EDITING);
                    that.dispose();
                });
        });
};

mirosubs.subtitle.MainPanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.MainPanel.superClass_.disposeInternal.call(this);
    this.saveManager_.dispose();
    this.lockManager_.dispose();
    this.captionManager_.dispose();
};