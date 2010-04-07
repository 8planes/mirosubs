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



goog.provide('mirosubs.AbstractVideoPlayer');

/**
 * Abstract base class for video player implementations. Any video player 
 * used with MiroSubs must implement the abstract methods defined by this 
 * class.
 * @constructor
 */
mirosubs.AbstractVideoPlayer = function(videoSource) {
    goog.ui.Component.call(this);
    this.videoSource_ = videoSource;
};
goog.inherits(mirosubs.AbstractVideoPlayer, goog.ui.Component);

mirosubs.AbstractVideoPlayer.prototype.getPlayheadFn = function() {
    return goog.bind(this.getPlayheadTime, this);
};
mirosubs.AbstractVideoPlayer.prototype.createDom = function() {
    mirosubs.AbstractVideoPlayer.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-videoDiv';
};
mirosubs.AbstractVideoPlayer.prototype.isPaused = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.isPlaying = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.videoEnded = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.play = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.pause = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.togglePause = function() {
    if (this.isPaused() || this.videoEnded())
        this.play();
    else
        this.pause();
};
mirosubs.AbstractVideoPlayer.prototype.getPlayheadTime = goog.abstractMethod;
mirosubs.AbstractVideoPlayer.prototype.getVideoSource = function() {
    return this.videoSource_;
};
mirosubs.AbstractVideoPlayer.prototype.setPlayheadTime = function(playheadTime) {
    goog.abstractMethod();
};
/**
 *
 * @param {String} text Caption text to display in video. null for blank.
 */
mirosubs.AbstractVideoPlayer.prototype.showCaptionText = function(text) {
    if (text == null || text == "") {
        if (this.captionElem_ != null) {
            this.getElement().removeChild(this.captionElem_);
            this.captionElem_ = null;
            if (this.captionBgElem_ != null) {
                this.getElement().removeChild(this.captionBgElem_);
                this.captionBgElem_ = null;
            }
        }
    }
    else {
        var needsIFrame = this.needsIFrame();
        if (this.captionElem_ == null) {
            this.captionElem_ = document.createElement("div");
            this.captionElem_.setAttribute("class", "mirosubs-captionDiv");
            var videoSize = this.getVideoSize();
            this.captionElem_.style.top = (videoSize.height - 60) + "px";
            if (needsIFrame)
                this.captionElem_.style.visibility = 'hidden';
            this.getElement().appendChild(this.captionElem_);
        }
        goog.dom.setTextContent(this.captionElem_, text);
        if (needsIFrame) {
            var $d = goog.dom;
            var $s = goog.style;
            if (this.captionBgElem_ == null) {
                this.captionBgElem_ = document.createElement('iframe');
                this.captionBgElem_.setAttribute("class", "mirosubs-captionDivBg");
                this.captionBgElem_.style.visibility = 'hidden';
                this.captionBgElem_.style.top = this.captionElem_.style.top;
                // FIXME: get rid of hardcoded value
                this.captionBgElem_.style.left = "10px";
                $d.insertSiblingBefore(this.captionBgElem_, 
                                       this.captionElem_);
            }
            var size = $s.getSize(this.captionElem_);
            $s.setSize(this.captionBgElem_, size.width, size.height);
            this.captionBgElem_.style.visibility = 'visible';
            this.captionElem_.style.visibility = 'visible';
        }
    }
};
/**
 * Override for video players that need to show an iframe behind captions for 
 * certain browsers (e.g. flash on linux/ff)
 * @protected
 */
mirosubs.AbstractVideoPlayer.prototype.needsIFrame = function() {
    return false;
};
/**
 *
 * @protected
 * @return {goog.math.Size} size of the video
 */
mirosubs.AbstractVideoPlayer.prototype.getVideoSize = goog.abstractMethod;

/**
 * Video player events
 * @enum {string}
 */
mirosubs.AbstractVideoPlayer.EventType = {
    /** dispatched when playback starts or resumes. */
    PLAY : 'videoplay',
    /** dispatched when playback is paused. */
    PAUSE : 'videopause'
};