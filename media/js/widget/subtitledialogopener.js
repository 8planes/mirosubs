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

goog.provide('mirosubs.widget.SubtitleDialogOpener');

/**
 * @constructor
 * @param {string} videoID
 * @param {string} videoURL This is used for creating the embed code 
 *     that appears in the widget.
 * @param {mirosubs.video.VideoSource} videoSource
 * @param {function(boolean)=} opt_loadingFn
 * @param {function()=} opt_subOpenFn
 */
mirosubs.widget.SubtitleDialogOpener = function(
    videoID, videoURL, videoSource, opt_loadingFn, opt_subOpenFn)
{
    goog.events.EventTarget.call(this);
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.videoSource_ = videoSource;
    this.loadingFn_ = opt_loadingFn;
    this.subOpenFn_ = opt_subOpenFn;
};
goog.inherits(mirosubs.widget.SubtitleDialogOpener,
              goog.events.EventTarget);

mirosubs.widget.SubtitleDialogOpener.prototype.showLoading_ = 
    function(loading) 
{
    if (this.loadingFn_)
        this.loadingFn_(loading);
};

mirosubs.widget.SubtitleDialogOpener.prototype.getResumeEditingRecord_ = 
    function(openDialogArgs)
{
    var resumeEditingRecord = mirosubs.widget.ResumeEditingRecord.fetch();
    if (resumeEditingRecord && resumeEditingRecord.matches(
        this.videoID_, openDialogArgs))
        return resumeEditingRecord;
    else
        return null;
};

mirosubs.widget.SubtitleDialogOpener.prototype.saveResumeEditingRecord_ = 
    function(sessionPK, openDialogArgs)
{
    var resumeEditingRecord = new mirosubs.widget.ResumeEditingRecord(
        this.videoID_, sessionPK, openDialogArgs);
    resumeEditingRecord.save();
};


/**
 * Calls start_editing on server and then, if successful, opens the dialog.
 * @param {mirosubs.widget.OpenDialogArgs} openDialogArgs
 * @param {function()=} opt_completeCallback
 */
mirosubs.widget.SubtitleDialogOpener.prototype.openDialog = function(
    openDialogArgs,
    opt_completeCallback)
{
    if (this.disallow_()) {
        return;
    }
    var that = this;
    this.showLoading_(true);
    var resumeEditingRecord = this.getResumeEditingRecord_(openDialogArgs);
    if (resumeEditingRecord && resumeEditingRecord.getSavedSubtitles()) {
        this.resumeEditing_(
            resumeEditingRecord.getSavedSubtitles(),
            openDialogArgs,
            opt_completeCallback);
    }
    else {
        this.startEditing_(openDialogArgs, opt_completeCallback);
    }
};

mirosubs.widget.SubtitleDialogOpener.prototype.startEditing_ = 
    function(openDialogArgs,
             opt_completeCallback) 
{
    var args = {
        'video_id': this.videoID_,
        'language_code': openDialogArgs.LANGUAGE,
        'subtitle_language_pk': openDialogArgs.SUBLANGUAGE_PK || null,
        'base_language_pk': openDialogArgs.BASELANGUAGE_PK || null,
        'original_language_code': openDialogArgs.ORIGINAL_LANGUAGE || null };
    var that = this;
    mirosubs.Rpc.call(
        'start_editing', args,
        function(result) {
            that.saveResumeEditingRecord_(
                result['session_pk'], openDialogArgs);
            if (opt_completeCallback)
                opt_completeCallback();
            that.startEditingResponseHandler_(result, false);
        });
};

mirosubs.widget.SubtitleDialogOpener.prototype.resumeEditing_ = 
    function(savedSubtitles,
             openDialogArgs,
             opt_completeCallback) 
{
    var that = this;
    mirosubs.Rpc.call(
        'resume_editing', 
        { 'session_pk': savedSubtitles.SESSION_PK },
        function(result) {
            if (result['response'] == 'ok') {
                result['subtitles']['subtitles'] = 
                    savedSubtitles.CAPTION_SET.makeJsonSubs();
                that.startEditingResponseHandler_(result, true);
            }
            else {
                // someone else stepped in front of us.
                // TODO: should we show a message here?
                that.removeResumeEditingRecord_();
                that.startEditing_(openDialogArgs,
                                   opt_completeCallback);
            }
        });
};

mirosubs.widget.SubtitleDialogOpener.prototype.showStartDialog = 
    function(opt_effectiveVideoURL, opt_lang) 
{
    if (this.disallow_()) {
        return;
    }
    var that = this;
    var dialog = new mirosubs.startdialog.Dialog(
        this.videoID_, opt_lang, 
        function(originalLanguage, subLanguage, subLanguageID, 
                 baseLanguageID, closeCallback) {
            that.openDialogOrRedirect(
                new mirosubs.widget.OpenDialogArgs(
                    subLanguage, originalLanguage, subLanguageID, 
                    baseLanguageID), 
                opt_effectiveVideoURL, 
                closeCallback);
        });
    dialog.setVisible(true);
};

mirosubs.widget.SubtitleDialogOpener.prototype.disallow_ = function() {
    if (!mirosubs.supportsLocalStorage()) {
        alert("Sorry, you'll need to upgrade your browser to use the subtitling dialog.");
        return true;
    }
    else {
        return false;
    }
};

mirosubs.widget.SubtitleDialogOpener.prototype.openDialogOrRedirect =
    function(openDialogArgs, 
             opt_effectiveVideoURL,
             opt_completeCallback)
{
    if (this.disallow_()) {
        return;
    }
    if (mirosubs.returnURL)
        this.openDialog(openDialogArgs,
                        opt_completeCallback);
    else {
        var config = {
            'videoID': this.videoID_,
            'videoURL': this.videoURL_,
            'effectiveVideoURL': opt_effectiveVideoURL || this.videoURL_,
            'languageCode': openDialogArgs.LANGUAGE,
            'originalLanguageCode': openDialogArgs.ORIGINAL_LANGUAGE || null,
            'subLanguagePK': openDialogArgs.SUBLANGUAGE_PK || null,
            'baseLanguagePK': openDialogArgs.BASELANGUAGE_PK || null
        };
        if (mirosubs.IS_NULL)
            config['nullWidget'] = true;
        var uri = new goog.Uri(mirosubs.siteURL() + '/onsite_widget/');
        uri.setParameterValue(
            'config',
            goog.json.serialize(config));
        window.location.assign(uri.toString());
    }
}

mirosubs.widget.SubtitleDialogOpener.prototype.saveInitialSubs_ = function(sessionPK, editableCaptionSet) {
    var savedSubs = new mirosubs.widget.SavedSubtitles(
        sessionPK, editableCaptionSet);
    mirosubs.widget.SavedSubtitles.saveInitial(savedSubs);
};

mirosubs.widget.SubtitleDialogOpener.prototype.startEditingResponseHandler_ = 
    function(result, fromResuming)
{
    this.showLoading_(false);
    if (result['can_edit']) {
        var sessionPK = result['session_pk'];
        var subtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['subtitles']);
        var originalSubtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['original_subtitles']);
        var captionSet = new mirosubs.subtitle.EditableCaptionSet(
            subtitles.SUBTITLES, subtitles.IS_COMPLETE, subtitles.TITLE);
        if (!fromResuming) {
            this.saveInitialSubs_(sessionPK, captionSet);
        }
        var serverModel = new mirosubs.subtitle.MSServerModel(
            sessionPK, this.videoID_, this.videoURL_, captionSet);
        if (subtitles.IS_ORIGINAL || subtitles.FORKED)
            this.openSubtitlingDialog(serverModel, subtitles);
        else {
            this.openDependentTranslationDialog_(
                serverModel, subtitles, originalSubtitles);
        }
    }
    else {
        var username = 
            (result['locked_by'] == 
             'anonymous' ? 'Someone else' : ('The user ' + result['locked_by']));
        alert(username + ' is currently editing these subtitles. Please wait and try again later.');
        if (goog.isDefAndNotNull(mirosubs.returnURL))
            window.location.replace(mirosubs.returnURL);
    }
};

mirosubs.widget.SubtitleDialogOpener.prototype.openSubtitlingDialog = 
    function(serverModel, subtitleState) 
{
    if (this.subOpenFn_)
        this.subOpenFn_();
    var subDialog = new mirosubs.subtitle.Dialog(
        this.videoSource_,
        serverModel, subtitleState,
        this);
    subDialog.setParentEventTarget(this);
    subDialog.setVisible(true);
};

mirosubs.widget.SubtitleDialogOpener.prototype.openDependentTranslationDialog_ = 
    function(serverModel, subtitleState, originalSubtitleState)
{
    if (this.subOpenFn_)
        this.subOpenFn_();
    var transDialog = new mirosubs.translate.Dialog(
        this,
        serverModel,
        this.videoSource_,
        subtitleState, originalSubtitleState);
    transDialog.setParentEventTarget(this);
    transDialog.setVisible(true);
};
