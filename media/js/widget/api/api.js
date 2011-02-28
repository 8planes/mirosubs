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

goog.provide('mirosubs.api');

/**
 * Opens the subtitling dialog for clients which provide their 
 * own server model, e.g. Wikimedia.
 * @param {Object} config Defined in the API documentation.
 */
mirosubs.api.openDialog = function(config) {
    mirosubs.siteConfig = mirosubs.Config.siteConfig;
    if (config['mediaURL'])
        mirosubs.Config.siteConfig['mediaURL'] = config['mediaURL'];
    var subtitles = config['subtitles'];
    var closeListener = config['closeListener'];
    var videoURL = config['videoURL'];
    var videoSource = new mirosubs.video.Html5VideoSource(
        videoURL, mirosubs.video.Html5VideoType.OGG);
    var serverModel = new mirosubs.api.ServerModel(config);
    var subDialog = new mirosubs.subtitle.Dialog(
        videoSource, serverModel, subtitles, 
        null,
        config['skipFinished']);
    mirosubs.currentUsername = config['username'];
    subDialog.setVisible(true);
    goog.events.listenOnce(
        subDialog,
        goog.ui.Dialog.EventType.AFTER_HIDE,
        closeListener);
    return {
        "close": function() { subDialog.setVisible(false); }
    };
};

/**
 * Used to open the dialog from the on-site widget page for Firefox bug. In this
 * case, general settings can be passed in from the page, so we don't bother
 * asking the server for them.
 * In near future, will also use this to open dialog for team actions.
 * @param {boolean} askLanguage Should we ask the user for the language first?
 * @param {Object} config Arguments for the dialog: videoURL to be used 
 *     in embed code, video url for the video player, version no, language 
 *     code, original language code if set, and fork. These are currently 
 *     set in SubtitleController#startEditing_.
 * @param {Object} generalSettings See WidgetController.makeGeneralSettings
 *     for more info.
 */ 
mirosubs.api.openUnisubsDialogWithSettings = function(askLanguage, config, generalSettings) {
    mirosubs.widget.WidgetController.makeGeneralSettings(generalSettings);
    if (config['returnURL'])
        mirosubs.returnURL = config['returnURL'];
    mirosubs.IS_NULL = !!config['nullWidget'];
    var videoSource = 
        mirosubs.video.VideoSource.videoSourceForURL(
            config['effectiveVideoURL']);
    var opener = new mirosubs.widget.SubtitleDialogOpener(
        config['videoID'], config['videoURL'], videoSource);
    if (!askLanguage)
        opener.openDialog(
            config['baseVersionNo'], config['languageCode'],
            config['originalLanguageCode'], config['fork']);
    else {
        mirosubs.widget.ChooseLanguageDialog.show(
            config['originalLanguageSubtitled'],
            function(subLanguage, originalLanguage) {
                opener.openDialog(
                    config['baseVersionNo'],
                    subLanguage, originalLanguage, 
                    mirosubs.isForkedLanguage(subLanguage));
            });
    }
};

/**
 * For JWPlayer API.
 */
mirosubs.api.openUnisubsDialog = function(videoURL) {
    // TODO: you might want to be getting an array of videourls back from
    // the server and then choosing the best one for effectiveVideoURL.
    mirosubs.Rpc.call(
        'fetch_video_id_and_settings',
        { 'video_url': videoURL },
        function(response) {
            mirosubs.api.openUnisubsDialogWithSettings(
                true,
                {'videoURL': videoURL,
                 'effectiveVideoURL': videoURL,
                 'videoID': response['video_id'],
                 'originalLanguageSubtitled': 
                     response['is_original_language_subtitled'],
                 'baseVersionNo': null },
                response['general_settings']);
        });
};

mirosubs.api.toSRT = function(jsonSubs) {
    var stringBuffer = new goog.string.StringBuffer();
    for (var i = 0; i < jsonSubs.length; i++)
        mirosubs.api.subToSrt_(jsonSubs[i], i, stringBuffer);
    return stringBuffer.toString();
};

mirosubs.api.loggedIn = function(username) {
    mirosubs.loggedIn(username);
};

mirosubs.api.subToSrt_ = function(sub, index, stringBuffer) {
    stringBuffer.
        append(index + 1).
        append("\n");
    mirosubs.api.writeSrtTimeLine_(sub, stringBuffer);
    stringBuffer.
        append(sub['text']).
        append("\n\n");
};

mirosubs.api.writeSrtTimeLine_ = function(sub, stringBuffer) {
    mirosubs.api.writeSrtTime_(sub['start_time'], stringBuffer);
    stringBuffer.append(' --> ');
    mirosubs.api.writeSrtTime_(sub['end_time'], stringBuffer);
    stringBuffer.append('\n');
};

mirosubs.api.writeSrtTime_ = function(seconds, stringBuffer) {
    var secondsInt = Math.floor(seconds);
    var p = goog.string.padNumber;
    stringBuffer.
        append(p(Math.floor(secondsInt / 3600) % 60, 2)).
        append(':').
        append(p(Math.floor(secondsInt / 60) % 60, 2)).
        append(':').
        append(p(secondsInt % 60, 2)).
        append(',').
        append(p(Math.floor(seconds * 1000) % 1000, 3));
};

mirosubs.api.embed = function(elementID, widgetConfig) {
    mirosubs.siteConfig = mirosubs.Config.siteConfig;
    var widget = new mirosubs.widget.Widget(widgetConfig);
    widget.decorate(goog.dom.getElement(elementID));
};

goog.exportSymbol(
    'mirosubs.api.openDialog',
    mirosubs.api.openDialog);

goog.exportSymbol(
    'mirosubs.api.openUnisubsDialogWithSettings',
    mirosubs.api.openUnisubsDialogWithSettings);

goog.exportSymbol(
    'mirosubs.api.openUnisubsDialog',
    mirosubs.api.openUnisubsDialog);

goog.exportSymbol(
    'mirosubs.api.toSRT',
    mirosubs.api.toSRT);

goog.exportSymbol(
    'mirosubs.api.loggedIn',
    mirosubs.api.loggedIn);

goog.exportSymbol(
    'mirosubs.api.embed',
    mirosubs.api.embed);