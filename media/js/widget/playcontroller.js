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
    videoID, videoSource, videoPlayer, videoTab, dropDown, opt_subtitleState) 
{
    goog.Disposable.call(this);
    this.videoID_ = videoID;
    this.videoSource_ = videoSource;
    this.videoPlayer_ = videoPlayer;
    this.videoTab_ = videoTab;
    this.dropDown_ = dropDown;
    if (opt_subtitleState)
        this.setUpSubs_(opt_subtitleState);
    this.menuEventHandler_ = new goog.events.EventHandler(this);
    var that = this;
    this.menuEventHandler_.
        listen(this.dropDown_,
               mirosubs.widget.DropDown.Selection.LANGUAGE_SELECTED,
               function(e) {
                   that.languageSelected(e.videoLanguage);
               }).
        listen(this.dropDown_,
               mirosubs.widget.DropDown.Selection.SUBTITLES_OFF,
               this.turnOffSubs);
    this.subtitleController_ = null;
    /* @type {bool}
     * Flag to keep track if the nudge has been show, to avoid
     * the cost of many calls to a dom changing function
     */
    this.nudgeShown_ = false;
};
goog.inherits(mirosubs.widget.PlayController, goog.Disposable);

mirosubs.widget.PlayController.prototype.setSubtitleController =
    function(subController)
{
    this.subtitleController_ = subController;
};

mirosubs.widget.PlayController.prototype.stopForDialog = function() {
    this.videoPlayer_.stopLoading();
    this.turnOffSubs();
};

mirosubs.widget.PlayController.prototype.dialogClosed = function() {
    this.videoPlayer_.resumeLoading();
};

mirosubs.widget.PlayController.prototype.turnOffSubs = function() {
    this.dropDown_.setCurrentSubtitleState(null);
    this.dropDown_.hide();
    this.videoTab_.showNudge(false);
    this.disposeComponents_();
    this.videoPlayer_.showCaptionText('');
    this.subtitleState_ = null;
    this.videoTab_.showContent(this.dropDown_.hasSubtitles());
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
    this.nudgeShown_ = false;
    this.disposeComponents_();
    this.subtitleState_ = subtitleState;
    var captionSet = new mirosubs.subtitle.EditableCaptionSet(
        subtitleState.SUBTITLES);
    this.captionManager_ = 
        new mirosubs.CaptionManager(this.videoPlayer_, captionSet);
    this.playEventHandler_ = new goog.events.EventHandler(this);
    this.playEventHandler_.
        listen(this.captionManager_,
               mirosubs.CaptionManager.CAPTION,
               this.captionReached_).
        listen(this.captionManager_,
               mirosubs.CaptionManager.CAPTIONS_FINISHED,
               this.finished_).
        listen(this.videoPlayer_,
               mirosubs.video.AbstractVideoPlayer.EventType.PLAY_ENDED,
               this.finished_);
};

mirosubs.widget.PlayController.prototype.languageSelected = function(videoLanguage) {
    var that = this;
    mirosubs.Tracker.getInstance().track('Selects_language_from_widget_dropdown');
    this.videoTab_.showLoading();
    mirosubs.Rpc.call(
        'fetch_subtitles',
        { 'video_id': this.videoID_,
          'language_pk': videoLanguage.PK },
        function(subStateJSON) {
            that.turnOffSubs();
            var subState = mirosubs.widget.SubtitleState.fromJSON(subStateJSON);
            that.setUpSubs_(subState);
            that.videoTab_.showContent(
                that.dropDown_.hasSubtitles(), subState);
            that.dropDown_.setCurrentSubtitleState(subState);
        });
};

mirosubs.widget.PlayController.prototype.captionReached_ = function(event) {
    var c = event.caption;
    this.videoPlayer_.showCaptionText(c ? c.getText() : '');
};

mirosubs.widget.PlayController.prototype.finished_ = function() {
    if (this.nudgeShown_){
        return;
    }
    var message = !!this.subtitleState_.LANGUAGE ?
        "Improve this Translation" : "Improve these Subtitles";
    this.videoTab_.updateNudge(
        message, 
        goog.bind(this.subtitleController_.openSubtitleDialog,
                  this.subtitleController_));
    this.videoTab_.showNudge(true);
    this.nudgeShown_ = true;
};

mirosubs.widget.PlayController.prototype.disposeComponents_ = function() {
    if (this.captionManager_) {
        this.captionManager_.dispose();
        this.captionManager_ = null;
    }
    if (this.playEventHandler_) {
        this.playEventHandler_.dispose();
        this.playEventHandler_ = null;
    }
};

mirosubs.widget.PlayController.prototype.disposeInternal = function() {
    mirosubs.widget.PlayController.superClass_.disposeInternal.call(this);
    this.disposeComponents_();
};
