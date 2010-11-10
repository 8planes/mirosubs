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
            this.openSubtitleDialog).
        listen(
            videoTab.getAnchorElem(), 'click',
            this.videoAnchorClicked_
        );
};

mirosubs.widget.SubtitleController.prototype.videoAnchorClicked_ = 
    function(e) 
{
    if (!this.dropDown_.hasSubtitles())
        this.openSubtitleDialog();
    else
        this.dropDown_.toggleShow();
    e.preventDefault();
};

/**
 * Corresponds to "Add new subs" or "Improve these subs" in menu.
 */
mirosubs.widget.SubtitleController.prototype.openSubtitleDialog = 
    function() 
{
    var forNewSubs = !this.dropDown_.hasSubtitles();
    var subtitleState = this.playController_.getSubtitleState();
    if (subtitleState != null && 
        !subtitleState.IS_LATEST && 
        !mirosubs.returnURL) {
        var msg =
            ["You're about to edit revision ", 
             subtitleState.REVISION, ", an old revision. ",
             "Changes may have been made since this revision, and your edits ",
             "will override those changes. Are you sure you want to do this?"].
            join('');
        if (confirm(msg))
            this.subtitle_(forNewSubs);
    }
    else
        this.subtitle_(forNewSubs);
};

/**
 * Correponds to "Add new subtitles" in menu. Don't call this if there 
 * are no subtitles yet.
 */
mirosubs.widget.SubtitleController.prototype.openNewLanguageDialog = 
    function() 
{
    if (!this.dropDown_.hasSubtitles())
        throw new Error();
    if (this.dropDown_.getSubtitleCount() > 0)
        this.openNewTranslationDialog_();
    else
        this.subtitle_(true);
};

mirosubs.widget.SubtitleController.prototype.openNewTranslationDialog_ =
    function()
{
    var that = this;
    mirosubs.widget.ChooseLanguageDialog.show(
        true, function(subLanguage, originalLanguage, forked) {
            that.startEditing_(null, subLanguage, null, 
                               mirosubs.isForkedLanguage(subLanguage));
        });
};

/**
 *
 * @param {boolean} newLanguage
 */
mirosubs.widget.SubtitleController.prototype.subtitle_ = function(newLanguage) {
    var that = this;
    if (newLanguage)
        mirosubs.widget.ChooseLanguageDialog.show(
            false,
            function(subLanguage, originalLanguage, forked) {
                that.startEditing_(null, subLanguage, originalLanguage, true);
            });
    else {
        var subState = this.playController_.getSubtitleState();
        if (!subState || !subState.LANGUAGE)
            this.startEditing_(null, null, null, false);
        else {
            version = subState.IS_LATEST ? null : subState.VERSION
            this.startEditing_(
                version, subState.LANGUAGE, null,
                subState.FORKED)
        }
    }
};

mirosubs.widget.SubtitleController.prototype.startEditing_ = 
    function(baseVersionNo, subLanguageCode, originalLanguageCode, fork) 
{
    if (mirosubs.DEBUG || !goog.userAgent.GECKO || mirosubs.returnURL)
        this.dialogOpener_.openDialog(
            baseVersionNo, subLanguageCode, 
            originalLanguageCode, fork);
    else {
        var config = {
            'returnURL': window.location.href,
            'videoID': this.videoID_,
            'baseVersionNo': baseVersionNo,
            'videoURL': this.videoURL_,
            'effectiveVideoUrl': 
                this.playController_.getVideoSource().getVideoURL(),
            'languageCode': subLanguageCode,
            'originalLanguageCode': originalLanguageCode,
            'fork': fork
        };
        if (mirosubs.IS_NULL)
            config['nullWidget'] = true;
        var uri = new goog.Uri(mirosubs.siteURL() + '/onsite_widget/');
        uri.setParameterValue(
            'config',
            goog.json.serialize(config));
        window.location.assign(uri.toString());
    }
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