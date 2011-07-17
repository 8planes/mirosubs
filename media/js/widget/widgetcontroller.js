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

goog.provide('mirosubs.widget.WidgetController');

/**
 * @constructor
 *
 */
mirosubs.widget.WidgetController = function(videoURL, videoPlayer, videoTab) {
    // TODO: when all VideoSource implementations support getVideoURL,
    // remove videoURL from the parameters for this constructor.
    this.videoURL_ = videoURL;
    this.videoPlayer_ = videoPlayer;
    this.videoTab_ = videoTab;
};

/**
 * Widget calls this when show_widget rpc call returns.
 */
mirosubs.widget.WidgetController.prototype.initializeState = function(result) {
    try {
        this.initializeStateImpl_(result);
    }
    catch (e) {
        if (console && console.log) {
            console.log(e);
        }
        this.videoTab_.showError();
    }
};

mirosubs.widget.WidgetController.prototype.initializeStateImpl_ = function(result) {
    mirosubs.widget.WidgetController.makeGeneralSettings(result);

    var videoID = result['video_id'];
     
    if (videoID){
        this.videoTab_.createShareButton(
            new goog.Uri(mirosubs.getSubtitleHomepageURL(videoID)), false);
    }

    var dropDownContents = new mirosubs.widget.DropDownContents(
        result['drop_down_contents'], result["is_moderated"]);
    var subtitleState = mirosubs.widget.SubtitleState.fromJSON(
        result['subtitles']);

    var popupMenu = new mirosubs.widget.DropDown(
        videoID, dropDownContents, this.videoTab_);

    this.videoTab_.showContent(popupMenu.hasSubtitles(),
                               subtitleState);

    popupMenu.render();
    mirosubs.style.showElement(popupMenu.getElement(), false);

    popupMenu.setCurrentSubtitleState(subtitleState);
    popupMenu.dispatchLanguageSelection_(this.currentLang_);

    this.playController_ = new mirosubs.widget.PlayController(
        videoID, this.videoPlayer_.getVideoSource(), this.videoPlayer_, 
        this.videoTab_, popupMenu, subtitleState);

    this.subtitleController_ = new mirosubs.widget.SubtitleController(
        videoID, this.videoURL_, 
        this.playController_, this.videoTab_, popupMenu);
};

/**
 * Sets parameters that the widget needs to function: username, 
 * embed version, writelock expiration, languages, and metadata languages.
 * @param {Object} settings
 */
mirosubs.widget.WidgetController.makeGeneralSettings = function(settings) {
    if (settings['username'])
        mirosubs.currentUsername = settings['username'];
    mirosubs.embedVersion = settings['embed_version'];
    mirosubs.LOCK_EXPIRATION = 
        settings["writelock_expiration"];
    mirosubs.languages = settings['languages'];
    mirosubs.metadataLanguages = settings['metadata_languages'];
    var sortFn = function(a, b) { 
        return a[1] > b[1] ? 1 : a[1] < b[1] ? -1 : 0
    };
    goog.array.sort(mirosubs.languages, sortFn);
    goog.array.sort(mirosubs.metadataLanguages, sortFn);
};

mirosubs.widget.WidgetController.prototype.getSubtitleController = function() {
    return this.subtitleController_;
};

mirosubs.widget.WidgetController.prototype.getPlayController = function() {
    return this.playController_;
};

mirosubs.widget.WidgetController.prototype.openMenu = function(){
    this.subtitleController_.dropDown_.show();
}
