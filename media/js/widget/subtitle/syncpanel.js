goog.provide('mirosubs.subtitle.SyncPanel');

/**
 *
 * @param {Array.<mirosubs.subtitle.EditableCaption>} subtitles The subtitles 
 *     for the video, so far.
 * @param {mirosubs.AbstractVideoPlayer} videoPlayer
 * @param {mirosubs.CaptionManager} Caption manager, already containing subtitles with 
 *     start_time set.
 */
mirosubs.subtitle.SyncPanel = function(subtitles, videoPlayer, 
                                       captionManager, focusableElem) {
    goog.ui.Component.call(this);
    /**
     * Always in correct order by time.
     * @type {Array.<mirosubs.subtitle.EditableCaption>}
     */ 
    this.subtitles_ = subtitles;

    this.videoPlayer_ = videoPlayer;
    this.captionManager_ = captionManager;
    this.keyHandler_ = null;
    this.lastActiveSubtitleWidget_ = null;
    this.videoStarted_ = false;
    this.focusableElem_ = focusableElem;
};
goog.inherits(mirosubs.subtitle.SyncPanel, goog.ui.Component);
mirosubs.subtitle.SyncPanel.prototype.enterDocument = function() {
    mirosubs.subtitle.SyncPanel.superClass_.enterDocument.call(this);
    var handler = this.getHandler();
    handler.listen(this.captionManager_,
                   mirosubs.CaptionManager.EventType.CAPTION,
                   this.captionReached_);    
    handler.listen(window,
                   goog.events.EventType.KEYDOWN,
                   this.handleKey_);
    var that = this;
    handler.listen(this.videoPlayer_,
                   mirosubs.AbstractVideoPlayer.EventType.PLAY,
                   function(event) {
                       that.focusableElem_.focus();
                   });
};
mirosubs.subtitle.SyncPanel.prototype.createDom = function() {
    mirosubs.subtitle.SyncPanel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());    
    this.getElement().appendChild(this.contentElem_ = $d('div'));
    this.addChild(this.subtitleList_ = new mirosubs.subtitle.SubtitleList(
        this.subtitles_, true, this.createHelpDom($d)), true);
};
/**
 *
 * @protected
 */
mirosubs.subtitle.SyncPanel.prototype.createHelpDom = function($d) {
    var helpLines = [['To sync your subtitles to the video, tap SPACEBAR ',
                      'at the exact moment each subtitle should display. ', 
                      'It’s easy!'].join(''), 
                     ['To begin, tap SPACEBAR to play the video and tap it ',
                      'again when each subtitle should appear.'].join('')];
    return mirosubs.subtitle.SubtitleList.createHelpLi($d, helpLines, 
                                                       'Syncing Controls', 
                                                       true, 'BEGIN');
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
    if (event.keyCode == goog.events.KeyCodes.SPACE && 
        !this.currentlyEditingSubtitle_()) {
        if (this.videoPlayer_.isPlaying()) {
            this.videoStarted_ = true;
            var playheadTime = this.videoPlayer_.getPlayheadTime();
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
                this.subtitleList_.scrollToCaption(nextSubtitle.getCaptionID());
                if (!isInManager)
                    this.captionManager_.addCaptions([nextSubtitle.jsonCaption]);
            }
        }
        else if (this.videoPlayer_.isPaused() && !this.videoStarted_) {
            this.videoPlayer_.play();
            this.videoStarted_ = true;
        }
        event.stopPropagation();
        event.preventDefault();
    }
};
mirosubs.subtitle.SyncPanel.prototype.startOver = function() {
    var i;
    for (i = 0; i < this.subtitles_.length; i++) {
        this.subtitles_[i].setStartTime(-1);
        this.subtitles_[i].setEndTime(-1);
        this.subtitleList_.updateWidget(this.subtitles_[i].getCaptionID());
    }
};
mirosubs.subtitle.SyncPanel.prototype.currentlyEditingSubtitle_ = function() {
    return this.subtitleList_.isCurrentlyEditing();
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
