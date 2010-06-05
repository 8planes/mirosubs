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

goog.provide('mirosubs.subtitle.EditDialog');

/**
 * @fileoverview Used to edit existing subtitles. Has some duplication 
 *     with mirosubs.subtitle.Dialog, which should be fixed in the future.
 *     TODO: fix duplication with mirosubs.subtitle.Dialog after this 
 *     solidifies a bit more.
 */

mirosubs.subtitle.EditDialog = function(videoSource, serverModel, 
                                        existingCaptions) {
    mirosubs.Dialog.call(this, videoSource);
    this.serverModel_ = serverModel;
    var uw = this.unitOfWork_ = new mirosubs.UnitOfWork();
    this.captionSet_ = 
        new mirosubs.subtitle.EditableCaptionSet(existingCaptions, uw);
    this.captionManager_ = 
        new mirosubs.CaptionManager(
            this.getVideoPlayerInternal(), this.captionSet_);
    this.serverModel_ = serverModel;
    this.serverModel_.init(uw, function() {});
    
    this.state_ = null;
    this.currentSubtitlePanel_ = null;
    this.rightPanelListener_ = new goog.events.EventHandler(this);
    this.doneButtonEnabled_ = true;
};
goog.inherits(mirosubs.subtitle.EditDialog, mirosubs.Dialog);

mirosubs.subtitle.EditDialog.State_ = {
    EDIT: 0,
    TRANSCRIBE: 1,
    FINISHED: 2
};

mirosubs.subtitle.EditDialog.prototype.captionReached_ = function(event) {
    var c = event.caption;
    this.getVideoPlayerInternal().showCaptionText(c ? c.getText() : '');
};
mirosubs.subtitle.EditDialog.prototype.createDom = function() {
    mirosubs.subtitle.EditDialog.superClass_.createDom.call(this);
    this.setState_(mirosubs.subtitle.EditDialog.State_.EDIT);
};
mirosubs.subtitle.EditDialog.prototype.enterDocument = function() {
    mirosubs.subtitle.EditDialog.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(
            document,
            goog.events.EventType.KEYDOWN,
            this.handleKeyDown_).
        listen(
            this.captionManager_,
            mirosubs.CaptionManager.CAPTION,
            this.captionReached_);
};
mirosubs.subtitle.EditDialog.prototype.setState_ = function(state) {
    this.state_ = state;

    var nextSubPanel = this.makeCurrentStateSubtitlePanel_();
    var captionPanel = this.getCaptioningAreaInternal();
    captionPanel.removeChildren(true);
    captionPanel.addChild(nextSubPanel, true);

    var rightPanel = nextSubPanel.getRightPanel();
    this.setRightPanelInternal(rightPanel);

    this.getTimelinePanelInternal().removeChildren(true);

    this.disposeCurrentPanels_();
    this.currentSubtitlePanel_ = nextSubPanel;

    var et = mirosubs.RightPanel.EventType;
    this.rightPanelListener_.listen(
        rightPanel, et.LEGENDKEY, this.handleLegendKeyPress_);
    this.rightPanelListener_.listen(
        rightPanel, et.DONE, this.handleDoneKeyPress_);
    var s = mirosubs.subtitle.EditDialog.State_;
    if (state == s.EDIT) {
        rightPanel.showBackLink("Return to Transcribe");
        this.rightPanelListener_.listen(
            rightPanel, et.BACK, this.handleBackKeyPress_);
        this.timelineSubtitleSet_ =
            new mirosubs.timeline.SubtitleSet(
                this.captionSet_, this.getVideoPlayerInternal());
        this.getTimelinePanelInternal().addChild(
            new mirosubs.timeline.Timeline(
                1, this.timelineSubtitleSet_,
                this.getVideoPlayerInternal()), true);
    }
    var videoPlayer = this.getVideoPlayerInternal();
    if (this.isInDocument()) {
        videoPlayer.setPlayheadTime(0);
        videoPlayer.pause();
    }
};
mirosubs.subtitle.EditDialog.prototype.setFinishedState_ = function() {
    var sharePanel = new mirosubs.subtitle.SharePanel(
        this.serverModel_);
    this.setRightPanelInternal(sharePanel);
    this.getCaptioningAreaInternal().removeChildren(true);
    var bottomContainer = this.getBottomPanelContainerInternal();
    var bottomFinishedPanel = new mirosubs.subtitle.BottomFinishedPanel();
    bottomContainer.addChild(bottomFinishedPanel, true);
};
mirosubs.subtitle.EditDialog.prototype.handleKeyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.CTRL)
        this.ctrlClicked_();
    if (event.keyCode == goog.events.KeyCodes.TAB) {
        // TODO: this violates accessibility guidelines. 
        // Use another key instead of TAB!
        this.togglePause_();
        event.preventDefault();
    }
};
mirosubs.subtitle.EditDialog.prototype.handleBackKeyPress_ = function(event) {
    this.setState_(mirosubs.subtitle.EditDialog.State_.TRANSCRIBE);
};
mirosubs.subtitle.EditDialog.prototype.handleLegendKeyPress_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.CTRL && 
        event.keyEventType == goog.events.EventType.CLICK)
        this.ctrlClicked_();
    if (event.keyCode == goog.events.KeyCodes.TAB &&
        event.keyEventType == goog.events.EventType.CLICK)
        this.togglePause_();
};
mirosubs.subtitle.EditDialog.prototype.handleDoneKeyPress_ = function(event) {
    if (!this.doneButtonEnabled_)
        return;
    if (this.state_ == mirosubs.subtitle.EditDialog.State_.EDIT) {
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
mirosubs.subtitle.EditDialog.prototype.nextState_ = function() {
    var s = mirosubs.subtitle.EditDialog.State_;
    if (this.state_ == s.TRANSCRIBE)
        return s.EDIT;
    else if (this.state == s.EDIT)
        return s.FINISHED;
};
mirosubs.subtitle.EditDialog.prototype.ctrlClicked_ = function() {
    var videoPlayer = this.getVideoPlayerInternal();
    var now = videoPlayer.getPlayheadTime();
    videoPlayer.setPlayheadTime(Math.max(now - 8, 0));
    videoPlayer.play();
};
mirosubs.subtitle.EditDialog.prototype.togglePause_ = function() {
    this.getVideoPlayerInternal().togglePause();
};
mirosubs.subtitle.EditDialog.prototype.makeCurrentStateSubtitlePanel_ = 
    function() 
{
    var s = mirosubs.subtitle.EditDialog.State_;
    if (this.state_ == s.TRANSCRIBE)
        return new mirosubs.subtitle.TranscribePanel(
            this.captionSet_,
            this.getVideoPlayerInternal(),
            this.serverModel_);
    else if (this.state_ == s.EDIT)
        return new mirosubs.subtitle.EditPanel(
            this.captionSet_,
            this.getVideoPlayerInternal(),
            this.serverModel_,
            this.captionManager_);
};
mirosubs.subtitle.EditDialog.prototype.disposeCurrentPanels_ = function() {
    if (this.currentSubtitlePanel_) {
        this.currentSubtitlePanel_.dispose();
        this.currentSubtitlePanel_ = null;
    }
    this.rightPanelListener_.removeAll();
    if (this.timelineSubtitleSet_ != null) {
        this.timelineSubtitleSet_.dispose();
        this.timelineSubtitleSet_ = null;
    }
};
mirosubs.subtitle.EditDialog.prototype.disposeInternal = function() {
    mirosubs.subtitle.EditDialog.superClass_.disposeInternal.call(this);
    this.disposeCurrentPanels_();
    this.captionManager_.dispose();
    this.serverModel_.dispose();
    this.rightPanelListener_.dispose();
    this.captionSet_.dispose();
};