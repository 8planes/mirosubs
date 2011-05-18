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

goog.provide('mirosubs.video.JWVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.YoutubeVideoSource} videoSource
 */
mirosubs.video.JWVideoPlayer = function(videoSource) {
    mirosubs.video.FlashVideoPlayer.call(this, videoSource);
    this.logger_ = goog.debug.Logger.getLogger('mirosubs.video.JWPlayer');
    this.stateListener_ = 'jwevent' + mirosubs.randomString();
    this.timeListener_ = 'jwtime' + mirosubs.randomString();
    this.playheadTime_ = 0;
    mirosubs.video.JWVideoPlayer.players_.push(this);
};
goog.inherits(mirosubs.video.JWVideoPlayer, 
              mirosubs.video.FlashVideoPlayer);

mirosubs.video.JWVideoPlayer.players_ = [];
mirosubs.video.JWVideoPlayer.playerReadyCalled_ = false;

mirosubs.video.JWVideoPlayer.prototype.onJWPlayerReady_ = function(elem) {
    if (goog.DEBUG) {
        this.logger_.info('player ready');
    }
    this.tryDecoratingAll();
};

mirosubs.video.JWVideoPlayer.prototype.decorateInternal = function(elem) {
    mirosubs.video.JWVideoPlayer.superClass_.decorateInternal.call(this, elem);
    this.playerSize_ = goog.style.getSize(this.getElement());
    this.setDimensionsKnownInternal();
    if (goog.DEBUG) {
        this.logger_.info(
            "playerReadyCalled_: " +
                mirosubs.video.JWVideoPlayer.playerReadyCalled_);
    }
    if (mirosubs.video.JWVideoPlayer.playerReadyCalled_)
        this.onJWPlayerReady_();
};

mirosubs.video.JWVideoPlayer.prototype.isFlashElementReady = function(elem) {
    return elem['addModelListener'];
};

mirosubs.video.JWVideoPlayer.prototype.setFlashPlayerElement = function(element) {
    this.player_ = element;
    this.playerSize_ = goog.style.getSize(this.player_);
    this.setDimensionsKnownInternal();
    window[this.stateListener_] = goog.bind(this.playerStateChanged_, this);
    window[this.timeListener_] = goog.bind(this.playerTimeChanged_, this);
    this.player_['addModelListener']('STATE', this.stateListener_);
    this.player_['addModelListener']('TIME', this.timeListener_);
};
mirosubs.video.JWVideoPlayer.prototype.getVideoSize = function() {
    return this.playerSize_;
};
mirosubs.video.JWVideoPlayer.prototype.playerStateChanged_ = function(data) {
    var newState = data['newstate'];
    if (goog.DEBUG) {
        this.logger_.info('statechanged: ' + newState);
    }
    var et = mirosubs.video.AbstractVideoPlayer.EventType;
    var s = mirosubs.video.JWVideoPlayer.State_;
    if (newState == s.PLAYING) {
        this.dispatchEvent(et.PLAY);
    } else if (newState == s.PAUSED) {
        this.dispatchEvent(et.PAUSE);
    } else if (newState == s.COMPLETED) {
        this.dispatchEndedEvent();
    }
};
mirosubs.video.JWVideoPlayer.prototype.playerTimeChanged_ = function(data) {
    this.playheadTime_ = data['position'];
    if (!this.duration_)
        this.duration_ = data['duration'];    
    this.dispatchEvent(
        mirosubs.video.AbstractVideoPlayer.EventType.TIMEUPDATE);
};
mirosubs.video.JWVideoPlayer.prototype.exitDocument = function() {
    mirosubs.video.JWVideoPlayer.superClass_.exitDocument.call(this);
    this.player_['removeModelListener']('STATE', this.stateListener_);
    this.player_['removeModelListener']('TIME', this.timeListener_);
};
mirosubs.video.JWVideoPlayer.prototype.getDuration = function() {
    return this.duration_;
};
mirosubs.video.JWVideoPlayer.prototype.isPausedInternal = function() {
    // TODO: write me
};
mirosubs.video.JWVideoPlayer.prototype.videoEndedInternal = function() {
    // TODO: write me
};
mirosubs.video.JWVideoPlayer.prototype.isPausedInternal = function() {
    // TODO: write me
};
mirosubs.video.JWVideoPlayer.prototype.playInternal = function() {
    this.sendEvent_('play', ['true']);
};
mirosubs.video.JWVideoPlayer.prototype.pauseInternal = function() {
    this.sendEvent_('play', ['false']);
};
mirosubs.video.JWVideoPlayer.prototype.stopLoadingInternal = function() {
    // TODO: implement this for real.
    this.pause();
    if (goog.DEBUG) {
        this.logger_.info('stopLoadingInternal called');
    }
};
mirosubs.video.JWVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime) {
    // TODO: implement this for real at some point.
    if (goog.DEBUG) {
        this.logger_.info('resumeLoadingInternal called');
    }
};
mirosubs.video.JWVideoPlayer.prototype.getPlayheadTime = function() {
    return this.playheadTime_;
};
mirosubs.video.JWVideoPlayer.prototype.needsIFrame = function() {
    return goog.userAgent.LINUX;
};
mirosubs.video.JWVideoPlayer.prototype.getVideoElement = function() {
    return this.player_;
};
mirosubs.video.JWVideoPlayer.prototype.sendEvent_ = function(event, args) {
    // TODO: prob check to see if this.player_ exists yet; if not, queue the
    // command.
    if (goog.DEBUG) {
        this.logger_.info(
            'sendEvent_ called with ' + event + ' and args ' +
                args.join(', '));
    }
    this.player_['sendEvent'].apply(this.player_, goog.array.concat(event, args));
};

mirosubs.video.JWVideoPlayer.State_ = {
    PLAYING: 'PLAYING',
    PAUSED: 'PAUSED',
    COMPLETED: 'COMPLETED'
};

mirosubs.video.JWVideoPlayer.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.video.JWVideoPlayerStatic');

(function() {
    var jwReady = "playerReady";
    var oldReady = window[jwReady] || goog.nullFunction;
    window[jwReady] = function(obj) {
        try {
            oldReady(obj);
        }
        catch (e) {
            // don't care
        }
        mirosubs.video.JWVideoPlayer.playerReadyCalled_ = true;
        if (goog.DEBUG) {
            mirosubs.video.JWVideoPlayer.logger_.info(
                "Number of players: " + 
                    mirosubs.video.JWVideoPlayer.players_.length);
        }
        goog.array.forEach(
            mirosubs.video.JWVideoPlayer.players_, 
            function(p) { p.onJWPlayerReady_(); });
    };
})();