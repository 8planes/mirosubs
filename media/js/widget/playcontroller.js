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

goog.provide('mirosubs.widget.PlayController');

/**
 * @constructor
 * 
 */
mirosubs.widget.PlayController = function(
    videoSource, videoPlayer, videoTab, dropDown, opt_subtitleState) 
{
    goog.Disposable.call(this);
    this.videoSource_ = videoSource;
    this.videoPlayer_ = videoPlayer;
    this.videoTab_ = videoTab;
    this.dropDown_ = dropDown;
    if (opt_subtitleState)
        this.setUpSubs_(opt_subtitleState);
};
goog.inherits(mirosubs.widget.PlayController, goog.Disposable);

mirosubs.widget.PlayController.prototype.stopForDialog = function() {
    this.videoPlayer_.stopLoading();
    this.turnOffSubs_();
};

mirosubs.widget.PlayController.prototype.turnOffSubs_ = function() {
    this.dropDown_.setShowingSubs(false);
    this.dropDown_.hide();
    this.videoTab_.showNudge(false);
    this.disposeComponents_();
    this.subtitleState_ = null;
    // TODO: set the video tab text here also.
};

/**
 * Returns a non-null value if and only if subs are not turned off for the 
 * the video right now.
 */
mirosubs.widget.PlayController.prototype.getSubtitleState = function() {
    return this.subtitleState_;
};

mirosubs.widget.PlayController.prototype.getVideoSource = function() {
    return this.videoSource_;
};

mirosubs.widget.PlayController.prototype.setUpSubs_ = 
    function(subtitleState) 
{
    this.disposeComponents_();
    this.subtitleState_ = subtitleState;
    var captionSet = new mirosubs.subtitle.EditableCaptionSet(
        subtitleState.SUBTITLES);
    this.captionManager_ = 
        new mirosubs.CaptionManager(this.videoPlayer_, captionSet);
    this.handler_ = new goog.events.EventHandler(this);
    this.handler_.
        listen(this.captionManager_,
               mirosubs.CaptionManager.CAPTION,
               this.captionReached_).
        listen(this.captionManager_,
               mirosubs.CaptionManager.CAPTIONS_FINISHED,
               this.finished_).
        listen(this.videoPlayer_,
               mirosubs.video.AbstractVideoPlayer.EventType.PLAY_ENDED,
               this.finished_);
    this.videoTab_.setText(
        subtitleState.LANGUAGE ? 
            mirosubs.languageNameForCode(subtitleState.LANGUAGE) :
            "Original Language");
};

mirosubs.widget.PlayController.prototype.captionReached_ = function() {
    var c = event.caption;
    this.videoPlayer_.showCaptionText(c ? c.getText() : '');
};

mirosubs.widget.PlayController.prototype.finished_ = function() {
    
};

mirosubs.widget.PlayController.prototype.disposeComponents_ = function() {
    if (this.captionManager_) {
        this.captionManager_.dispose();
        this.captionManager_ = null;
    }
    if (this.handler_) {
        this.handler_.dispose();
        this.handler_ = null;
    }
};

mirosubs.widget.PlayController.prototype.disposeInternal = function() {
    mirosubs.widget.PlayController.superClass_.disposeInternal.call(this);
    this.disposeComponents_();
};