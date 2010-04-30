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

goog.provide('mirosubs.timeline.TimeRow');

mirosubs.timeline.TimeRow = function(spacing) {
    goog.ui.Component.call(this);
    this.spacing_ = spacing;
    /**
     * Set to non-null value iff not entered document yet and time is set.
     * @type {?number}
     */
    this.startTime_ = null;
};
goog.inherits(mirosubs.timeline.TimeRow, goog.ui.Component);
mirosubs.timeline.TimeRow.logger_ =
    goog.debug.Logger.getLogger('mirosubs.timeline.TimeRow');
mirosubs.timeline.TimeRow.prototype.enterDocument = function() {
    mirosubs.timeline.TimeRow.superClass_.enterDocument.call(this);
    var size = goog.style.getSize(this.getElement());
    this.width_ = size.width;
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.row_ = new mirosubs.timeline.TimeRowUL($d, this.spacing_);
    this.getElement().appendChild(this.row_.getElement());
    this.sideBufferSeconds_ = this.width_ * this.spacing_ / 
        (2 * mirosubs.timeline.TimeRowUL.PX_PER_TICK) + 1;

    mirosubs.timeline.TimeRow.logger_.info(
        "Side buffer seconds set at " + this.sideBufferSeconds_);

    if (this.startTime_ != null)
        this.setTime(this.startTime_);
    this.startTime_ = null;
};
/**
 * @param {number} time in seconds
 */
mirosubs.timeline.TimeRow.prototype.setTime = function(time) {
    if (!this.isInDocument()) {
        this.startTime_ = time;
        return;
    }
    if (this.row_.getFirstTime() == null || 
        (this.row_.getFirstTime() > this.sideBufferSeconds_ &&
         time < this.row_.getFirstTime() + this.sideBufferSeconds_) || 
        time >= this.row_.getLastTime() - this.sideBufferSeconds_ )
    {
        mirosubs.timeline.TimeRow.logger_.info(
            "Reset occurring at " + time);
        this.row_.setFirstTime(time - 
                               mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS *
                               this.spacing_ / 4);
        this.setTime(time);
    }
    else {       
        // just need to shift pixel position.
        this.row_.getElement().style.marginLeft = 
            (this.width_ / 2 - 
             mirosubs.timeline.TimeRowUL.PX_PER_TICK * 
             (time - this.row_.getFirstTime()) / this.spacing_) + 'px';
    }
};
