goog.provide('mirosubs.subtitle.SyncPanel');

/**
 *
 * @param {Array.<mirosubs.subtitle.EditableCaption>} subtitles The subtitles 
 *     for the video, so far.
 * @param {Function} playheadFn Function that returns current playhead time for video.
 * @param {mirosubs.CaptionManager} Caption manager, already containing subtitles with 
 *     start_time set.
 */
mirosubs.subtitle.SyncPanel = function(subtitles, playheadFn, captionManager) {
    goog.ui.Component.call(this);
    /**
     * Always in correct order by time.
     * @type {Array.<mirosubs.subtitle.EditableCaption>}
     */ 
    this.subtitles_ = subtitles;

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
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    el.appendChild($d('div', {'class':'mirosubs-tips'},
                      $d('p', null, ['Tap spacebar to begin, and tap again ',
                                     'to align each subtitle.'].join('')),
                      $d('p', null, 'TAB = Play/Pause  CTRL = Skip Back')));
    el.appendChild(this.contentElem_ = $d('div'));
    this.addChild(this.subtitleList_ = 
                  new mirosubs.subtitle.SubtitleList(this.subtitles_), true);
    this.getHandler().listen(document,
                             goog.events.EventType.KEYDOWN,
                             this.handleKey_, false, this);
};
mirosubs.subtitle.SyncPanel.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE) {
        var playheadTime = this.playheadFn_();
        var lastSubtitle = null;
        var activeSubtitleWidget = this.subtitleList_.getActiveWidget();
        if (activeSubtitleWidget != null) {
            lastSubtitle = activeSubtitleWidget.getSubtitle();
            if (lastSubtitle.getStartTime() != -1)
                lastSubtitle.setEndTime(playheadTime);
        }
        // TODO: get rid of this linear search in the future by getting 
        // another map in instance state.
        var nextIndex = lastSubtitle == null ? 
            0 : goog.array.indexOf(this.subtitles_, lastSubtitle) + 1;
        if (nextIndex < this.subtitles_.length) {
            var currentSubtitle = this.subtitles_[nextIndex];
            var isInManager = currentSubtitle.getStartTime() != -1;
            currentSubtitle.setStartTime(playheadTime);
            currentSubtitle.setEndTime(99999);
            this.subtitleList_.updateWidget(currentSubtitle.getCaptionID());
            if (!isInManager)
                this.captionManager_.addCaptions([currentSubtitle.jsonCaption]);
        }
    }
};
mirosubs.subtitle.SyncPanel.prototype.captionReached_ = function(jsonCaptionEvent) {
    var jsonCaption = jsonCaptionEvent.caption;
    this.subtitleList_.clearActiveWidget();
    if (jsonCaption != null)
        this.subtitleList_.setActiveWidget(jsonCaption['caption_id']);
};
mirosubs.subtitle.SyncPanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.SyncPanel.superClass_.disposeInternal.call(this);
    if (this.keyHandler_)
        this.keyHandler_.dispose();
};