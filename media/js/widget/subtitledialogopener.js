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

/**
 * Calls start_editing on server and then, if successful, opens the dialog.
 * @param {string} subLanguageCode The iso language code for subtitles.
 * @param {string=} opt_originalLanguageCode The iso language code for the video's
 *     original language. Should be null iff the video's original language is
 *     already set.
 * @param {number=} opt_subLanguagePK PK for the SubtitleLanguage to edit, 
 *     if any.
 * @param {number=} opt_baseLanguagePK PK for the SubtitleLanguage to use
 *     as base for dependent.
 */
mirosubs.widget.SubtitleDialogOpener.prototype.openDialog = function(
    subLanguageCode, 
    opt_originalLanguageCode, 
    opt_subLanguagePK,
    opt_baseLanguagePK,
    opt_completeCallback)
{
    this.showLoading_(true);
    var args = {
        'video_id': this.videoID_,
        'language_code': subLanguageCode,
        'subtitle_language_pk': opt_subLanguagePK || null,
        'base_language_pk': opt_baseLanguagePK || null,
        'original_language_code': opt_originalLanguageCode || null };
    var that = this;
    mirosubs.Rpc.call(
        'start_editing', args,
        function(result) {
            if (opt_completeCallback)
                opt_completeCallback();
            that.startEditingResponseHandler_(result);
        });
};

mirosubs.widget.SubtitleDialogOpener.prototype.showStartDialog = 
    function(opt_effectiveVideoURL) 
{
    var that = this;
    var dialog = new mirosubs.startdialog.Dialog(
        this.videoID_, null, 
        function(originalLanguage, subLanguage, subLanguageID, 
                 baseLanguageID, closeCallback) {
            that.openDialogOrRedirect_(
                subLanguage, originalLanguage, subLanguageID, 
                baseLanguageID, opt_effectiveVideoURL, 
                closeCallback);
        });
    dialog.setVisible(true);
};

mirosubs.widget.SubtitleDialogOpener.prototype.openDialogOrRedirect_ =
    function(subLanguageCode, 
             opt_originalLanguageCode, 
             opt_subLanguagePK,
             opt_baseLanguagePK, 
             opt_effectiveVideoURL,
             opt_completeCallback)
{
    if (mirosubs.DEBUG || !goog.userAgent.GECKO || mirosubs.returnURL)
        this.openDialog(
            subLanguageCode, 
            opt_originalLanguageCode,
            opt_subLanguagePK,
            opt_baseLanguagePK,
            opt_completeCallback);
    else {
        var config = {
            'videoID': this.videoID_,
            'videoURL': this.videoURL_,
            'effectiveVideoURL': opt_effectiveVideoURL || this.videoURL_,
            'languageCode': subLanguageCode,
            'originalLanguageCode': opt_originalLanguageCode || null,
            'subLanguagePK': opt_subLanguagePK || null,
            'baseLanguagePK': opt_baseLanguagePK || null
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

/**
 * @param {number} draftPK The draft saved with this primary key should 
 *     already be in forked state on the server.
 * @param {mirosubs.widget.SubtitleState} subtitles The subtitles should 
 *     include current timing information.
 */
mirosubs.widget.SubtitleDialogOpener.prototype.openForkedTranslationDialog = 
    function(draftPK, subtitles)
{
    var serverModel = new mirosubs.subtitle.MSServerModel(
        draftPK, this.videoID_, this.videoURL_);
    this.openSubtitlingDialog_(serverModel, subtitles);
};

mirosubs.widget.SubtitleDialogOpener.prototype.startEditingResponseHandler_ = 
    function(result)
{
    this.showLoading_(false);
    if (result['can_edit']) {
        var draftPK = result['draft_pk'];
        subtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['subtitles']);
        originalSubtitles = mirosubs.widget.SubtitleState.fromJSON(
            result['original_subtitles']);
        var serverModel = new mirosubs.subtitle.MSServerModel(
            draftPK, this.videoID_, this.videoURL_);
        if (subtitles.IS_ORIGINAL || subtitles.FORKED)
            this.openSubtitlingDialog_(serverModel, subtitles);
        else
            this.openDependentTranslationDialog_(
                serverModel, subtitles, originalSubtitles);
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

mirosubs.widget.SubtitleDialogOpener.prototype.openSubtitlingDialog_ = 
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
