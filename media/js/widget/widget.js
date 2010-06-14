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
 * widgetConfig parameter documentation is currenty in embed.js.
 *
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
    this.videoTab_ = new mirosubs.VideoTab();
    this.videoTab_.setText("Loading...");
    this.videoTab_.showLoading(true);
    this.addChild(this.videoTab_, true);
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
    // TODO: probably set this when startEditing or whatever is called.
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        result["writelock_expiration"];
    this.videoID_ = result['video_id'];

    this.popupMenu_ = new mirosubs.MainMenu(
        this.videoID_, this.nullWidget_, 
        result['initial_tab'] == 
            mirosubs.widget.VideoTab.InitialState.SUBTITLE_ME,
        result['translation_languages']);
    this.popupMenu_.render(document.body);
    this.popupMenu_.attach(
        this.videoTab_.getAnchorElem(), 
        goog.positioning.Corner.BOTTOM_LEFT,
        goog.positioning.Corner.TOP_LEFT);

    // TODO: set text for videotab.

    if (this.autoplay_)
        this.subsLoaded_(this.autoplayLanguage_,
                         result['subtitles']);
    if (subtitleImmediately)
        goog.Timer.callOnce(goog.bind(this.startSubtitling_, this));

    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.enterDocument = function() {
    mirosubs.widget.Widget.superClass_.enterDocument.call(this);
    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.attachEvents_ = function() {
    if (!this.stateInitialized_ || !this.isInDocument())
        return;
    this.getHandler().
        listen(this.videoTab_.getAnchorElem(), 'click',
               function(e) { e.preventDefault(); }).
        listen(this.popupMenu_, et.ADD_SUBTITLES, this.startSubtitling_).
        listen(this.popupMenu_, et.EDIT_SUBTITLES, this.editSubtitles_).
        listen(this.popupMenu_, et.LANGUAGE_SELECTED, this.languageSelected_).
        listen(this.popupMenu_, et.ADD_NEW_LANGUAGE, this.addNewLanguage_).
        listen(this.popupMenu_, et.TURN_OFF_SUBS, this.turnOffSubs_).
        listen(mirosubs.userEventTarget,
               goog.object.getValues(mirosubs.EventType),
               this.loginStatusChanged_);
};

mirosubs.EmbeddableWidget.prototype.loginStatusChanged_ = function() {
    if (this.dialog_)
        this.dialog_.updateLoginState();
};
/**
 * @param {function(int, array.<JsonCaption>)} postFn
 */
mirosubs.EmbeddableWidget.prototype.subtitle_ = function(postFn) {
    this.videoTab_.showLoading(true);
    var that = this;
    mirosubs.Rpc.call(
        "start_editing" + (this.nullWidget_ ? '_null' : ''), 
        {"video_id": this.videoID_},
        function(result) {
            that.videoTab_.showLoading(false);
            if (result["can_edit"])
                postFn(result["version"], result["existing"]);
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
mirosubs.EmbeddableWidget.prototype.startSubtitling_ = function() {
    this.subtitle_(goog.bind(this.startSubtitlingImpl_, this));
};
mirosubs.EmbeddableWidget.prototype.editSubtitles_ = function() {
    if (this.languageCodePlaying_ == null) {
        // original language
        this.subtitle_(goog.bind(this.editSubtitlesImpl_, this));
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
mirosubs.EmbeddableWidget.prototype.editTranslations_ = function(result) {
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
mirosubs.EmbeddableWidget.prototype.editSubtitlesImpl_ = 
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
    this.languageCodePlaying_ = languageCode;
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
