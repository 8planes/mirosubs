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

goog.provide('mirosubs.subtitle.SubtitleList');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 */
mirosubs.subtitle.SubtitleList = function(captions, displayTimes) {
    goog.ui.Component.call(this);
    this.captions_ = captions;
    this.displayTimes_ = displayTimes;
    this.currentActiveSubtitle_ = null;
    this.subtitleWidgets_ = [];
    /**
     * A map of captionID to mirosubs.subtitle.SubtitleWidget
     */
    this.subtitleMap_ = {};
    this.currentlyEditing_ = false;
};
goog.inherits(mirosubs.subtitle.SubtitleList, goog.ui.Component);
mirosubs.subtitle.SubtitleList.MIN_SUB_LENGTH = 1;
mirosubs.subtitle.SubtitleList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper().createDom(
        'ul', 'mirosubs-titlesList'));
    goog.array.forEach(this.captions_, this.addSubtitle, this);
};

/**
 *
 */
mirosubs.subtitle.SubtitleList.prototype.addSubtitle = 
    function(subtitle, opt_scrollDown) 
{
    var subtitleWidget = 
        new mirosubs.subtitle.SubtitleWidget(
            subtitle, this.displayTimes_, this,
            this.subtitleWidgets_.length);
    this.addChild(subtitleWidget, true);
    this.getHandler().listen(
        subtitleWidget, mirosubs.Spinner.VALUE_CHANGED,
        goog.bind(this.timeValueChanged_, this, 
                  this.subtitleWidgets_.length));
    this.subtitleWidgets_.push(subtitleWidget);
    if (this.subtitleWidgets_.length > 1)
        this.setSubtitleMinMax_(this.subtitleWidgets_.length - 2);
    this.setSubtitleMinMax_(this.subtitleWidgets_.length - 1);
    this.subtitleMap_[subtitle.getCaptionID() + ''] = subtitleWidget;
    if (typeof(opt_scrollDown) == 'boolean' && opt_scrollDown)
        this.scrollToCaption(subtitle.getCaptionID());
};
mirosubs.subtitle.SubtitleList.prototype.clearActiveWidget = function() {
    if (this.currentActiveSubtitle_ != null) {
        this.currentActiveSubtitle_.setActive(false);
        this.currentActiveSubtitle_ = null;
    }
};
mirosubs.subtitle.SubtitleList.prototype.timeValueChanged_ = 
    function(subtitleIndex, event)
{
    var newTimeValue = event.value;
    var subtitle = this.subtitleWidgets_[subtitleIndex].getSubtitle();
    subtitle.setStartTime(newTimeValue);
    if (subtitleIndex > 0) {
        var lastSubtitle = this.subtitleWidgets_[
            subtitleIndex - 1].getSubtitle();
        lastSubtitle.setEndTime(newTimeValue);
    }
    this.setSubtitleMinMax_(subtitleIndex + 1);
    this.setSubtitleMinMax_(subtitleIndex - 1);
};
mirosubs.subtitle.SubtitleList.prototype.setActiveWidget = function(captionID) {
    this.scrollToCaption(captionID);
    this.clearActiveWidget();
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    subtitleWidget.setActive(true);
    this.currentActiveSubtitle_ = subtitleWidget;
};
mirosubs.subtitle.SubtitleList.prototype.getActiveWidget = function() {
    return this.currentActiveSubtitle_;
};
mirosubs.subtitle.SubtitleList.prototype.scrollToCaption = function(captionID) {
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    goog.style.scrollIntoContainerView(subtitleWidget.getElement(),
                                       this.getElement(), true);
};
mirosubs.subtitle.SubtitleList.prototype.updateWidget = function(captionID) {
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    subtitleWidget.updateValues();
    this.setSubtitleMinMax_(subtitleWidget.getIndex() + 1);
    this.setSubtitleMinMax_(subtitleWidget.getIndex() - 1);
};
mirosubs.subtitle.SubtitleList.prototype.setSubtitleMinMax_ = function(index) {
    if (index >= 0 && index < this.subtitleWidgets_.length) {
        var subWidget = this.subtitleWidgets_[index];
        if (index > 0) {
            var lastSubWidget = this.subtitleWidgets_[index - 1];
            if (lastSubWidget.getSubtitle().getStartTime() != -1)
                subWidget.setMinSubTime(
                    lastSubWidget.getSubtitle().getStartTime() +
                        mirosubs.subtitle.SubtitleList.MIN_SUB_LENGTH);
            else
                subWidget.setMinSubTime(0);
        }
        else
            subWidget.setMinSubTime(0);
        if (subWidget.getSubtitle().getEndTime() != -1)
            subWidget.setMaxSubTime(
                subWidget.getSubtitle().getEndTime() -
                    mirosubs.subtitle.SubtitleList.MIN_SUB_LENGTH);
        else
            subWidget.setMaxSubTime(999999999);
    }
};
mirosubs.subtitle.SubtitleList.prototype.setCurrentlyEditing = 
    function(subtitleWidget, editing) {
    this.currentlyEditing_ = editing;
};
mirosubs.subtitle.SubtitleList.prototype.isCurrentlyEditing = function() {
    return this.currentlyEditing_;
};
