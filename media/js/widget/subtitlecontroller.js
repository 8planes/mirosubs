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
    playController, videoTab, dropDown) 
{
    this.videoTab_ = videoTab;
    this.dropDown_ = dropDown;
    this.playController_ = playController;
    var m = mirosubs.widget.VideoTab.Messages;
    if (playController.getSubtitleState() == null)
        this.videoTab_.setText(
            this.dropDown_.getSubtitleCount() > 0 ? 
                m.CHOOSE_LANGUAGE : m.SUBTITLE_ME);
    this.handler_ = new goog.events.EventHandler(this);
    var s = mirosubs.widget.DropDown.Selection;
    this.handler_.
        listen(
            dropDown,
            s.ADD_TRANSLATION,
            this.openNewTranslationDialog).
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
    if (this.dropDown_.getSubtitleCount() == 0)
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
    var subtitleState = this.playController_.getSubtitleState();
    console.log(subtitleState.VERSION);
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
            this.possiblyRedirect_(false, this.subtitle_);
    }
    else
        this.possiblyRedirect_(false, this.subtitle_);
};

/**
 * Correponds to "Add new translation" in menu. Don't call this if there 
 * are no subtitles yet.
 */
mirosubs.widget.SubtitleController.prototype.openNewTranslationDialog = 
    function() 
{
    if (this.dropDown_.getSubtitleCount() == 0)
        throw new Error();
    var that = this;
    mirosubs.widget.ChooseLanguageDialog.show(
        false, true, true,
        function(language, forked) {
            that.startEditing_(null, language, forked);
        });
};

mirosubs.widget.SubtitleController.prototype.possiblyRedirect_ = 
    function(addNewTranslation, callback)
{
    if (mirosubs.DEBUG || !goog.userAgent.GECKO || mirosubs.returnURL)
        goog.bind(callback, this)();
    else {
        var uri = new goog.Uri(mirosubs.siteURL() + '/onsite_widget/');
        uri.setParameterValue('video_url', mirosubs.videoURL);
        if (mirosubs.IS_NULL)
            uri.setParameterValue('null_widget', 'true');
        if (addNewTranslation)
            uri.setParameter('translate_immediately', 'true');
        else
            uri.setParameter('subtitle_immediately', 'true');
        var subState = this.playController_.getSubtitleState();
        if (subState)
            uri.setParameter('base_state', subState.baseParams());
        uri.setParameter('return_url', window.location.href);
        window.location.assign(uri.toString());
    }
};

mirosubs.widget.SubtitleController.prototype.subtitle_ = function() {
    var that = this;
    if (this.dropDown_.getSubtitleCount() == 0)
        mirosubs.widget.ChooseLanguageDialog.show(
            true, true, false,
            function(language, forked) {
                that.startEditing_(null, language, true);
            });
    else {
        var subState = this.playController_.getSubtitleState();
        if (!subState || !subState.LANGUAGE)
            this.startEditing_(null, null, false);
        else if (subState && subState.FORKED)
            this.startEditing_(
                subState.VERSION, subState.LANGUAGE, true);
        else
            mirosubs.widget.ChooseLanguageDialog.show(
                false, false, true,
                function(language, forked) {
                    that.startEditing_(
                        subState.VERSION, subState.LANGUAGE, forked);
                });
    }
};

mirosubs.widget.SubtitleController.prototype.startEditing_ = 
        function(baseVersionNo, languageCode, fork) 
{
    this.videoTab_.showLoading(true);
    mirosubs.Rpc.call(
        'start_editing', 
        {'video_id': mirosubs.videoID,
         'language_code': languageCode,
         'base_version_no': baseVersionNo,
         'fork': fork},
        goog.bind(this.startEditingResponseHandler_, this));
};

mirosubs.widget.SubtitleController.prototype.startEditingResponseHandler_ =
    function(result)
{
    this.videoTab_.showLoading(false);
    if (result['can_edit']) {
        subtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['subtitles']);
        originalSubtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['original_subtitles']);
        if (!subtitles.LANGUAGE || subtitles.FORKED)
            this.openSubtitlingDialog_(subtitles);
        else
            this.openDependentTranslationDialog_(subtitles, originalSubtitles);
    }
    else {
        var username = 
            (result['locked_by'] == 
             'anonymous' ? 'Someone else' : ('The user ' + result['locked_by']));
        alert(username + ' is currently editing these subtitles. Please wait and try again later.');
    }
};

mirosubs.widget.SubtitleController.prototype.openSubtitlingDialog_ = 
    function(subtitleState) 
{
    this.playController_.stopForDialog();
    var subDialog = new mirosubs.subtitle.Dialog(
        this.playController_.getVideoSource(),
        new mirosubs.subtitle.MSServerModel(
            mirosubs.videoID, subtitleState.LANGUAGE),
        subtitleState.SUBTITLES);
    subDialog.setVisible(true);
    goog.events.listenOnce(
        subDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        this.subtitleDialogClosed_);
};

mirosubs.widget.SubtitleController.prototype.openDependentTranslationDialog_ = 
    function(subtitleState, originalSubtitleState)
{
    
};

mirosubs.widget.SubtitleController.prototype.subtitleDialogClosed_ = function(e) {
    
};