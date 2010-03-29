// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

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
    this.videoStarted_ = false;
    this.focusableElem_ = focusableElem;
    this.spaceDownPlayheadTime_ = -1;
    this.spaceDownSubIndex_ = -1;
    this.spaceDown_ = false;
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
                   this.handleKeyDown_);
    handler.listen(window,
                   goog.events.EventType.KEYUP,
                   this.handleKeyUp_);
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
/**
 * Find the last subtitle with a start time at or before playheadTime.
 * @param {number} playheadTime
 * @return {number} -1 if before first sub start time, or index of last 
 *     subtitle with start time at or before playheadTime.
 */
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
mirosubs.subtitle.SyncPanel.prototype.handleKeyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE && 
        !this.currentlyEditingSubtitle_()) {
        event.preventDefault();
        if (this.videoPlayer_.isPlaying()) {
            if (this.spaceDown_)
                return;
            this.captionManager_.disableCaptionEvents(true);
            this.spaceDown_ = true;
            this.videoStarted_ = true;
            this.spaceDownPlayheadTime_ = 
                this.videoPlayer_.getPlayheadTime();
            this.spaceDownSubIndex_ =
                this.findSubtitleIndex_(this.spaceDownPlayheadTime_);
        }
        else if (this.videoPlayer_.isPaused() && !this.videoStarted_) {
            this.videoPlayer_.play();
            this.videoStarted_ = true;
        }
    }
};
mirosubs.subtitle.SyncPanel.prototype.handleKeyUp_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE && 
        this.spaceDown_) {
            this.captionManager_.disableCaptionEvents(false);        
        this.spaceDown_ = false;
        event.preventDefault();
        var playheadTime = this.videoPlayer_.getPlayheadTime();
        if (this.spaceDownSubIndex > -1 &&
            this.subtitles_[this.spaceDownSubIndex_].isShownAt(playheadTime))
            this.moveSubTimeForward();
        else {
            var currentSubIndex = this.findSubtitleIndex_(playheadTime);
            if (this.spaceDownSubIndex_ == currentSubIndex)
                this.moveSubTimeForward();
            else
                this.moveSubTimesBack(playheadTime, currentSubIndex);
        }
        this.spaceDownPlayheadTime_ = -1;
        this.spaceDownSubIndex_ = -1;
    }
};
mirosubs.subtitle.SyncPanel.prototype.moveSubTimeForward = function() {
    if (this.spaceDownSubIndex_ > -1) {
        var currentSubtitle = this.subtitles_[this.spaceDownSubIndex_];
        if (currentSubtitle.getStartTime() != -1)
            currentSubtitle.setEndTime(this.spaceDownPlayheadTime_);
    }
    var nextSubIndex = this.spaceDownSubIndex_ + 1;
    if (nextSubIndex < this.subtitles_.length) {
        var nextSubtitle = this.subtitles_[nextSubIndex];
        var isInManager = nextSubtitle.getStartTime() != -1;
        nextSubtitle.setStartTime(this.spaceDownPlayheadTime_);
        if (nextSubtitle.getEndTime() == -1)
            nextSubtitle.setEndTime(99999);
        this.subtitleList_.updateWidget(nextSubtitle.getCaptionID());
        this.subtitleList_.scrollToCaption(nextSubtitle.getCaptionID());
        if (!isInManager)
            this.captionManager_.addCaptions([nextSubtitle.jsonCaption]);
    }
};
mirosubs.subtitle.SyncPanel.prototype.moveSubTimesBack = 
    function(playheadTime, currentSubIndex) {
    var i;
    var subtitle = null;
    for (i = this.spaceDownSubIndex_; i <= currentSubIndex; i++) {
        if (i > -1) {
            subtitle = this.subtitles_[i];
            var isInManager = subtitle.getStartTime() != -1;
            if (subtitle.getStartTime() > this.spaceDownPlayheadTime_ &&
                subtitle.getStartTime() < playheadTime)
                subtitle.setStartTime(playheadTime);
            if (subtitle.getEndTime() > this.spaceDownPlayheadTime_ &&
                subtitle.getStartTime() < playheadTime)
                subtitle.setEndTime(playheadTime);
            this.subtitleList_.updateWidget(subtitle.getCaptionID());
            if (!isInManager)
                this.captionManager_.addCaptions([subtitle.jsonCaption]);
        }
    }
    if (subtitle != null) {
        this.subtitleList_.scrollToCaption(subtitle.getCaptionID());
        this.subtitleList_.setActiveWidget(subtitle.getCaptionID());
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
