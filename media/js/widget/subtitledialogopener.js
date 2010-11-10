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
 * @param {string} videoURL
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

mirosubs.widget.SubtitleDialogOpener.prototype.openDialog = function(
    baseVersionNo, subLanguageCode, originalLanguageCode, fork)
{
    this.showLoading_(true);
    mirosubs.Rpc.call(
        'start_editing', 
        {'video_id': this.videoID_,
         'language_code': subLanguageCode,
         'original_language_code': originalLanguageCode,
         'base_version_no': baseVersionNo,
         'fork': fork},
        goog.bind(this.startEditingResponseHandler_, this));
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
        if (!subtitles.LANGUAGE || subtitles.FORKED)
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
    }
};

mirosubs.widget.SubtitleController.prototype.openSubtitlingDialog_ = 
    function(serverModel, subtitleState) 
{
    if (this.subOpenFn_)
        this.subOpenFn_();
    var subDialog = new mirosubs.subtitle.Dialog(
        this.videoSource_,
        serverModel, subtitleState.SUBTITLES);
    subDialog.setParentEventTarget(this);
    subDialog.setVisible(true);
};

mirosubs.widget.SubtitleController.prototype.openDependentTranslationDialog_ = 
    function(serverModel, subtitleState, originalSubtitleState)
{
    if (this.subOpenFn_)
        this.subOpenFn_();
    var transDialog = new mirosubs.translate.Dialog(
        serverModel,
        this.videoSource_,
        subtitleState, originalSubtitleState);
    transDialog.setParentEventTarget(this);
    transDialog.setVisible(true);
};
