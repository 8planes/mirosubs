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
 * Don't call this constructor directly. Instead call the factory method in
 * mirosubs.subtitle.EditableCaptionSet.
 *
 * @constructor
 * @param {Number=} opt_subOrder Order in which this sub appears. Provide
 *    this parameter iff the caption doesn't exist in the MiroSubs
 *    system.
 * @param {JSONCaption=} opt_jsonCaption optional JSON caption on which
 *     we're operating. Provide this parameter iff the caption exists
 *     already in the MiroSubs system.
 */
mirosubs.subtitle.EditableCaption = function(opt_subOrder, opt_jsonCaption) {
    goog.events.EventTarget.call(this);
    this.json = opt_jsonCaption ||
        {
            'subtitle_id' : mirosubs.randomString(),
            'text' : '',
            'start_time' : mirosubs.subtitle.EditableCaption.TIME_UNDEFINED,
            'end_time' : mirosubs.subtitle.EditableCaption.TIME_UNDEFINED,
            'sub_order' : opt_subOrder
        };
    this.previousCaption_ = null;
    this.nextCaption_ = null;
};
goog.inherits(mirosubs.subtitle.EditableCaption, goog.events.EventTarget);

mirosubs.subtitle.EditableCaption.prototype.fork = function(jsonSub) {
    this.json['sub_order'] = jsonSub['sub_order'];
    this.json['start_time'] = jsonSub['start_time'];
    this.json['end_time'] = jsonSub['end_time'];
};

mirosubs.subtitle.EditableCaption.orderCompare = function(a, b) {
    return a.getSubOrder() - b.getSubOrder();
};

/*
 * @const
 * @type {int} 
 */
mirosubs.subtitle.EditableCaption.TIME_UNDEFINED = -1;
mirosubs.subtitle.EditableCaption.TIME_UNDEFINED_SERVER = (100 * 60 * 60) -1;

mirosubs.subtitle.EditableCaption.isTimeUndefined = function(v){
    return !goog.isDefAndNotNull(v) || 
        v == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ||
        v == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED_SERVER || false;
}
mirosubs.subtitle.EditableCaption.CHANGE = 'captionchanged';

/**
 * Minimum subtitle length, in seconds.
 */
mirosubs.subtitle.EditableCaption.MIN_LENGTH = 0.5;

/**
 * @param {mirosubs.subtitle.EditableCaption} caption Previous caption in list.
 *
 */
mirosubs.subtitle.EditableCaption.prototype.setPreviousCaption =
    function(caption)
{
    this.previousCaption_ = caption;
};
mirosubs.subtitle.EditableCaption.prototype.getPreviousCaption = function() {
    return this.previousCaption_;
};
/**
 * @param {mirosubs.subtitle.EditableCaption} caption Next caption in list.
 *
 */
mirosubs.subtitle.EditableCaption.prototype.setNextCaption =
    function(caption)
{
    this.nextCaption_ = caption;
};
mirosubs.subtitle.EditableCaption.prototype.getNextCaption = function() {
    return this.nextCaption_;
};
mirosubs.subtitle.EditableCaption.prototype.identicalTo = function(other) {
    return this.getSubOrder() == other.getSubOrder() &&
        this.getTrimmedText() == other.getTrimmedText() &&
        this.getStartTime() == other.getStartTime() &&
        this.getEndTime() == other.getEndTime() &&
        this.getCaptionID() == other.getCaptionID();
};
mirosubs.subtitle.EditableCaption.prototype.getSubOrder = function() {
    return this.json['sub_order'];
};
mirosubs.subtitle.EditableCaption.prototype.setText = function(text, opt_dontTrack) {
    this.json['text'] = text;
    this.changed_(false, opt_dontTrack);
};
mirosubs.subtitle.EditableCaption.prototype.getText = function() {
    return this.json['text'];
};
mirosubs.subtitle.EditableCaption.prototype.getTrimmedText = function() {
    return goog.string.trim(this.json['text']);
};
mirosubs.subtitle.EditableCaption.prototype.setStartTime =
    function(startTime)
{
    var previousStartTime = this.getStartTime();
    this.setStartTime_(startTime);
    this.changed_(previousStartTime == 
                  mirosubs.subtitle.EditableCaption.TIME_UNDEFINED);
};
mirosubs.subtitle.EditableCaption.prototype.setStartTime_ =
    function(startTime)
{
    startTime = Math.max(startTime, this.getMinStartTime());
    this.json['start_time'] = startTime;
    if (this.getEndTime() != mirosubs.subtitle.EditableCaption.TIME_UNDEFINED &&
        this.getEndTime() < startTime +
        mirosubs.subtitle.EditableCaption.MIN_LENGTH)
        this.setEndTime_(
            startTime + mirosubs.subtitle.EditableCaption.MIN_LENGTH);
    if (this.previousCaption_ &&
        (this.previousCaption_.getEndTime() == 
         mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ||
         this.previousCaption_.getEndTime() > startTime))
         this.previousCaption_.setEndTime(startTime);
};
mirosubs.subtitle.EditableCaption.prototype.getStartTime = function() {
    if (goog.isDefAndNotNull(this.json['start_time'])) {
        return this.json['start_time'];
    }
    else {
        return mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
    }
};
mirosubs.subtitle.EditableCaption.prototype.setEndTime =
    function(endTime)
{
    this.setEndTime_(endTime);
    this.changed_(false);
};
mirosubs.subtitle.EditableCaption.prototype.setEndTime_ =
    function(endTime)
{
    this.json['end_time'] = endTime;
    if (this.getStartTime() > endTime -
        mirosubs.subtitle.EditableCaption.MIN_LENGTH)
        this.setStartTime_(
            endTime - mirosubs.subtitle.EditableCaption.MIN_LENGTH);
    if (this.nextCaption_ &&
        this.nextCaption_.getStartTime() != 
        mirosubs.subtitle.EditableCaption.TIME_UNDEFINED &&
        this.nextCaption_.getStartTime() < endTime)
        this.nextCaption_.setStartTime(endTime);
};
/**
 * Clears times. Does not issue a CHANGE event.
 */
mirosubs.subtitle.EditableCaption.prototype.clearTimes = function() {
    if (this.getStartTime() != mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ||
        this.getEndTime() != mirosubs.subtitle.EditableCaption.TIME_UNDEFINED) {
        this.json['start_time'] = mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
        this.json['end_time'] = mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
    }
};
mirosubs.subtitle.EditableCaption.prototype.getEndTime = function() {
    if (goog.isDefAndNotNull(this.json['end_time'])) {
        return this.json['end_time'];
    }
    else {
        return mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
    }
};
mirosubs.subtitle.EditableCaption.prototype.getMinStartTime = function() {
    return this.previousCaption_ ?
        (this.previousCaption_.getStartTime() +
         mirosubs.subtitle.EditableCaption.MIN_LENGTH) : 0;
};
mirosubs.subtitle.EditableCaption.prototype.getMaxStartTime = function() {
    if (this.getEndTime() == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED)
        return 99999;
    else
        return this.getEndTime() -
            mirosubs.subtitle.EditableCaption.MIN_LENGTH;
};
mirosubs.subtitle.EditableCaption.prototype.getMinEndTime = function() {
    return this.getStartTime() + mirosubs.subtitle.EditableCaption.MIN_LENGTH;
};
mirosubs.subtitle.EditableCaption.prototype.getMaxEndTime = function() {
    return this.nextCaption_ && this.nextCaption_.getEndTime() != 
        mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ?
        (this.nextCaption_.getEndTime() -
         mirosubs.subtitle.EditableCaption.MIN_LENGTH) : 99999;
};
mirosubs.subtitle.EditableCaption.prototype.getCaptionID = function() {
    return this.json['subtitle_id'];
};
mirosubs.subtitle.EditableCaption.prototype.isShownAt = function(time) {
    return this.getStartTime() <= time &&
        (this.getEndTime() == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ||
            time < this.getEndTime());
};
mirosubs.subtitle.EditableCaption.prototype.hasStartTimeOnly = function() {
    return this.getStartTime() != mirosubs.subtitle.EditableCaption.TIME_UNDEFINED &&
        this.getEndTime() == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
};

/*
 * @return {boolean} True if either startTime or endTime is not defined.
 */
mirosubs.subtitle.EditableCaption.prototype.needsSync = function() {
    return this.getStartTime() == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED ||
        this.getEndTime() == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED;
}

mirosubs.subtitle.EditableCaption.prototype.changed_ =
    function(timesFirstAssigned, opt_dontTrack)
{
    if (!opt_dontTrack)
        mirosubs.SubTracker.getInstance().trackEdit(this.getCaptionID());
    this.dispatchEvent(
        new mirosubs.subtitle.EditableCaption.ChangeEvent(
            timesFirstAssigned));
};

mirosubs.subtitle.EditableCaption.adjustUndefinedTiming = function(json) {
    if (!json['start_time'] || json['start_time'] == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED){
        json['start_time'] = mirosubs.subtitle.EditableCaption.TIME_UNDEFINED_SERVER;
    }
    if (!json['end_time'] || json['end_time'] == mirosubs.subtitle.EditableCaption.TIME_UNDEFINED){
        json['end_time'] = mirosubs.subtitle.EditableCaption.TIME_UNDEFINED_SERVER;
    }
    return json;
};

mirosubs.subtitle.EditableCaption.toJsonArray = function(editableCaptions) {
    return goog.array.map(
        editableCaptions, 
        function(editableCaption) {
            return mirosubs.subtitle.EditableCaption.adjustUndefinedTiming(editableCaption.json);
        });
};
mirosubs.subtitle.EditableCaption.toIDArray = function(editableCaptions) {
    return goog.array.map(
        editableCaptions,
        function(ec) {
            return ec.getCaptionID();
        });
};


/**
 * @constructor
 */
mirosubs.subtitle.EditableCaption.ChangeEvent = function(timesFirstAssigned) {
    this.type = mirosubs.subtitle.EditableCaption.CHANGE;
    this.timesFirstAssigned = timesFirstAssigned;
};
