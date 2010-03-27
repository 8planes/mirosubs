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

goog.provide('mirosubs.subtitle.EditableCaption');

/**
 * @param {mirosubs.UnitOfWork} unitOfWork UnitOfWork through which changes to 
 *     this caption can be registered.
 * @param {JSONCaption} opt_jsonCaption optional JSON caption on which we're operating.
 *     Provide this parameter iff the caption exists already in the MiroSubs system.
 */
mirosubs.subtitle.EditableCaption = function(unitOfWork, opt_jsonCaption) {
    this.unitOfWork_ = unitOfWork;
    this.jsonCaption = opt_jsonCaption || 
        { 
            'caption_id' : new Date().getTime(),
            'caption_text' : '',
            'start_time' : -1,
            'end_time' : -1
        };
    if (!opt_jsonCaption)
        this.unitOfWork_.registerNew(this);
};

// TODO: get rid of repetition here, if possible.

mirosubs.subtitle.EditableCaption.prototype.setText = function(text) {
    this.jsonCaption['caption_text'] = text;
    this.unitOfWork_.registerUpdated(this);
};
mirosubs.subtitle.EditableCaption.prototype.getText = function() {
    return this.jsonCaption['caption_text'];
};
mirosubs.subtitle.EditableCaption.prototype.setStartTime = function(startTime) {
    this.jsonCaption['start_time'] = startTime;
    this.unitOfWork_.registerUpdated(this);
};
mirosubs.subtitle.EditableCaption.prototype.getStartTime = function() {
    return this.jsonCaption['start_time'];
};
mirosubs.subtitle.EditableCaption.prototype.setEndTime = function(endTime) {
    this.jsonCaption['end_time'] = endTime;
    this.unitOfWork_.registerUpdated(this);
};
mirosubs.subtitle.EditableCaption.prototype.getEndTime = function() {
    return this.jsonCaption['end_time'];
};
mirosubs.subtitle.EditableCaption.prototype.getCaptionID = function() {
    return this.jsonCaption['caption_id'];
};
mirosubs.subtitle.EditableCaption.prototype.isShownAt = function(time) {
    return this.getStartTime() < time && time < this.getEndTime();
};