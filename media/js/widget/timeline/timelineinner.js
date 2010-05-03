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

goog.provide('mirosubs.timeline.TimelineInner');


/**
 *
 * @param {number} spacing The space, in seconds, between two 
 *     major ticks.
 * @param {mirosubs.subtitle.EditableCaptionSet} captionSet
 */
mirosubs.timeline.TimelineInner = function(spacing, captionSet) {
    goog.ui.Component.call(this);
    this.spacing_ = spacing;
    this.captionSet_ = captionSet;
};
goog.inherits(mirosubs.timeline.TimelineInner, goog.ui.Component);
mirosubs.timeline.TimelineInner.prototype.createDom = function() {
    mirosubs.timeline.TimelineInner.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-timeline-inner';
    this.timerow_ = new mirosubs.timeline.TimeRow(this.spacing_);
    this.addChild(this.timerow_, true);
    this.timelineSubs_ = new mirosubs.timeline.TimelineSubs(
        this.captionSet_,
        mirosubs.timeline.TimeRowUL.PX_PER_TICK / this.spacing_);
    this.addChild(this.timelineSubs_, true);
};
mirosubs.timeline.TimelineInner.prototype.ensureVisible = function(time) {
    this.timerow_.ensureVisible(time);
};