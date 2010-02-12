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
    this.lastActiveSubtitleWidget_ = null;
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
                  new mirosubs.subtitle.SubtitleList(this.subtitles_, true), true);
    this.getHandler().listen(document,
                             goog.events.EventType.KEYDOWN,
                             this.handleKey_, false, this);
};
mirosubs.subtitle.SyncPanel.prototype.findSubtitleIndex_ = function(playheadTime) {
    var i;
    // TODO: write unit test then get rid of linear search in future.
    for (i = 0; i < this.subtitles_.length; i++)
        if (this.subtitles_[i].getStartTime() != -1 &&
            this.subtitles_[i].getStartTime() <= playheadTime &&
            (i == this.subtitles_.length - 1 ||
             this.subtitles_[i + 1].getStartTime() == -1 ||
             this.subtitles_[i + 1].getStartTime() > playheadTime))
            return i;
    return -1;
};
mirosubs.subtitle.SyncPanel.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE) {
        var playheadTime = this.playheadFn_();
        var currentSubIndex = this.findSubtitleIndex_(playheadTime);
        if (currentSubIndex > -1) {
            var currentSubtitle = this.subtitles_[currentSubIndex];
            if (currentSubtitle.getStartTime() != -1)
                currentSubtitle.setEndTime(playheadTime);
        }
        var nextSubIndex = currentSubIndex + 1;
        if (nextSubIndex < this.subtitles_.length) {
            var nextSubtitle = this.subtitles_[nextSubIndex];
            var isInManager = nextSubtitle.getStartTime() != -1;
            nextSubtitle.setStartTime(playheadTime);
            if (nextSubtitle.getEndTime() == -1)
                nextSubtitle.setEndTime(99999);
            this.subtitleList_.updateWidget(nextSubtitle.getCaptionID());
            if (!isInManager)
                this.captionManager_.addCaptions([nextSubtitle.jsonCaption]);
        }
        event.preventDefault();
    }
};
mirosubs.subtitle.SyncPanel.prototype.captionReached_ = function(jsonCaptionEvent) {
    console.log("captionReached");
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
