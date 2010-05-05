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
 */
mirosubs.timeline.Timeline = function(spacing, captionSet) {
    goog.ui.Component.call(this);
    this.spacing_ = spacing;
    this.captionSet_ = captionSet;
    this.pixelsPerSecond_ = mirosubs.timeline.TimeRowUL.PX_PER_TICK / spacing;    
};
goog.inherits(mirosubs.timeline.Timeline, goog.ui.Component);
mirosubs.timeline.Timeline.prototype.createDom = function() {
    mirosubs.timeline.Timeline.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var el = this.getElement();
    el.className = 'mirosubs-timeline';
    el.appendChild($d('div', 'top', ' '));
    this.timelineInner_ = new mirosubs.timeline.TimelineInner(
        this.spacing_, this.captionSet_);
    this.addChild(this.timelineInner_, true);
    el.appendChild($d('div', 'marker'));
};
mirosubs.timeline.Timeline.prototype.enterDocument = function() {
    mirosubs.timeline.Timeline.superClass_.enterDocument.call(this);
    var size = goog.style.getSize(this.getElement());
    this.width_ = size.width;
};
mirosubs.timeline.Timeline.prototype.setTime = function(time) {
    this.timelineInner_.getElement().style.left = 
        (-time * this.pixelsPerSecond_ + this.width_ / 2) + 'px';
    this.timelineInner_.ensureVisible(time);
};
