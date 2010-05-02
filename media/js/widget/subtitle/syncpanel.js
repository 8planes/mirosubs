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
 * @param {mirosubs.subtitle.EditableCaptionSet} subtitles The subtitles 
 *     for the video, so far.
 * @param {mirosubs.AbstractVideoPlayer} videoPlayer
 * @param {mirosubs.CaptionManager} Caption manager, already containing subtitles 
 *     with start_time set.
 */
mirosubs.subtitle.SyncPanel = function(subtitles, videoPlayer, 
                                       serverModel, captionManager) {
    goog.ui.Component.call(this);
    /**
     * @type {mirosubs.subtitle.EditableCaptionSet}
     */ 
    this.subtitles_ = subtitles;

    this.videoPlayer_ = videoPlayer;
    /**
     * @protected
     */
    this.serverModel = serverModel;
    this.captionManager_ = captionManager;
    this.videoStarted_ = false;
    this.spaceDownSub_ = null;
    this.spaceDownPlayheadTime_ = -1;
    this.spaceDown_ = false;
    this.focusableElem_ = null;
};
goog.inherits(mirosubs.subtitle.SyncPanel, goog.ui.Component);

mirosubs.subtitle.SyncPanel.prototype.enterDocument = function() {
    mirosubs.subtitle.SyncPanel.superClass_.enterDocument.call(this);
    var handler = this.getHandler();
    handler.listen(this.captionManager_,
                   mirosubs.CaptionManager.EventType.CAPTION,
                   this.captionReached_);    
    handler.listen(document,
                   goog.events.EventType.KEYDOWN,
                   this.handleKeyDown_);
    handler.listen(document,
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
        this.videoPlayer_, this.subtitles_, true), true);
    this.subtitleList_.setTaller(true);
};
mirosubs.subtitle.SyncPanel.prototype.getRightPanel = function() {
    if (!this.rightPanel_) {
        this.rightPanel_ = this.createRightPanelInternal();
        this.focusableElem_ = this.rightPanel_.getDoneAnchor();
        this.getHandler().listen(this.rightPanel_, 
                                 mirosubs.RightPanel.EventType.LEGENDKEY,
                                 this.handleLegendKeyPress_);
        this.getHandler().listen(this.rightPanel_,
                                 mirosubs.RightPanel.EventType.RESTART,
                                 this.startOverClicked_);    
    }
    return this.rightPanel_;
};
mirosubs.subtitle.SyncPanel.prototype.createRightPanelInternal = function() {
    var helpContents = new mirosubs.RightPanel.HelpContents(
        "STEP 2: Syncing Subtitles",
        ["Congratulations, you finished the hard part (all that typing)!",
         ["Now, to line up your subtitles to the video, tap SPACEBAR right ", 
          "when each subtitle should appear."].join(''),
         "Tap spacebar to begin, tap it for the first subtitle, and so on.",
         ["Don't worry about small mistakes. We can correct them in the ", 
          "next step. If you need to start over, click \"restart\" ", 
          "below."].join('')],
        "Watch a how-to video on syncing",
        "http://youtube.com");
    return new mirosubs.RightPanel(
        this.serverModel, helpContents, 
        this.makeKeySpecsInternal(), true, "Done?", 
        "Next Step: Reviewing");
};
mirosubs.subtitle.SyncPanel.prototype.makeKeySpecsInternal = function() {
    var KC = goog.events.KeyCodes;
    return [
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-begin', 'mirosubs-spacebar', 'spacebar', 
            'Sync Next Subtitle', KC.SPACE),
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-play', 'mirosubs-tab', 'tab', 'Play/Pause', KC.TAB),
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-skip', 'mirosubs-control', 'control', 
            'Skip Back 8 Seconds', KC.CTRL)
    ];
    
};
mirosubs.subtitle.SyncPanel.prototype.handleLegendKeyPress_ = 
    function(event) 
{
    if (event.keyCode == goog.events.KeyCodes.SPACE) {
        if (event.keyEventType == goog.events.EventType.MOUSEDOWN &&
            !this.currentlyEditingSubtitle_())
            this.spacePressed_();
        else if (event.keyEventType == goog.events.EventType.MOUSEUP &&
                this.spaceDown_)
            this.spaceReleased_();
    }
};
mirosubs.subtitle.SyncPanel.prototype.handleKeyDown_ = function(event) {
    console.log('key down');
    if (event.keyCode == goog.events.KeyCodes.SPACE && 
        !this.currentlyEditingSubtitle_()) {
        event.preventDefault();
        this.spacePressed_();
    }
};
mirosubs.subtitle.SyncPanel.prototype.spacePressed_ = function() {
    if (this.videoPlayer_.isPlaying()) {
        if (this.spaceDown_)
            return;
        this.captionManager_.disableCaptionEvents(true);
        this.spaceDown_ = true;
        this.videoStarted_ = true;
        this.spaceDownPlayheadTime_ = 
            this.videoPlayer_.getPlayheadTime();
        this.spaceDownSub_ =
            this.subtitles_.findLastForTime(this.spaceDownPlayheadTime_);
    }
    else if (this.videoPlayer_.isPaused() && !this.videoStarted_) {
        this.videoPlayer_.play();
        this.videoStarted_ = true;
    }
};
mirosubs.subtitle.SyncPanel.prototype.handleKeyUp_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.SPACE && this.spaceDown_) {
        event.preventDefault();
        this.spaceReleased_();
    }
};
mirosubs.subtitle.SyncPanel.prototype.spaceReleased_ = function() {
    this.captionManager_.disableCaptionEvents(false);        
    this.spaceDown_ = false;
    var playheadTime = this.videoPlayer_.getPlayheadTime();

    if (this.spaceDownSub_ == null || 
        !this.spaceDownSub_.isShownAt(this.spaceDownPlayheadTime_)) {
        // pressed down before first sub or in between subs.
        var nextSub = null;
        if (this.spaceDownSub_ == null && this.subtitles_.count() > 0)
            nextSub = this.subtitles_.caption(0);
        if (this.spaceDownSub_)
            nextSub = this.spaceDownSub_.getNextCaption();
        if (nextSub != null)
            nextSub.setStartTime(playheadTime);
    }
    else if (this.spaceDownSub_.isShownAt(playheadTime) && 
             this.spaceDownSub_.getNextCaption()) 
        this.spaceDownSub_.getNextCaption().setStartTime(playheadTime);
    else
        this.spaceDownSub_.setEndTime(playheadTime);

    this.spaceDownSub_ = null;
    this.spaceDownPlayheadTime_ = -1;
};
mirosubs.subtitle.SyncPanel.prototype.startOverClicked_ = function() {
    var answer = 
        confirm("Are you sure you want to start over? All timestamps " +
                "will be deleted.");
    if (answer) {
        this.subtitles_.clearTimes();
        this.videoPlayer_.setPlayheadTime(0);
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
    if (this.rightPanel_)
        this.rightPanel_.dispose();
};