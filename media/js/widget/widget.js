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
 * @constructor
 * @param {Object} widgetConfig parameter documentation is currenty in embed.js.
 */
mirosubs.widget.Widget = function(widgetConfig) {
    goog.ui.Component.call(this);

    /**
     * @type {string}
     */
    this.videoURL_ = widgetConfig['video_url'];
    this.alternateVideoURLs_ = widgetConfig['alternate_video_urls'];
    this.forceFormat_ = !!widgetConfig['force_format'];
    this.videoConfig_ = widgetConfig['video_config'];
    /**
     * If true, this is the equivalent of clicking on "Add subtitles" 
     * if base state is null, or equivalent of clicking on "Improve 
     * these subtitles" if base state is not null.
     * @type {boolean}
     */
    this.subtitleImmediately_ = 
        !!widgetConfig['subtitle_immediately'];
    /**
     * If true, this is the equivalent of clicking on 
     * "Add New Translation"
     * @type {boolean}
     */
    this.translateImmediately_ =
        !!widgetConfig['translate_immediately'];
    var baseState = widgetConfig['base_state'];
    if (baseState)
        this.baseState_ = new mirosubs.widget.BaseState(baseState);
};
goog.inherits(mirosubs.widget.Widget, goog.ui.Component);

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

mirosubs.widget.Widget.prototype.createVideoPlayer_ = function(videoSource) {
    this.videoPlayer_ = videoSource.createPlayer();
    this.addChildAt(this.videoPlayer_, 0, true);
    this.setVideoDimensions_();
};

mirosubs.widget.Widget.prototype.findVideoSource_ = function() {
    if (this.alternateVideoURLs_ && this.alternateVideoURLs_.length > 0) {
        var mainVideoSpec = this.videoURL_;
        if (this.videoConfig_)
            mainVideoSpec = { 'url': this.videoURL_, 
                              'config': this.videoConfig_ };
        return mirosubs.video.VideoSource.bestVideoSource(
            goog.array.concat(mainVideoSpec, this.alternateVideoURLs_));
    }
    else
        return mirosubs.video.VideoSource.videoSourceForURL(
            this.videoURL_, this.videoConfig_);
};

mirosubs.widget.Widget.prototype.isVideoSourceImmediatelyUsable_ = 
    function() 
{
    if (this.videoSource_ instanceof mirosubs.video.BlipTVPlaceholder)
        return false;
    if (this.forceFormat_ || goog.isDefAndNotNull(this.alternateVideoURLs_))
        return true;
    else {
        if (this.videoSource_ instanceof mirosubs.video.Html5VideoSource)
            return this.videoSource_.isBestVideoSource();
        else
            return !mirosubs.video.supportsVideo();
    }
};

mirosubs.widget.Widget.prototype.addVideoLoadingPlaceholder_ = 
    function(el) 
{
    this.videoPlaceholder_ = this.getDomHelper().createDom(
        'div', 'mirosubs-videoLoading', 'Loading...');
    goog.dom.appendChild(el, this.videoPlaceholder_);
};

mirosubs.widget.Widget.prototype.addWidget_ = function(el) {
    try {
        this.videoSource_ = this.findVideoSource_();
    }
    catch (err) {
        // TODO: format this more.
        el.innerHTML = err.message;
        return;
    }
    if (this.isVideoSourceImmediatelyUsable_())
        this.createVideoPlayer_(this.videoSource_);
    else
        this.addVideoLoadingPlaceholder_(el);
    this.videoTab_ = new mirosubs.widget.VideoTab();
    var videoTabContainer = new goog.ui.Component();
    this.addChild(videoTabContainer, true);
    videoTabContainer.addChild(this.videoTab_, true);
    videoTabContainer.getElement().className = 
        'mirosubs-videoTab-container';
    this.videoTab_.showLoading();
    var args = {
        'video_url': this.videoURL_,
        'is_remote': mirosubs.isFromDifferentDomain()
    };
    if (this.baseState_)
        args['base_state'] = this.baseState_.ORIGINAL_PARAM;
    mirosubs.Rpc.call(
        'show_widget', args, 
        goog.bind(this.initializeState_, this),
        goog.bind(this.showWidgetError_, this));
};

mirosubs.widget.Widget.prototype.showWidgetError_ = function() {
    // call to show_widget timed out.
    if (!this.isVideoSourceImmediatelyUsable_()) {
        // waiting for video source from server.
        if (this.videoSource_ instanceof mirosubs.video.BlipTVPlaceholder) {
            // out of luck.
            
        }
        else {
            this.createVideoPlayer_(this.videoSource_);            
        }
    }
    this.videoTab_.showError();
};

mirosubs.widget.Widget.prototype.initializeState_ = function(result) {
    if (!this.isVideoSourceImmediatelyUsable_()) {
        goog.dom.removeNode(this.videoPlaceholder_);
        var videoSource = mirosubs.video.VideoSource.bestVideoSource(
            result['video_urls']);
        if (goog.typeOf(videoSource) == goog.typeOf(this.videoSource_) &&
            this.videoConfig_)
            videoSource.setVideoConfig(this.videoConfig_);
        this.videoSource_ = videoSource;
        this.createVideoPlayer_(this.videoSource_);
    }

    this.controller_ = new mirosubs.widget.WidgetController(
        this.videoURL_, this.videoPlayer_, this.videoTab_);
    this.controller_.initializeState(result);

    var subController = this.controller_.getSubtitleController();

    if (this.subtitleImmediately_)
        goog.Timer.callOnce(
            goog.bind(subController.openSubtitleDialog, subController));
    else if (this.translateImmediately_)
        goog.Timer.callOnce(
            goog.bind(subController_.openNewLanguageDialog, 
                      subController_));
};

mirosubs.widget.Widget.prototype.enterDocument = function() {
    mirosubs.widget.Widget.superClass_.enterDocument.call(this);
    this.setVideoDimensions_();
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

/**
 * Select a menu item. Either called by selecting 
 * a menu item or programmatically by js on the page.
 */
mirosubs.widget.Widget.prototype.selectMenuItem = function(selection, opt_languageCode) {
    var s = mirosubs.widget.DropDown.Selection;
    var subController = this.controller_.getSubtitleController();
    var playController = this.controller_.getPlayController();
    if (selection == s.ADD_LANGUAGE)
        subController.openNewLanguageDialog();
    else if (selection == s.IMPROVE_SUBTITLES)
        subController.openSubtitleDialog();
    else if (selection == s.SUBTITLE_HOMEPAGE)
        alert('subtitle homepage');
    else if (selection == s.SUBTITLES_OFF)
        playController.turnOffSubs();
    else if (selection == s.LANGUAGE_SELECTED)
        playController.languageSelected(opt_languageCode);
};
mirosubs.widget.Widget.prototype.playAt = function(time) {
    this.videoPlayer_.setPlayheadTime(time);
    this.videoPlayer_.play();
};