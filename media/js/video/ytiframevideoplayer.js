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

goog.provide('mirosubs.video.YTIFrameVideoPlayer');

/**
 * @constructor
 */
mirosubs.video.YTIFrameVideoPlayer = function(videoSource, opt_forDialog) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);
    this.player_ = null;
    this.videoSource_ = videoSource;
    this.playerElemID_ = mirosubs.randomString() + "_ytplayer";
    this.forDialog_ = !!opt_forDialog;
    this.commands_ = [];
    this.progressTimer_ = new goog.Timer(
        mirosubs.video.AbstractVideoPlayer.PROGRESS_INTERVAL);
    this.timeUpdateTimer_ = new goog.Timer(
        mirosubs.video.AbstractVideoPlayer.TIMEUPDATE_INTERVAL);
    this.logger_ = goog.debug.Logger.getLogger(
        'mirosubs.video.YTIFrameVideoPlayer');
    goog.mixin(mirosubs.video.YTIFrameVideoPlayer.prototype,
               mirosubs.video.YoutubeBaseMixin.prototype);
};
goog.inherits(mirosubs.video.YTIFrameVideoPlayer, mirosubs.video.AbstractVideoPlayer);

mirosubs.video.YTIFrameVideoPlayer.prototype.createDom = function() {
    mirosubs.video.YTIFrameVideoPlayer.superClass_.createDom.call(this);
    this.setPlayerSize_();
    var embedUri = new goog.Uri(
        "http://youtube.com/embed/" + 
            this.videoSource_.getYoutubeVideoID());
    this.addQueryString_(embedUri);
    this.iframe_ = this.getDomHelper().createDom(
        'iframe', 
        { 'id': this.playerElemID_,
          'type': 'text/html',
          'width': this.playerSize_.width + '',
          'height': this.playerSize_.height + '', 
          'src': embedUri.toString(),
          'frameborder': '0'});
    this.setElementInternal(this.iframe_);
};

mirosubs.video.YTIFrameVideoPlayer.prototype.addQueryString_ = function(uri) {
    var config = this.videoSource_.getVideoConfig();
    if (!this.forDialog_ && config) {
        for (var prop in config) {
            if (prop != 'width' && prop != 'height')
                uri.setParameterValue(prop, config[prop]);
        }
    }
    var locationUri = new goog.Uri(window.location);
    var domain = window.location.protocol + "//" + 
        locationUri.getDomain() + 
        (locationUri.getPort() != 80 ? (':' + locationUri.getPort()) : '');
    uri.setParameterValue('enablejsapi', '1').
        setParameterValue('origin', domain).
        setParameterValue('wmode', 'opaque');
    if (this.forDialog_) {
        uri.setParameterValue('disablekb', '1').
            setParameterValue('controls', '0');
    }
};

mirosubs.video.YTIFrameVideoPlayer.prototype.setPlayerSize_ = function() {
    var sizeFromConfig = this.videoSource_.sizeFromConfig();
    if (!this.forDialog_ && sizeFromConfig)
        this.playerSize_ = sizeFromConfig;
    else
        this.playerSize_ = this.forDialog_ ?
        mirosubs.video.AbstractVideoPlayer.DIALOG_SIZE :
        mirosubs.video.AbstractVideoPlayer.DEFAULT_SIZE;
    this.setDimensionsKnownInternal();
};

mirosubs.video.YTIFrameVideoPlayer.prototype.decorateInternal = function(elem) {
    mirosubs.video.YTIFrameVideoPlayer.superClass_.decorateInternal.call(this, elem);
    this.logger_.info('decorating');
    this.iframe_ = elem;
    if (elem.id) {
        this.playerElemID_ = elem.id;
    }
    else {
        elem.id = this.playerElemID_;
    }
    this.playerSize_ = new goog.math.Size(
        parseInt(elem['width']), parseInt(elem['height']));
    this.setDimensionsKnownInternal();
};

mirosubs.video.YTIFrameVideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.YTIFrameVideoPlayer.superClass_.enterDocument.call(this);
    var w = window;
    if (w['YT'] && w['YT']['Player'])
        this.makePlayer_();
    else {
        var readyFunc = "onYouTubePlayerAPIReady";
        var oldReady = goog.nullFunction;
        if (w[readyFunc])
            oldReady = w[readyFunc];
        var myOnReady = goog.bind(this.makePlayer_, this);
        window[readyFunc] = function() {
            oldReady();
            myOnReady();
        };
        mirosubs.addScript("http://www.youtube.com/player_api");
    }
};

mirosubs.video.YTIFrameVideoPlayer.prototype.makePlayer_ = function() {
    if (goog.DEBUG) {
        this.logger_.info('makePlayer_ called');
    }
    var playerStateChange = goog.bind(this.playerStateChange_, this);
    this.almostPlayer_ = new window['YT']['Player'](
        this.playerElemID_, {
            'events': {
                'onReady': goog.bind(this.playerReady_, this),
                'onStateChange': function(state) {
                    playerStateChange(state['data']);
                }
            }
        });
};

mirosubs.video.YTIFrameVideoPlayer.prototype.playerReady_ = function(e) {
    this.logger_.info('player ready');
    this.player_ = this.almostPlayer_;
    goog.array.forEach(this.commands_, function(cmd) { cmd(); });
    this.commands_ = [];
    this.getHandler().
        listen(this.progressTimer_, goog.Timer.TICK, this.progressTick_).
        listen(this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
    this.progressTimer_.start();
};

mirosubs.video.YTIFrameVideoPlayer.prototype.getVideoElements = function() {
    return [this.iframe_];
};

mirosubs.video.YTIFrameVideoPlayer.prototype.disposeInternal = function() {
    mirosubs.video.YTIFrameVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
};

mirosubs.video.YTIFrameVideoPlayer.prototype.exitDocument = function() {
    mirosubs.video.YTIFrameVideoPlayer.superClass_.exitDocument.call(this);
    this.progressTimer_.stop();
    this.timeUpdateTimer_.stop();
};
