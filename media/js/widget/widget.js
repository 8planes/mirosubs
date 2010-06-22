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

goog.provide('mirosubs.widget.Widget');

/**
 * @param {Object} widgetConfig parameter documentation is currenty in embed.js.
 */
mirosubs.widget.Widget = function(widgetConfig) {
    goog.ui.Component.call(this);

    /**
     * @type {?string}
     */
    this.videoURL_ = widgetConfig['video_url'];
    /**
     * @type {undefined|HTMLVideoElement|HTMLObjectElement|HTMLEmbedElement}
     */
    this.videoElement_ = widgetConfig['video_element'];
    this.nullWidget_ = !!widgetConfig['null_widget'];
    this.subtitleImmediately_ = 
        !!widgetConfig['subtitle_immediately'];
    this.translateImmediately_ =
        !!widgetConfig['translate_immediately'];
    /**
     * null if no autoplay, blank string for original language, 
     * language code for other
     * @type {?string}
     */
    this.autoplayLanguage_ = widgetConfig['autoplay_language'];
    if (!this.autoplayLanguage_ && this.autoplayLanguage_ != '')
        this.autoplayLanguage_ = null;
    /**
     * Whether or not we've heard back from the initial call 
     * to the server yet.
     */
    this.stateInitialized_ = false;
};
goog.inherits(mirosubs.widget.Widget, goog.ui.Component);

mirosubs.widget.Widget.logger_ =
    goog.debug.Logger.getLogger('mirosubs.widget.Widget');

mirosubs.widget.Widget.prototype.createDom = function() {
    mirosubs.widget.Widget.superClass_.createDom.call(this);
    this.addWidget_(this.getElement());
};

/**
 * @param {HTMLDivElement} el Just a blank div with class mirosubs-widget.
 */
mirosubs.widget.Widget.prototype.decorateInternal = function(el) {
    mirosubs.widget.Widget.superClass_.decorateInternal.call(this, el);
    this.addWidget_(el);
};

mirosubs.widget.Widget.prototype.addWidget_ = function(el) {
    this.videoSource_ = null;
    try {
        this.videoSource_ = 
            mirosubs.video.VideoSource.videoSourceForURL(this.videoURL_);
    }
    catch (err) {
        // TODO: format this more.
        el.innerHTML = err.message;
        return;
    }
    this.videoPlayer_ = this.videoSource_.createPlayer();
    this.addChild(this.videoPlayer_, true);
    this.videoTab_ = new mirosubs.widget.VideoTab();
    this.addChild(this.videoTab_, true);
    this.videoTab_.setText("Loading...");
    this.videoTab_.showLoading(true);
    mirosubs.Rpc.call(
        'show_widget', {
            'video_url' : this.videoURL_,
            'null_widget': this.nullWidget_,
            'autoplay': this.autoplayLanguage_ != null,
            'autoplay_language': this.autoplayLanguage_
        },
        goog.bind(this.initializeState_, this));
};

mirosubs.widget.Widget.prototype.initializeState_ = function(result) {
    this.stateInitialized_ = true;
    if (result['username'])
        mirosubs.currentUsername = result['username'];
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        result["writelock_expiration"];
    this.videoID_ = result['video_id'];

    var initialTab = result['initial_tab'];
    var IS = mirosubs.widget.VideoTab.InitialState;
    this.popupMenu_ = new mirosubs.MainMenu(
        this.videoID_, this.nullWidget_, initialTab == IS.CHOOSE_LANGUAGE, 
        result['translation_languages']);
    this.popupMenu_.render(document.body);
    this.popupMenu_.attach(
        this.videoTab_.getAnchorElem(), 
        goog.positioning.Corner.BOTTOM_LEFT,
        goog.positioning.Corner.TOP_LEFT);

    this.setInitialVideoTabState_(initialTab, result['owned_by']);

    if (this.autoplayLanguage_ != null)
        this.subsLoaded_(
            this.autoplayLanguage_ == '' ? null : this.autoplayLanguage_,
            result['subtitles']);
    if (this.subtitleImmediately_)
        goog.Timer.callOnce(goog.bind(this.subtitle_, this));
    else if (this.translateImmediately_)
        goog.Timer.callOnce(goog.bind(this.addNewLanguage_, this));

    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.setInitialVideoTabState_ = 
    function(initialTab, opt_lockedBy) 
{
    this.videoTab_.showLoading(false);
    var IS = mirosubs.widget.VideoTab.InitialState;
    var M = mirosubs.widget.VideoTab.Messages;
    if (initialTab == IS.SUBTITLE_ME)
        this.videoTab_.setText(M.SUBTITLE_ME);
    else if (initialTab == IS.CONTINUE)
        this.videoTab_.setText(M.CONTINUE);
    else if (initialTab == IS.IN_PROGRESS)
        this.videoTab_.setText(M.IN_PROGRESS + opt_lockedBy);
    else if (initialTab == IS.CHOOSE_LANGUAGE)
        this.videoTab_.setText(M.CHOOSE_LANGUAGE);
};

mirosubs.widget.Widget.prototype.enterDocument = function() {
    mirosubs.widget.Widget.superClass_.enterDocument.call(this);
    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.attachEvents_ = function() {
    if (!this.stateInitialized_ || !this.isInDocument())
        return;
    var et = mirosubs.MainMenu.EventType;
    this.getHandler().
        listen(this.videoTab_.getAnchorElem(), 'click',
               function(e) { e.preventDefault(); }).
        listen(this.popupMenu_, et.ADD_SUBTITLES, this.subtitle_).
        listen(this.popupMenu_, et.EDIT_SUBTITLES, this.editSubtitles_).
        listen(this.popupMenu_, et.LANGUAGE_SELECTED, this.languageSelected_).
        listen(this.popupMenu_, et.ADD_NEW_LANGUAGE, this.addNewLanguage_).
        listen(this.popupMenu_, et.TURN_OFF_SUBS, this.turnOffSubs_).
        listen(mirosubs.userEventTarget,
               goog.object.getValues(mirosubs.EventType),
               this.loginStatusChanged_);
};

mirosubs.widget.Widget.prototype.loginStatusChanged_ = function() {
    if (this.dialog_)
        this.dialog_.updateLoginState();
};
mirosubs.widget.Widget.prototype.subtitle_ = function() {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call(
        "start_editing" + (this.nullWidget_ ? '_null' : ''), 
        {"video_id": this.videoID_},
        function(result) {
            that.videoTab_.showLoading(false);
            if (result["can_edit"]) {
                var version = result["version"];
                var existingSubs = result["existing"];
                if (version == 0)
                    that.startSubtitling_(existingSubs);
                else
                    that.editSubtitlesImpl_(version, existingSubs);
            }
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
mirosubs.widget.Widget.prototype.editSubtitles_ = function() {
    if (this.languageCodePlaying_ == null) {
        // original language
        this.subtitle_();
    }
    else {
        // foreign language
        this.videoTab_.showLoading(true);
        mirosubs.Rpc.call(
            'start_translating' + (this.nullWidget_ ? '_null' : ''),
            { 'video_id' : this.videoID_,
              'language_code' : this.languageCodePlaying_,
              'editing' : true },
            goog.bind(this.editTranslations_, this));
    }
};
mirosubs.widget.Widget.prototype.editTranslations_ = function(result) {
    // TODO: check result['can_edit']
    this.videoTab_.showLoading(false);
    this.videoPlayer_.pause();
    this.turnOffSubs_();
    var dialog = new mirosubs.translate.EditDialog(
        this.videoSource_, this.videoID_,
        result['existing_captions'],
        result['languages'],
        result['version'],
        this.languageCodePlaying_,
        result['existing'],
        this.nullWidget_);
    dialog.setVisible(true);
    this.dialog_ = dialog;
};
mirosubs.widget.Widget.prototype.startSubtitling_ = 
    function(existingCaptions) 
{
    this.videoPlayer_.pause();
    this.turnOffSubs_();
    var subtitleDialog = new mirosubs.subtitle.Dialog(
        this.videoSource_, 
        new mirosubs.subtitle.MSServerModel(
            this.videoID_, 0, this.nullWidget_),
        existingCaptions);
    subtitleDialog.setVisible(true);
    this.dialog_ = subtitleDialog;
    var that = this;
    goog.events.listenOnce(
        subtitleDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
            if (subtitleDialog.isSaved()) {
                that.videoTab_.setText(
                    mirosubs.widget.VideoTab.Messages.CHOOSE_LANGUAGE);
                that.popupMenu_.setSubtitled();
            }
        });
};
mirosubs.widget.Widget.prototype.editSubtitlesImpl_ = 
    function(version, existingCaptions) 
{
    this.videoPlayer_.pause();
    this.turnOffSubs_();
    var dialog = new mirosubs.subtitle.EditDialog(
        this.videoSource_,
        new mirosubs.subtitle.MSServerModel(
            this.videoID_, version, this.nullWidget_),
        existingCaptions);
    dialog.setVisible(true);
    this.dialog_ = dialog;
};
mirosubs.widget.Widget.prototype.languageSelected_ = function(event) {
    if (event.languageCode)
        this.translationSelected_(event.languageCode);
    else
        this.originalLanguageSelected_();
};

mirosubs.widget.Widget.prototype.translationSelected_ = function(languageCode) {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_translations' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_,
                        'language_code' : languageCode },
                      goog.bind(this.subsLoaded_, this, languageCode));
};

mirosubs.widget.Widget.prototype.originalLanguageSelected_ = function() {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call('fetch_captions' + (this.nullWidget_ ? '_null' : ''),
                      { 'video_id' : this.videoID_ },
                      goog.bind(this.subsLoaded_, this, null));
};

mirosubs.widget.Widget.prototype.turnOffSubs_ = function(event) {
    if (this.playManager_) {
        this.popupMenu_.setShowingSubs(false);
        this.videoTab_.setText(
            mirosubs.widget.VideoTab.Messages.CHOOSE_LANGUAGE);
        this.disposePlayManager_();
    }
};

/**
 * @param {string=} languageCode for language, or null for original language.
 */
mirosubs.widget.Widget.prototype.subsLoaded_ = 
    function(languageCode, subtitles) 
{
    this.videoTab_.showLoading(false);
    this.disposePlayManager_();
    this.languageCodePlaying_ = languageCode;
    this.playManager_ = new mirosubs.play.Manager(
        this.videoPlayer_, subtitles);
    this.videoTab_.setText(
        languageCode == null ? "Original language" : 
            this.findLanguage_(languageCode)['name']);
    this.popupMenu_.setCurrentLangCode(languageCode);
    this.popupMenu_.setShowingSubs(true);
};
mirosubs.widget.Widget.prototype.findLanguage_ = function(code) {
    return goog.array.find(
        this.popupMenu_.getTranslationLanguages(), 
        function(tl) {
            return tl['code'] == code;
        });
};
mirosubs.widget.Widget.prototype.addNewLanguage_ = function() {
    this.videoTab_.showLoading(true);
    mirosubs.Rpc.call(
        'fetch_captions_and_open_languages' + 
            (this.nullWidget_ ? '_null' : ''),
        { 'video_id' : this.videoID_ },
        goog.bind(this.addNewLanguageResponseReceived_, this));
};

mirosubs.widget.Widget.prototype.addNewLanguageResponseReceived_ = 
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
mirosubs.widget.Widget.prototype.disposePlayManager_ = function() {
    if (this.playManager_) {
        this.playManager_.dispose();
        this.playManager_ = null;
    }
    this.videoPlayer_.showCaptionText(null);
};
mirosubs.widget.Widget.prototype.disposeInternal = function() {
    mirosubs.widget.Widget.superClass_.disposeInternal.call(this);
    this.handler_.dispose();
    this.disposePlayManager_();
};
