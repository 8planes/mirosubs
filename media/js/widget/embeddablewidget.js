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

mirosubs.EmbeddableWidget = function(uuid, videoID, videoURL, 
                                     youtubeVideoID, translationLanguages, 
                                     showTab, nullWidget, 
                                     autoplayParams, subtitleImmediately) {
    goog.Disposable.call(this);

    this.videoID_ = videoID;
    this.nullWidget_ = nullWidget;
    if (youtubeVideoID == '')
        this.videoSource_ = 
            new mirosubs.video.Html5VideoSource(videoURL);
    else
        this.videoSource_ = 
            new mirosubs.video.YoutubeVideoSource(uuid, youtubeVideoID);
    this.videoPlayer_ = this.videoSource_.createPlayer();
    this.videoPlayer_.decorate(goog.dom.$(uuid + "_video"));
    this.videoTab_ = new mirosubs.VideoTab();
    this.videoTab_.decorate(goog.dom.$(uuid + '_videoTab'));
    this.handler_ = new goog.events.EventHandler(this);

    this.popupMenu_ = new mirosubs.MainMenu(
        videoID, nullWidget, showTab == 3, translationLanguages);
    this.popupMenu_.render(document.body);
    this.popupMenu_.attach(this.videoTab_.getAnchorElem(),
                           goog.positioning.Corner.BOTTOM_LEFT,
                           goog.positioning.Corner.TOP_LEFT);
    this.handler_.listen(this.videoTab_.getAnchorElem(), 'click',
                         function(event) {
                             event.preventDefault();
                         });
    var et = mirosubs.MainMenu.EventType;
    this.handler_.listen(
        this.popupMenu_, et.ADD_SUBTITLES, this.startSubtitling_);
    this.handler_.listen(
        this.popupMenu_, et.LANGUAGE_SELECTED, this.languageSelected_);
    this.handler_.listen(
        this.popupMenu_, et.ADD_NEW_LANGUAGE, this.addNewLanguage_);
    this.handler_.listen(
        this.popupMenu_, et.TURN_OFF_SUBS, this.turnOffSubs_);
    /**
     * The Manager used for displaying subtitles on the video on the page.
     * @type {?mirosubs.play.Manager} 
     */
    this.playManager_ = null;
    /**
     * Master list of translation languages for this video.
     * TODO: Only use list stored in MainMenu.
     */
    this.translationLanguages_ = translationLanguages;
    this.handler_.listen(mirosubs.userEventTarget,
                         goog.object.getValues(mirosubs.EventType),
                         this.loginStatusChanged_);
    if (autoplayParams != null)
        this.subsLoaded_(autoplayParams['language_code'],
                         autoplayParams['subtitles']);
    if (subtitleImmediately)
        goog.Timer.callOnce(goog.bind(this.startSubtitling_, this));
};
goog.inherits(mirosubs.EmbeddableWidget, goog.Disposable);

mirosubs.EmbeddableWidget.logger_ =
    goog.debug.Logger.getLogger('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget.wrap = function(identifier) {
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
                                      identifier["video_url"],
                                      identifier["youtube_videoid"],
                                      identifier["translation_languages"],
                                      identifier["show_tab"],
                                      identifier["null_widget"],
                                      identifier["autoplay_params"],
                                      identifier["subtitle_immediately"]));
};

mirosubs.EmbeddableWidget.setConstants_ = function(identifier) {
    var username = identifier["username"];
    mirosubs.EmbeddableWidget.logger_.info('username is ' + username);
    mirosubs.currentUsername = username == '' ? null : username;
    var baseURL = identifier["base_url"];
    mirosubs.Rpc.BASE_URL = baseURL + '/widget/rpc/';
    mirosubs.BASE_URL = baseURL;
    mirosubs.Clippy.SWF_URL = 
        [baseURL, '/site_media/swf/clippy.swf'].join('');
    mirosubs.subtitle.MSServerModel.EMBED_JS_URL = baseURL + '/embed_widget.js';
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        identifier["writelock_expiration"];
};

mirosubs.EmbeddableWidget.prototype.loginStatusChanged_ = function() {
    if (this.dialog_)
        this.dialog_.updateLoginState();
};

mirosubs.EmbeddableWidget.prototype.startSubtitling_ = function() {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call(
        "start_editing" + (this.nullWidget_ ? '_null' : ''), 
        {"video_id": this.videoID_},
        function(result) {
            that.videoTab_.showLoading(false);
            if (result["can_edit"])
                that.startSubtitlingImpl_(result["version"], 
                                          result["existing"]);
            else {
                if (result["owned_by"])
                    alert("Sorry, this video is owned by " + 
                          result["owned_by"]);
                else
                    alert("Sorry, this video is locked by " +
                          result["locked_by"]);
            }
        });
};
mirosubs.EmbeddableWidget.prototype.startSubtitlingImpl_ = 
    function(version, existingCaptions) 
{
    this.videoPlayer_.pause();
    this.turnOffSubs_();
    var subtitleDialog = new mirosubs.subtitle.Dialog(
        this.videoSource_, 
        new mirosubs.subtitle.MSServerModel(
            this.videoID_, version, this.nullWidget_),
        existingCaptions);
    subtitleDialog.setVisible(true);
    this.dialog_ = subtitleDialog;
    var that = this;
    goog.events.listenOnce(
        subtitleDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
            if (subtitleDialog.isSaved()) {
                // FIXME: petit duplication. appears in server-side code also.
                that.videoTab_.setText('Choose language...');
                that.popupMenu_.setSubtitled();
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
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_translations' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_,
                        'language_code' : languageCode },
                      goog.bind(this.subsLoaded_, this, languageCode));
};

mirosubs.EmbeddableWidget.prototype.originalLanguageSelected_ = function() {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_captions' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_ },
                      goog.bind(this.subsLoaded_, this, null));
};

mirosubs.EmbeddableWidget.prototype.turnOffSubs_ = function(event) {
    if (this.playManager_) {
        this.popupMenu_.setShowingSubs(false);
        // FIXME: petit duplication. appears in server-side code also.
        this.videoTab_.setText("Choose Language...");
        this.disposePlayManager_();
    }
};

mirosubs.EmbeddableWidget.prototype.subsLoaded_ = 
    function(languageCode, subtitles) 
{
    this.videoTab_.showLoading(false);
    this.disposePlayManager_();
    this.playManager_ = new mirosubs.play.Manager(
        this.videoPlayer_, subtitles);
    // FIXME: petit duplication. appears in server-side code also.
    this.videoTab_.setText(
        languageCode == null ? "Original language" : 
            this.findLanguage_(languageCode)['name']);
    this.popupMenu_.setCurrentLangCode(languageCode);
    this.popupMenu_.setShowingSubs(true);
};
mirosubs.EmbeddableWidget.prototype.findLanguage_ = function(code) {
    return goog.array.find(
        this.translationLanguages_, function(tl) {
            return tl['code'] == code;
        });
};
mirosubs.EmbeddableWidget.prototype.addNewLanguage_ = function(event) {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call(
        'fetch_captions_and_open_languages' + 
            (this.nullWidget_ ? '_null' : ''),
        { 'video_id' : this.videoID_ },
        goog.bind(this.addNewLanguageResponseReceived_, this));
};

mirosubs.EmbeddableWidget.prototype.addNewLanguageResponseReceived_ = 
    function(result) 
{
    this.videoTab_.showLoading(false);
    this.videoPlayer_.pause();
    this.turnOffSubs_();
    var translationDialog = new mirosubs.translate.Dialog(
        this.videoSource_, this.videoID_, result['captions'], 
        result['languages'], this.nullWidget_);
    translationDialog.setVisible(true);
    this.dialog_ = translationDialog;
    var that = this;
    goog.events.listenOnce(
        translationDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
            var availableLanguages = 
                translationDialog.getAvailableLanguages();
            if (availableLanguages) {
                that.translationLanguages_ = availableLanguages;
                that.popupMenu_.setTranslationLanguages(
                    availableLanguages);
            }
        });
};
mirosubs.EmbeddableWidget.prototype.disposePlayManager_ = function() {
    if (this.playManager_) {
        this.playManager_.dispose();
        this.playManager_ = null;
    }
    this.videoPlayer_.showCaptionText(null);
};
mirosubs.EmbeddableWidget.prototype.disposeInternal = function() {
    mirosubs.EmbeddableWidget.superClass_.disposeInternal.call(this);
    this.handler_.dispose();
    this.disposePlayManager_();
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
