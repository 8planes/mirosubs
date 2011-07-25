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

goog.provide('mirosubs.widget.SubtitleController');

/**
 * @constructor
 */
mirosubs.widget.SubtitleController = function(
    videoID, videoURL, playController, videoTab, dropDown) 
{
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.videoTab_ = videoTab;
    this.dropDown_ = dropDown;
    this.playController_ = playController;
    this.playController_.setSubtitleController(this);
    this.handler_ = new goog.events.EventHandler(this);
    this.dialogOpener_ = new mirosubs.widget.SubtitleDialogOpener(
        videoID, videoURL, this.playController_.getVideoSource(),
        function(loading) {
            if (loading)
                videoTab.showLoading();
            else
                videoTab.stopLoading();
        },
        goog.bind(playController.stopForDialog, playController));

    /**
     * Show a request subtitles button as a nudge.
     * It will get overwritten by the Improve Subtitles button.
     */
    this.videoTab_.updateNudge(
        'Request Subtitles',
        goog.bind(this.openRequestSubtitlesDialog,
                  this));
    this.videoTab_.showNudge(true);

    this.handler_.listenOnce(
        this.dialogOpener_,
        goog.ui.Dialog.EventType.AFTER_HIDE,
        this.subtitleDialogClosed_);
    var s = mirosubs.widget.DropDown.Selection;
    this.handler_.
        listen(
            dropDown,
            s.ADD_LANGUAGE,
            this.openNewLanguageDialog).
        listen(
            dropDown,
            s.IMPROVE_SUBTITLES,
            this.improveSubtitles_).
       listen(
            dropDown,
            s.REQUEST_SUBTITLES,
            this.requestSubtitles_).
       listen(
            videoTab.getAnchorElem(), 'click',
            this.videoAnchorClicked_
        );
};

mirosubs.widget.SubtitleController.prototype.videoAnchorClicked_ = 
    function(e) 
{
    e.preventDefault();
    mirosubs.Tracker.getInstance().trackPageview('videoTabClicked');
    if (!this.dropDown_.hasSubtitles())
        this.openSubtitleDialog();
    else
        this.dropDown_.toggleShow();
};

mirosubs.widget.SubtitleController.prototype.improveSubtitles_ = function() {
    var state  = this.playController_.getSubtitleState();
    this.dialogOpener_.openDialogOrRedirect(
        new mirosubs.widget.OpenDialogArgs(
            state.LANGUAGE,
            null,
            state.LANGUAGE_PK,
            state.BASE_LANGUAGE_PK));
};

/**
 * Corresponds to "request subtitles" in menu.
 */
mirosubs.widget.SubtitleController.prototype.requestSubtitles_ = function() {
    this.openRequestSubtitlesDialog();
};

/**
 * Corresponds to "add new subs" in menu.
 */
mirosubs.widget.SubtitleController.prototype.openSubtitleDialog = 
    function() 
{
    var state  = this.playController_.getSubtitleState();
    this.openNewLanguageDialog(state);
};

mirosubs.widget.SubtitleController.prototype.openNewLanguageDialog = 
    function(opt_langState) 
{
    this.dialogOpener_.showStartDialog(
        this.playController_.getVideoSource().getVideoURL(), opt_langState);
};

mirosubs.widget.SubtitleController.prototype.subtitleDialogClosed_ = function(e) {
    var dropDownContents = e.target.getDropDownContents();
    this.playController_.dialogClosed();
    this.videoTab_.showContent(
        this.dropDown_.hasSubtitles(),
        this.playController_.getSubtitleState());
    this.dropDown_.setCurrentSubtitleState(
        this.playController_.getSubtitleState());
    if (dropDownContents != null) {
        this.dropDown_.updateContents(dropDownContents);
    }
};

/**
 * Opens the request subtitles dialog.
 */
mirosubs.widget.SubtitleController.prototype.openRequestSubtitlesDialog = function()
{
    mirosubs.login();
    if (mirosubs.isLoginAttemptInProgress()) {
        //Logging in
        return;
    }
    else{
        // Create a new request Dialog
        var dialog = new mirosubs.RequestDialog(this.videoID_);
        dialog.setVisible(true);
    }
}
