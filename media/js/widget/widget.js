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

// FIXME: this class has become too long/complicated. Need to break it up into smaller components.

/**
 * @param {Object} widgetConfig parameter documentation is currenty in embed.js.
 */
mirosubs.widget.Widget = function(widgetConfig) {
    goog.ui.Component.call(this);

    /**
     * @type {?string}
     */
    this.videoURL_ = widgetConfig['video_url'];
    mirosubs.videoURL = this.videoURL_;
    /**
     * @type {undefined|HTMLVideoElement|HTMLObjectElement|HTMLEmbedElement}
     */
    this.videoElement_ = widgetConfig['video_element'];
    this.hideTab_ = !!widgetConfig['hide_tab'];
    this.subtitleImmediately_ = 
        !!widgetConfig['subtitle_immediately'];
    this.translateImmediately_ =
        !!widgetConfig['translate_immediately'];
    this.baseState_ = new mirosubs.widget.BaseState(
        widgetConfig['base_state']);
    /**
     * Whether or not we've heard back from the initial call 
     * to the server yet.
     */
    this.stateInitialized_ = false;
    this.state_ = null;
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

mirosubs.widget.Widget.prototype.setVideoSource_ = function(videoSource) {
    this.videoSource_ = videoSource;
    this.videoPlayer_ = this.videoSource_.createPlayer();
    this.addChildAt(this.videoPlayer_, 0, true);
    this.setVideoDimensions_();
};

mirosubs.widget.Widget.prototype.addWidget_ = function(el) {
    var videoSource = null;
    try {
        videoSource = mirosubs.video.VideoSource.videoSourceForURL(
            this.videoURL_);
    }
    catch (err) {
        // TODO: format this more.
        el.innerHTML = err.message;
        return;
    }
    if (videoSource != null)
        this.setVideoSource_(videoSource);
    this.videoTab_ = new mirosubs.widget.VideoTab();
    var videoTabContainer = new goog.ui.Component();
    this.addChild(videoTabContainer, true);
    videoTabContainer.addChild(this.videoTab_, true);
    videoTabContainer.getElement().className = 
        'mirosubs-videoTab-container';
    if (this.hideTab_)
        goog.style.showElement(this.videoTab_.getElement(), false);
    this.videoTab_.setText("Loading...");
    this.videoTab_.showLoading(true);

    this.state_ = new mirosubs.widget.InitialState(
        this, this.videoURL_, this.baseState_);
    this.state_.initialize(goog.bind(this.initializeState_, this));
};

mirosubs.widget.Widget.prototype.initializeState_ = function(result) {
    this.stateInitialized_ = true;
    if (result['username'])
        mirosubs.currentUsername = result['username'];
    mirosubs.embedVersion = result['embed_version'];
    if (result['flv_url'] && !this.videoSource_)
        this.setVideoSource_(new mirosubs.video.FlvVideoSource(
            result['flv_url']));
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        result["writelock_expiration"];
    this.videoID_ = result['video_id'];

    var initialTab = result['initial_tab'];
    var IS = mirosubs.widget.VideoTab.InitialState;

    var subtitleCount = result['subtitles'] ? 
        result['subtitles'].length : result['subtitle_count'];

    this.addChild(this.popupMenu_ = new mirosubs.widget.DropDown(
        this, this.videoID_, subtitleCount, 
        result['translation_languages']), true);
    goog.style.showElement(this.popupMenu_.getElement(), false);

    this.setInitialVideoTabState_(initialTab, result['owned_by']);
    this.videoTab_.showNudge(false);

    if (this.baseState_.NOT_NULL)
        this.subsLoaded_(
            this.baseState_.LANGUAGE, result['subtitles']);
    else if (result['subtitles']) 
        // subs loaded based on autoplay preferences
        this.subsLoaded_(
            result['subtitles_language'], result['subtitles']);
    if (this.subtitleImmediately_)
        goog.Timer.callOnce(goog.bind(this.subtitle_, this));
    else if (this.translateImmediately_) {
        if (this.baseState_.LANGUAGE)
            goog.Timer.callOnce(goog.bind(this.editTranslationImpl_, this));
        else
            goog.Timer.callOnce(goog.bind(this.addNewLanguage_, this));
    }

    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.setInitialVideoTabState_ = 
    function(initialTab, opt_lockedBy) 
{
    this.videoTab_.showLoading(false);
    var IS = mirosubs.widget.VideoTab.InitialState;
    var M = mirosubs.widget.VideoTab.Messages;
    if (initialTab == IS.SUBTITLE_ME)
        this.videoTab_.setText(M.SUBTITLE_ME, true);
    else if (initialTab == IS.CHOOSE_LANGUAGE)
        this.videoTab_.setText(M.CHOOSE_LANGUAGE);
};

mirosubs.widget.Widget.prototype.enterDocument = function() {
    mirosubs.widget.Widget.superClass_.enterDocument.call(this);
    this.setVideoDimensions_();
    this.attachEvents_();
};

mirosubs.widget.Widget.prototype.setVideoDimensions_ = function() {
    if (!this.isInDocument() || !this.videoPlayer_)
        return;
    if (this.videoPlayer_.areDimensionsKnown())
        this.videoDimensionsKnown_();
    else
        this.getHandler().listen(
            this.videoPlayer_,
            mirosubs.video.AbstractVideoPlayer.EventType.DIMENSIONS_KNOWN,
            this.videoDimensionsKnown_);
};

mirosubs.widget.Widget.prototype.videoDimensionsKnown_ = function() {
    this.getElement().style.width = 
        Math.round(this.videoPlayer_.getVideoSize().width) + 'px';
};

mirosubs.widget.Widget.prototype.attachEvents_ = function() {
    if (!this.stateInitialized_ || !this.isInDocument())
        return;
    this.getHandler().
        listen(this.videoTab_.getAnchorElem(), 'click',
               this.videoAnchorClicked_).
        listen(this.popupMenu_, 
               goog.object.getValues(mirosubs.widget.DropDown.Selection),
               this.menuItemSelected_).
        listen(mirosubs.userEventTarget,
               goog.object.getValues(mirosubs.EventType),
               this.loginStatusChanged_);
};

mirosubs.widget.Widget.prototype.videoAnchorClicked_ = function(e) {
    if (this.videoTab_.hasNoSubtitles())
        this.editSubtitles_();
    else
        this.popupMenu_.toggleShow();
    e.preventDefault();
};

mirosubs.widget.Widget.prototype.menuItemSelected_ = function(event) {
    this.selectMenuItem(event.type, event.languageCode);
};

/**
 * Select a menu item. Either called by selecting 
 * a menu item or programmatically by js on the page.
 */
mirosubs.widget.Widget.prototype.selectMenuItem = function(selection, opt_languageCode) {
    var s = mirosubs.widget.DropDown.Selection;
    if (selection == s.ADD_TRANSLATION)
        this.addNewLanguageClicked_();
    else if (selection == s.IMPROVE_SUBTITLES)
        this.editSubtitles_();
    else if (selection == s.SUBTITLE_HOMEPAGE)
        alert('subtitle homepage');
    else if (selection == s.SUBTITLES_OFF)
        this.turnOffSubs_();
    else if (selection == s.LANGUAGE_SELECTED)
        this.languageSelected_(opt_languageCode);
};
mirosubs.widget.Widget.prototype.playAt = function(time) {
    this.videoPlayer_.setPlayheadTime(time);
    this.videoPlayer_.play();
};

mirosubs.widget.Widget.prototype.loginStatusChanged_ = function() {
    if (this.dialog_)
        this.dialog_.updateLoginState();
    this.popupMenu_.loginStatusChanged();
};
mirosubs.widget.Widget.prototype.subtitle_ = function() {
    if (this.baseState_.REVISION != null) {
        var msg = 
            ["You're about to edit revision ", 
             this.baseState_.REVISION, ", an old revision. ",
             "Changes may have been made since this revision, and your edits ",
             "will override those changes. Are you sure you want to do this?"].
            join('');
        if (confirm(msg))
            this.subtitleImpl_();
        else if (mirosubs.returnURL)
            window.location.replace(mirosubs.returnURL);
    }
    else
        this.subtitleImpl_();
};
mirosubs.widget.Widget.prototype.subtitleImpl_ = function() {
    this.videoTab_.showLoading(true);
    var that = this;
    this.state_ = new mirosubs.widget.SubtitleState(this, this.videoID_, this.baseState_);
    this.state_.initialize(
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
                else {
                    var username = 
                        (result['locked_by'] == 'anonymous' ?
                         'Someone else' : ('The user ' + result['locked_by']));
                    alert(username + ' is currently editing these subtitles. Please wait and try again later.');
                }
            }
        });
};
mirosubs.widget.Widget.prototype.getState = function() {
    return self.state_;
};
mirosubs.widget.Widget.prototype.editSubtitles_ = function() {
    if (this.languageCodePlaying_ == null) {
        // original language
        if (!this.possiblyRedirectToOnsiteWidget_(true))
            this.subtitle_();
    }
    else {
        // foreign language
        if (!this.possiblyRedirectToOnsiteWidget_(false))
            this.editTranslationImpl_();
    }
};
mirosubs.widget.Widget.prototype.editTranslationImpl_ = function() {
    if (this.baseState_.REVISION != null) {
        var msg =
            ["You're about to edit revision ", 
             this.baseState_.REVISION, ", an old revision. ",
             "Changes may have been made since this revision, and your edits ",
             "will override those changes. Are you sure you want to do this?"].
            join('');
        if (confirm(msg))
            this.editTranslationConfirmed_();
        else if (mirosubs.returnURL)
            window.location.replace(mirosubs.returnURL);
    }
    else
        this.editTranslationConfirmed_();
};
mirosubs.widget.Widget.prototype.editTranslationConfirmed_ = function() {
    var languageCode = this.baseState_.LANGUAGE ? 
        this.baseState_.LANGUAGE : this.languageCodePlaying_;
    this.state_ = new mirosubs.widget.EditTranslationState(this, this.videoID_,
        languageCode, this.baseState_);
    this.videoTab_.showLoading(true);
    this.state_.initialize(goog.bind(this.editTranslations_, this));
};
/**
 * @param {boolean} forSubtitling true for subs, false for translations
 */
mirosubs.widget.Widget.prototype.possiblyRedirectToOnsiteWidget_ =
    function(forSubtitling) 
{
    if (mirosubs.DEBUG || !goog.userAgent.GECKO)
        return false;
    else {
        var url = mirosubs.siteURL() + '/onsite_widget/?';
        var queryData = new goog.Uri.QueryData();
        var newBaseState = {};
        queryData.set('video_url', this.videoURL_);
        if (mirosubs.IS_NULL)
            queryData.set('null_widget', 'true');
        if (mirosubs.DEBUG)
            queryData.set('debug_js', 'true');

        if (this.baseState_.NOT_NULL)
            newBaseState = this.baseState_.ORIGINAL_PARAM;

        if (forSubtitling)
            queryData.set('subtitle_immediately', 'true');
        else {
            queryData.set('translate_immediately', 'true');
            newBaseState['language'] = this.languageCodePlaying_;
        }

        if (this.baseState_.NOT_NULL || !forSubtitling)
            queryData.set('base_state', goog.json.serialize(newBaseState));
        queryData.set('return_url', window.location.href);
        window.location.assign(url + queryData.toString());
        return true;
    }
};
mirosubs.widget.Widget.prototype.editTranslations_ = function(result) {
    // TODO: check result['can_edit']
    this.videoTab_.showLoading(false);
    this.videoPlayer_.stopLoading();
    this.turnOffSubs_();
    var dialog = new mirosubs.translate.EditDialog(
        this.videoSource_, this.videoID_,
        result['existing_captions'],
        result['languages'],
        result['version'],
        this.languageCodePlaying_,
        result['existing']);
    dialog.setVisible(true);
    this.dialog_ = dialog;

    var that = this;
    goog.events.listenOnce(
        dialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
	    that.videoPlayer_.resumeLoading();
        });
};
mirosubs.widget.Widget.prototype.startSubtitling_ = 
    function(existingCaptions) 
{
    this.videoPlayer_.stopLoading();
    this.turnOffSubs_();
    var subtitleDialog = new mirosubs.subtitle.Dialog(
        this.videoSource_, 
        new mirosubs.subtitle.MSServerModel(
            this.videoID_, 0),
        existingCaptions);
    subtitleDialog.setVisible(true);
    this.dialog_ = subtitleDialog;
    var that = this;
    goog.events.listenOnce(
        subtitleDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
	    that.videoPlayer_.resumeLoading();
            if (subtitleDialog.isSaved()) {
                that.videoTab_.setText(
                    mirosubs.widget.VideoTab.Messages.CHOOSE_LANGUAGE);
// FIXME: this method is not implemented
//                that.popupMenu_.setSubtitled();
            }
        });
};
mirosubs.widget.Widget.prototype.editSubtitlesImpl_ = 
    function(version, existingCaptions) 
{
    this.videoPlayer_.stopLoading();
    this.turnOffSubs_();
    var dialog = new mirosubs.subtitle.Dialog(
        this.videoSource_,
        new mirosubs.subtitle.MSServerModel(
            this.videoID_, version),
        existingCaptions);
    dialog.setVisible(true);
    this.dialog_ = dialog;

    var that = this;
    goog.events.listenOnce(
        dialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
	    that.videoPlayer_.resumeLoading();
        });
};
mirosubs.widget.Widget.prototype.languageSelected_ = function(opt_languageCode) {
    // this clears out the base state.
    var lang = this.findLanguage_(opt_languageCode);
    var name = lang ? lang.name : null;
    this.state_ = new mirosubs.widget.ViewState(this, opt_languageCode, name);
    this.videoTab_.showLoading(true);
    this.videoTab_.showNudge(false);
    this.state_.initialize(goog.bind(this.subsLoaded_, this, opt_languageCode));
};

mirosubs.widget.Widget.prototype.turnOffSubs_ = function(event) {
    if (this.playManager_) {
        this.popupMenu_.setShowingSubs(false);
        this.videoTab_.setText("Subtitles Off");
        this.videoTab_.showNudge(false);
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
        this.videoPlayer_, subtitles,
        goog.bind(this.lastCaptionFinished_, this));
    
    var lang = this.findLanguage_(languageCode);
    if (lang != null && lang['percent_done'] < 100) {
        this.videoTab_.updateNudge("Finish this Translation",
                                   goog.bind(this.editSubtitles_, this));
        this.videoTab_.showNudge(true);
    }
    else {
        this.videoTab_.showNudge(false);
    }

    // FIXME: duplication with mirosubs.widget.ViewState
    var tabText = "Original Subtitles";
    if (lang)
        tabText = lang['name'] + " Subtitles";

    this.videoTab_.setText(tabText);
    this.popupMenu_.setCurrentLanguageCode(languageCode);
};

mirosubs.widget.Widget.prototype.lastCaptionFinished_ = function(evt) {
    if (!this.languageCodePlaying_) {
        this.videoTab_.updateNudge(
            "Improve these Subtitles",
            goog.bind(this.editSubtitles_, this));
        this.videoTab_.showNudge(true);
    }
};

mirosubs.widget.Widget.prototype.findLanguage_ = function(code) {
    return goog.array.find(
        this.popupMenu_.getTranslationLanguages(), 
        function(tl) {
            return tl.code == code;
        });
};
mirosubs.widget.Widget.prototype.addNewLanguageClicked_ = function() {
    if (!this.possiblyRedirectToOnsiteWidget_(false))
        this.addNewLanguage_();
};
mirosubs.widget.Widget.prototype.addNewLanguage_ = function() {
    this.videoTab_.showLoading(true);
    this.state_ = new mirosubs.widget.NewTranslationState(this, this.videoID_);
    this.state_.initialize(goog.bind(this.addNewLanguageResponseReceived_, this));
};

mirosubs.widget.Widget.prototype.addNewLanguageResponseReceived_ = 
    function(result) 
{
    this.videoTab_.showLoading(false);
    this.videoPlayer_.stopLoading();
    this.turnOffSubs_();
    var translationDialog = new mirosubs.translate.Dialog(
        this.videoSource_, this.videoID_, result['captions'], 
        result['languages']);
    translationDialog.setVisible(true);
    this.dialog_ = translationDialog;
    var that = this;
    goog.events.listenOnce(
        translationDialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(event) {
            that.dialog_ = null;
	    this.videoPlayer_.resumeLoading();
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

mirosubs.widget.Widget.prototype.getVideoId = function() {
    return this.videoID_;
};
