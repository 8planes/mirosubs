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

goog.provide('mirosubs.subtitle.Dialog');

/**
 * 
 * @param {mirosubs.subtitle.ServerModel} serverModel
 * @param {Array.<Object.<string, *>>} existingCaptions existing captions in 
 *     json object format.
 */
mirosubs.subtitle.Dialog = function(videoSource, serverModel, 
                                    existingCaptions) {
    mirosubs.Dialog.call(this, videoSource);
    this.serverModel_ = serverModel;
    var uw = this.unitOfWork_ = new mirosubs.UnitOfWork();
    /**
     * Array of captions.
     * @type {Array.<mirosubs.subtitle.EditableCaption>}
     */
    this.captions_ = goog.array.map(
        existingCaptions, function(caption) { 
            return new mirosubs.subtitle.EditableCaption(uw, caption);
        });
    this.captionManager_ = 
        new mirosubs.CaptionManager(goog.bind(this.getPlayheadTime_, this));
    this.captionManager_.addCaptions(existingCaptions);
    this.getHandler().listen(this.captionManager_,
                             mirosubs.CaptionManager.EventType.CAPTION,
                             this.captionReached_);
    this.serverModel_ = serverModel;
    this.serverModel_.init(uw, goog.bind(this.showLoginNag_, this));
    /**
     * @type {?boolean} True iff we pass into FINISHED state.
     */
    this.saved_ = false;
    this.state_ = null;
    this.currentSubtitlePanel_ = null;
    this.rightPanelListener_ = new goog.events.EventHandler(this);
    this.doneButtonEnabled_ = true;
};
goog.inherits(mirosubs.subtitle.Dialog, mirosubs.Dialog);

/**
 *
 * @enum
 */
mirosubs.subtitle.Dialog.State_ = {
    TRANSCRIBE: 0,
    SYNC: 1,
    REVIEW: 2,
    FINISHED: 3
};
mirosubs.subtitle.Dialog.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.getVideoPlayerInternal().showCaptionText(c ? c['caption_text'] : '');
};
mirosubs.subtitle.Dialog.prototype.createDom = function() {
   mirosubs.subtitle.Dialog.superClass_.createDom.call(this);
    this.setState_(mirosubs.subtitle.Dialog.State_.TRANSCRIBE);
};
mirosubs.subtitle.Dialog.prototype.enterDocument = function() {
    mirosubs.subtitle.Dialog.superClass_.enterDocument.call(this);
    this.getHandler().listen(document,
                             goog.events.EventType.KEYDOWN,
                             this.handleKeyDown_);
};
mirosubs.subtitle.Dialog.prototype.setState_ = function(state) {
    this.state_ = state;

    var nextSubPanel = this.makeCurrentStateSubtitlePanel_();
    var captionPanel = this.getCaptioningAreaInternal();
    captionPanel.removeChildren(true);
    captionPanel.addChild(nextSubPanel, true);

    var rightPanel = nextSubPanel.getRightPanel();
    this.setRightPanelInternal(rightPanel);

    this.disposeCurrentPanels_();
    this.currentSubtitlePanel_ = nextSubPanel;

    var et = mirosubs.RightPanel.EventType;
    this.rightPanelListener_.listen(
        rightPanel, et.LEGENDKEY, this.handleLegendKeyPress_);
    this.rightPanelListener_.listen(
        rightPanel, et.DONE, this.handleDoneKeyPress_);
    var s = mirosubs.subtitle.Dialog.State_;
    if (state == s.SYNC || state == s.REVIEW) {
        rightPanel.showBackLink(
            state == s.SYNC ? "Back to Transcribe" : "Back to Sync");
        this.rightPanelListener_.listen(
            rightPanel, et.BACK, this.handleBackKeyPress_);
    }

    var videoPlayer = this.getVideoPlayerInternal();
    if (this.isInDocument()) {
        videoPlayer.setPlayheadTime(0);
        videoPlayer.pause();
    }
};
mirosubs.subtitle.Dialog.prototype.setFinishedState_ = function() {
    this.saved_ = true;
    var sharePanel = new mirosubs.subtitle.SharePanel(
        this.serverModel_);
    this.setRightPanelInternal(sharePanel);
    this.getCaptioningAreaInternal().removeChildren(true);
    var bottomContainer = this.getBottomPanelContainerInternal();
    console.log(bottomContainer);
    var bottomFinishedPanel = new mirosubs.subtitle.BottomFinishedPanel();
    console.log(bottomFinishedPanel);
    bottomContainer.addChild(bottomFinishedPanel, true);
};
mirosubs.subtitle.Dialog.prototype.handleKeyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.CTRL)
        this.ctrlClicked_();
    if (event.keyCode == goog.events.KeyCodes.TAB) {
        //TODO: this violates accessibility guidelines. Use another key instead of TAB!
        this.togglePause_();
        event.preventDefault();
    }
};
mirosubs.subtitle.Dialog.prototype.handleBackKeyPress_ = function(event) {
    var s = mirosubs.subtitle.Dialog.State_;
    if (this.state_ == s.SYNC)
        this.setState_(s.TRANSCRIBE);
    else if (this.state_ == s.REVIEW)
        this.setState_(s.SYNC);    
};
mirosubs.subtitle.Dialog.prototype.handleLegendKeyPress_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.CTRL && 
        event.keyEventType == goog.events.EventType.CLICK)
        this.ctrlClicked_();
    if (event.keyCode == goog.events.KeyCodes.TAB &&
        event.keyEventType == goog.events.EventType.CLICK)
        this.togglePause_();
};
mirosubs.subtitle.Dialog.prototype.handleDoneKeyPress_ = function(event) {
    if (!this.doneButtonEnabled_)
        return;
    if (this.state_ == mirosubs.subtitle.Dialog.State_.REVIEW) {
        this.doneButtonEnabled_ = false;
        this.getRightPanelInternal().showLoading(true);
        var that = this;
        this.serverModel_.finish(function() {
            that.doneButtonEnabled_ = true;
            that.getRightPanelInternal().showLoading(false);
            that.setFinishedState_();
        });
    }
    else
        this.setState_(this.nextState_());
};
mirosubs.subtitle.Dialog.prototype.ctrlClicked_ = function() {
    var videoPlayer = this.getVideoPlayerInternal();
    var now = videoPlayer.getPlayheadTime();
    videoPlayer.setPlayheadTime(Math.max(now - 8, 0));
    videoPlayer.play();
};
mirosubs.subtitle.Dialog.prototype.togglePause_ = function() {
    this.getVideoPlayerInternal().togglePause();
};
mirosubs.subtitle.Dialog.prototype.makeCurrentStateSubtitlePanel_ = function() {
    var s = mirosubs.subtitle.Dialog.State_;
    if (this.state_ == s.TRANSCRIBE)
        return new mirosubs.subtitle.TranscribePanel(
            this.captions_, this.unitOfWork_, 
            this.getVideoPlayerInternal(),
            this.serverModel_, 
            this.captionManager_);
    else if (this.state_ == s.SYNC)
        return new mirosubs.subtitle.SyncPanel(
            this.captions_, 
            this.getVideoPlayerInternal(),
            this.serverModel_,
            this.captionManager_);
    else if (this.state_ == s.REVIEW)
        return new mirosubs.subtitle.ReviewPanel(
            this.captions_, 
            this.getVideoPlayerInternal(),
            this.serverModel_,
            this.captionManager_);
};
mirosubs.subtitle.Dialog.prototype.nextState_ = function() {
    var s = mirosubs.subtitle.Dialog.State_;
    if (this.state_ == s.TRANSCRIBE)
        return s.SYNC;
    else if (this.state_ == s.SYNC)
        return s.REVIEW;
    else if (this.state_ == s.REVIEW)
        return s.FINISHED;
};
mirosubs.subtitle.Dialog.prototype.getPlayheadTime_ = function() {
    var vp = this.getVideoPlayerInternal();
    return vp ? vp.getPlayheadTime() : 0;
};
mirosubs.subtitle.Dialog.prototype.showLoginNag_ = function() {
    // not doing anything here right now.
};
/**
 * Did we ever pass into finished state?
 */
mirosubs.subtitle.Dialog.prototype.isSaved = function() {
    return this.saved_;
};
mirosubs.subtitle.Dialog.prototype.disposeCurrentPanels_ = function() {
    if (this.currentSubtitlePanel_) {
        this.currentSubtitlePanel_.dispose();
        this.currentSubtitlePanel_ = null;
    }
    this.rightPanelListener_.removeAll();
};
mirosubs.subtitle.Dialog.prototype.disposeInternal = function() {
    mirosubs.subtitle.Dialog.superClass_.disposeInternal.call(this);
    this.disposeCurrentPanels_();
    this.captionManager_.dispose();
    this.serverModel_.dispose();
    this.rightPanelListener_.dispose();
};