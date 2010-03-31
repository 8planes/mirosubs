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

goog.provide('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget = function(uuid, videoID, youtubeVideoID, 
                                     translationLanguages, 
                                     showTab, nullWidget, 
                                     autoplay_params) {
    goog.Disposable.call(this);

    this.videoID_ = videoID;
    this.nullWidget_ = nullWidget;
    if (youtubeVideoID == '')
        this.videoPlayer_ = mirosubs.Html5VideoPlayer.wrap(uuid + "_video");
    else
        this.videoPlayer_ = new mirosubs
            .YoutubeVideoPlayer(uuid, uuid + "_ytvideo", youtubeVideoID);
    this.userPanel_ = new mirosubs.UserPanel(uuid);
    this.controlTabPanel_ = new mirosubs.ControlTabPanel(uuid, showTab, videoID, 
                                                         translationLanguages,
                                                         nullWidget);
    this.captionPanel_ = new mirosubs.CaptionPanel(videoID, 
                                                   this.videoPlayer_, 
                                                   nullWidget);
    this.captionPanel_.decorate(goog.dom.$(uuid + "_captions"));
    this.handler_ = new goog.events.EventHandler(this);

    var et = mirosubs.MainMenu.EventType;
    this.handler_.listen(
        this.controlTabPanel_, et.ADD_SUBTITLES, this.startSubtitling_);
    this.handler_.listen(
        this.controlTabPanel_, et.LANGUAGE_SELECTED, this.languageSelected_);
    this.handler_.listen(
        this.controlTabPanel_, et.ADD_NEW_LANGUAGE, this.addNewLanguage_);
    this.handler_.listen(
        this.controlTabPanel_, et.TURN_OFF_SUBS, this.turnOffSubs_);
    if (autoplay_params != null)
        this.subsLoaded_(autoplay_params['language_code'],
                         autoplay_params['subtitles']);
};
goog.inherits(mirosubs.EmbeddableWidget, goog.Disposable);

mirosubs.EmbeddableWidget.logger_ =
    goog.debug.Logger.getLogger('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget.wrap = function(identifier) {
    var nullWidget = identifier["null_widget"];
    var debug = identifier["debug_js"];
    if (debug) {
        var debugWindow = new goog.debug.FancyWindow('main');
        debugWindow.setEnabled(true);
        debugWindow.init(); 
    }
    mirosubs.EmbeddableWidget.setConstants_(identifier);
    mirosubs.EmbeddableWidget.widgets = mirosubs.EmbeddableWidget.widgets || [];
    mirosubs.EmbeddableWidget.widgets.push(
        new mirosubs.EmbeddableWidget(identifier["uuid"], 
                                      identifier["video_id"],
                                      identifier["youtube_videoid"],
                                      identifier["translation_languages"],
                                      identifier["show_tab"],
                                      nullWidget,
                                      identifier["autoplay_params"]));
};

mirosubs.EmbeddableWidget.setConstants_ = function(identifier) {
    var username = identifier["username"];
    mirosubs.EmbeddableWidget.logger_.info('username is ' + username);
    mirosubs.currentUsername = username == '' ? null : username;
    var baseURL = identifier["base_url"];
    mirosubs.subtitle.MainPanel.SPINNER_GIF_URL = 
        baseURL + '/site_media/images/spinner.gif';
    mirosubs.Rpc.BASE_URL = baseURL + '/widget/rpc/';
    mirosubs.BASE_URL = baseURL;
    mirosubs.Clippy.SWF_URL = 
        [baseURL, '/site_media/swf/clippy.swf'].join('');
    mirosubs.subtitle.MSServerModel.EMBED_JS_URL = baseURL + '/embed_widget.js';
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        identifier["writelock_expiration"];
};

mirosubs.EmbeddableWidget.prototype.updateLoginState = function() {
    if (mirosubs.currentUsername == null)
        this.userPanel_.setLoggedOut();
    else
        this.userPanel_.setLoggedIn(mirosubs.currentUsername);
    this.captionPanel_.updateLoginState();
};

mirosubs.EmbeddableWidget.prototype.startSubtitling_ = function() {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    // FIXME: get the startSubtitling function contents out of CaptionPanel
    // and into this class.
    this.captionPanel_.startSubtitling(function(success) {
            that.controlTabPanel_.showLoading(false);
            if (success) {
                that.userPanel_.setVisible(false);
                goog.events.listenOnce(that.captionPanel_, 
                                       mirosubs.subtitle.MainPanel.EventType.FINISHED,
                                       that.finishedSubtitling_, false, that);
            }
        });
};

mirosubs.EmbeddableWidget.prototype.languageSelected_ = function(event) {
    if (event.languageCode)
        this.translationSelected_(event.languageCode);
    else
        this.originalLanguageSelected_();
};

mirosubs.EmbeddableWidget.prototype.translationSelected_ = function(languageCode) {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_translations' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_,
                        'language_code' : languageCode },
                      goog.bind(this.subsLoaded_, this, languageCode));
};

mirosubs.EmbeddableWidget.prototype.originalLanguageSelected_ = function() {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_captions' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_ },
                      goog.bind(this.subsLoaded_, this, null));
};

mirosubs.EmbeddableWidget.prototype.turnOffSubs_ = function(event) {
    this.controlTabPanel_.getMainMenu().setShowingSubs(false);
    this.captionPanel_.turnOffSubs();
};

mirosubs.EmbeddableWidget.prototype.subsLoaded_ = function(languageCode, subtitles) {
    this.controlTabPanel_.showLoading(false);
    this.captionPanel_.languageSelected(languageCode, subtitles);
    var mainMenu = this.controlTabPanel_.getMainMenu();
    mainMenu.setCurrentLangCode(languageCode);
    mainMenu.setShowingSubs(true);
};

mirosubs.EmbeddableWidget.prototype.addNewLanguage_ = function(event) {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_captions_and_open_languages' + 
                      (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_ },
                      goog.bind(this.addNewLanguageResponseReceived_, this));
};

mirosubs.EmbeddableWidget.prototype.addNewLanguageResponseReceived_ = function(result) {
    this.controlTabPanel_.showLoading(false);
    this.captionPanel_.addNewLanguage(result['captions'], 
                                      result['languages']);
    this.userPanel_.setVisible(false);
    goog.events.listenOnce(this.captionPanel_,
                           mirosubs.translate.MainPanel.EventType.FINISHED,
                           this.finishedTranslating_, false, this);
};

mirosubs.EmbeddableWidget.prototype.finishedSubtitling_ = function(event) {
    this.controlTabPanel_.showSelectLanguage();
    this.userPanel_.setVisible(true);
};

mirosubs.EmbeddableWidget.prototype.finishedTranslating_ = function(event) {
    this.userPanel_.setVisible(true);
    this.controlTabPanel_.setAvailableLanguages(event.availableLanguages);
};

mirosubs.EmbeddableWidget.prototype.disposeInternal = function() {
    mirosubs.EmbeddableWidget.superClass_.disposeInternal.call(this);
    this.handler_.dispose();
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
mirosubs["EmbeddableWidget"] = mirosubs.EmbeddableWidget;
mirosubs.EmbeddableWidget["wrap"] = mirosubs.EmbeddableWidget.wrap;

(function() {
    var m = window["MiroSubsToEmbed"];
    if (typeof(m) != 'undefined')
        for (var i = 0; i < m.length; i++)
            mirosubs.EmbeddableWidget.wrap(m[i]);
})();
