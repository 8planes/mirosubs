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

goog.provide('mirosubs.timeline.Timeline');

/**
 *
 * @param {number} spacing The space, in seconds, between two 
 *     major ticks.
 * @param {mirosubs.timeline.SubtitleSet} subtitleSet
 */
mirosubs.timeline.Timeline = function(spacing, subtitleSet, videoPlayer) {
    goog.ui.Component.call(this);
    this.spacing_ = spacing;
    this.subtitleSet_ = subtitleSet;
    this.pixelsPerSecond_ = mirosubs.timeline.TimeRowUL.PX_PER_TICK / spacing;
    this.videoPlayer_ = videoPlayer;
};
goog.inherits(mirosubs.timeline.Timeline, goog.ui.Component);
mirosubs.timeline.Timeline.prototype.createDom = function() {
    mirosubs.timeline.Timeline.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var el = this.getElement();
    el.className = 'mirosubs-timeline';
    el.appendChild($d('div', 'top', ' '));
    this.timelineInner_ = new mirosubs.timeline.TimelineInner(
        this.spacing_, this.subtitleSet_);
    this.addChild(this.timelineInner_, true);
    el.appendChild($d('div', 'marker'));
};
mirosubs.timeline.Timeline.prototype.enterDocument = function() {
    mirosubs.timeline.Timeline.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.videoPlayer_,
        mirosubs.video.AbstractVideoPlayer.EventType.TIMEUPDATE,
        this.videoTimeUpdate_).
        listen(this.timelineInner_,
               goog.object.getValues(
                   mirosubs.timeline.TimelineSub.EventType),
               this.timelineSubEdit_);
    this.setTime_(this.videoPlayer_.getPlayheadTime());
};
mirosubs.timeline.Timeline.prototype.timelineSubEdit_ = function(e) {
    var et = mirosubs.timeline.TimelineSub.EventType;
    if (e.type == et.START_EDITING)
        this.videoPlayer_.pause();
    else if (e.type == et.FINISH_EDITING)
        this.videoPlayer_.playWithNoUpdateEvents(
            e.target.getSubtitle().getStartTime(), 2);
};
mirosubs.timeline.Timeline.prototype.videoTimeUpdate_ = function(e) {
    this.setTime_(this.videoPlayer_.getPlayheadTime());
};
mirosubs.timeline.Timeline.prototype.setTime_ = function(time) {
    if (!this.width_) {
        var size = goog.style.getSize(this.getElement());
        this.width_ = size.width;
    }
    this.timelineInner_.getElement().style.left = 
        (-time * this.pixelsPerSecond_ + this.width_ / 2) + 'px';
    this.timelineInner_.ensureVisible(time);
};
