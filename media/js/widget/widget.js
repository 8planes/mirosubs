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
 * @private
 */
mirosubs.widget.Widget = function() {};

mirosubs.widget.Widget.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.widget.Widget');

/**
 * @type {!string}
 */
mirosubs.widget.Widget.prototype.videoURL_ = undefined;
/**
 * @type {Object.<string, *>}
 */
mirosubs.widget.Widget.prototype.videoConfig_ = null;

/**
 * If true, this is the equivalent of clicking on "Add subtitles" 
 * if base state is null, or equivalent of clicking on "Improve 
 * these subtitles" if base state is not null.
 * @type {boolean}
 */
mirosubs.widget.Widget.prototype.subtitleImmediately_ = false;

/**
 * If true, this is the equivalent of clicking on 
 * "Add New Translation"
 * @type {boolean}
 */
mirosubs.widget.Widget.prototype.translateImmediately_ = false;

/**
 * 
 * @type {mirosubs.widget.BaseState}
 */
mirosubs.widget.Widget.prototype.baseState_ = null;

/**
 *
 * @type {mirosubs.video.AbstractVideoPlayer}
 */
mirosubs.widget.Widget.prototype.videoPlayer_ = null;

/**
 * Container in which video player should be placed.
 * @type {?Element}
 */
mirosubs.widget.Widget.prototype.container_ = null;

/**
 * Called to create a video player with tab and add it to the page.
 * @param {Element} element Empty element to decorate, probably div.
 * @param {Object.<string, *>} widgetConfig widget params
 *
 */
mirosubs.widget.Widget.decorateContainer = function(element, widgetConfig) {
    var widget = new mirosubs.widget.Widget();
    widget.videoURL_ = widgetConfig['video_url'];
    widget.videoConfig_ = widgetConfig['video_config'];
    widget.subtitleImmediately_ =
        !!widgetConfig['subtitle_immediately'];
    widget.translateImmediately_ =
        !!widgetConfig['translate_immediately'];
    var baseState = widgetConfig['base_state'];
    if (baseState)
        widget.baseState_ = new mirosubs.widget.BaseState(baseState);
    return widget;
};

/**
 * Called to decorate a video player that's already on the page. 
 * The video player must meet the proper criteria (e.g. js api 
 * enabled for youtube)
 * @param {mirosubs.video.AbstractVideoPlayer} player This player
 *     should already be in the page, probably by calling decorate.
 * @return {mirosubs.widget.Widget}
 */
mirosubs.widget.Widget.decoratePlayer = function(player) {
    var widget = new mirosubs.widget.Widget();
    widget.videoURL_ = player.getVideoSource().getVideoURL();
    mirosubs.widget.Widget.logger_.info('video url is ' + widget.videoURL);
    widget.videoPlayer_ = player;
    return widget;
};

mirosubs.widget.Widget.prototype.setVideoSource_ = function(videoSource) {
    this.videoPlayer_ = videoSource.createPlayer();
    this.addChildAt(this.videoPlayer_, 0, true);
    this.setVideoDimensions_();
};

mirosubs.widget.Widget.prototype.addWidget_ = function(el) {
    var videoSource = null;
    try {
        videoSource = mirosubs.video.VideoSource.videoSourceForURL(
            this.videoURL_, this.videoConfig_);
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
    this.videoTab_.showLoading();
    var args = {
        'video_url': this.videoURL_,
        'is_remote': mirosubs.isFromDifferentDomain()
    };
    if (this.baseState_)
        args['base_state'] = this.baseState_.ORIGINAL_PARAM;
    mirosubs.Rpc.call(
        'show_widget', args, goog.bind(this.initializeState_, this));
};

mirosubs.widget.Widget.prototype.initializeState_ = function(result) {
    this.makeGeneralSettings_(result);

    var videoID = result['video_id'];

    if (result['flv_url'] && !this.videoSource_)
        this.setVideoSource_(new mirosubs.video.FlvVideoSource(
            result['flv_url']));

    var dropDownContents = mirosubs.widget.DropDownContents.fromJSON(
        result['drop_down_contents']);
    var subtitleState = mirosubs.widget.SubtitleState.fromJSON(
        result['subtitles']);

    var popupMenu = new mirosubs.widget.DropDown(
        videoID, dropDownContents, this.videoTab_);

    this.videoTab_.showContent(popupMenu.hasSubtitles(),
                               subtitleState);

    popupMenu.render(this.getDomHelper().getDocument().body);
    goog.style.showElement(popupMenu.getElement(), false);

    popupMenu.setCurrentSubtitleState(subtitleState);

    this.playController_ = new mirosubs.widget.PlayController(
        videoID, this.videoSource_, this.videoPlayer_, 
        this.videoTab_, popupMenu, subtitleState);

    this.subtitleController_ = new mirosubs.widget.SubtitleController(
        videoID, this.videoURL_, 
        this.playController_, this.videoTab_, popupMenu);

    if (this.subtitleImmediately_)
        goog.Timer.callOnce(
            goog.bind(this.subtitleController_.openSubtitleDialog, 
                      this.subtitleController_));
    else if (this.translateImmediately_)
        goog.Timer.callOnce(
            goog.bind(this.subtitleController_.openNewLanguageDialog,
                      this.subtitleController_));
};

mirosubs.widget.Widget.prototype.makeGeneralSettings_ = function(result) {
    if (result['username'])
        mirosubs.currentUsername = result['username'];
    mirosubs.embedVersion = result['embed_version'];
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        result["writelock_expiration"];
    mirosubs.languages = result['languages'];
    mirosubs.metadataLanguages = result['metadata_languages'];
    var sortFn = function(a, b) { 
        return a[1] > b[1] ? 1 : a[1] < b[1] ? -1 : 0
    };
    goog.array.sort(mirosubs.languages, sortFn);
    goog.array.sort(mirosubs.metadataLanguages, sortFn);
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
    if (selection == s.ADD_LANGUAGE)
        this.subtitleController_.openNewLanguageDialog();
    else if (selection == s.IMPROVE_SUBTITLES)
        this.subtitleController_.openSubtitleDialog();
    else if (selection == s.SUBTITLE_HOMEPAGE)
        alert('subtitle homepage');
    else if (selection == s.SUBTITLES_OFF)
        this.playController_.turnOffSubs();
    else if (selection == s.LANGUAGE_SELECTED)
        this.playController_.languageSelected(opt_languageCode);
};
mirosubs.widget.Widget.prototype.playAt = function(time) {
    this.videoPlayer_.setPlayheadTime(time);
    this.videoPlayer_.play();
};