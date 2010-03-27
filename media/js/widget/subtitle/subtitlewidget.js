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

goog.provide('mirosubs.subtitle.SubtitleWidget');

mirosubs.subtitle.SubtitleWidget = function(subtitle, displayTimes, subtitleList) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    this.keyHandler_ = null;
    this.displayTimes_ = displayTimes;
    this.subtitleList_ = subtitleList;
};
goog.inherits(mirosubs.subtitle.SubtitleWidget, goog.ui.Component);
mirosubs.subtitle.SubtitleWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.setElementInternal($d('li', null,
                               this.timestampElem_ = 
                               $d('span', {'className':'mirosubs-timestamp'}),
                               this.titleElem_ = 
                               $d('span', {'className':'mirosubs-title'},
                                  this.titleElemInner_ = 
                                  $d('span'))));
    if (!this.displayTimes_) {
        goog.dom.classes.add(this.titleElem_, 'mirosubs-title-notime');
        this.timestampElem_.style.display = 'none';
    }
    this.textareaElem_ = null;
    this.keyHandler_ = null;
    this.docClickListener_ = null;
    this.updateValues();
    this.showingTextarea_ = false
};
mirosubs.subtitle.SubtitleWidget.prototype.enterDocument = function() {
    this.getHandler().listen(this.getElement(),
                             goog.events.EventType.DBLCLICK,
                             this.doubleClicked_, false, this);
};
mirosubs.subtitle.SubtitleWidget.prototype.setActive = function(active) {
    var c = goog.dom.classes;
    if (active)
        c.add(this.getElement(), 'active');
    else
        c.remove(this.getElement(), 'active');
};
/**
 *
 * @return {mirosub.subtitle.EditableCaption} The subtitle for this widget.
 */
mirosubs.subtitle.SubtitleWidget.prototype.getSubtitle = function() {
    return this.subtitle_;
};
mirosubs.subtitle.SubtitleWidget.prototype.doubleClicked_ = function(event) {
    if (this.showingTextarea_)
        return;
    this.showingTextarea_ = true;
    if (this.subtitleList_)
        this.subtitleList_.setCurrentlyEditing(this, true);
    this.docClickListener_ = new goog.events.EventHandler();
    var that = this;
    this.docClickListener_.listen(document, goog.events.EventType.CLICK,
                                  function(event) {
                                      if (event.target != that.textareaElem_)
                                          that.switchToView_();
                                  });
    goog.dom.removeNode(this.titleElemInner_);
    this.textareaElem_ = this.getDomHelper().createElement('textarea');
    this.titleElem_.appendChild(this.textareaElem_);
    this.textareaElem_.value = this.subtitle_.getText();
    this.textareaElem_.focus();
    this.keyHandler_ = new goog.events.KeyHandler(this.textareaElem_);
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_, false, this);
    event.stopPropagation();
    event.preventDefault();
};
mirosubs.subtitle.SubtitleWidget.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        this.switchToView_();
        event.stopPropagation();
        event.preventDefault();
    }
};
mirosubs.subtitle.SubtitleWidget.prototype.switchToView_ = function() {
    if (!this.showingTextarea_)
        return;
    this.getHandler().unlisten(this.keyHandler_);
    this.disposeEventHandlers_();
    this.subtitle_.setText(this.textareaElem_.value);
    goog.dom.removeNode(this.textareaElem_);
    this.titleElem_.appendChild(this.titleElemInner_);
    this.updateValues();
    this.showingTextarea_ = false;
    if (this.subtitleList_)
        this.subtitleList_.setCurrentlyEditing(this, false);
};
mirosubs.subtitle.SubtitleWidget.prototype.updateValues = function() {
    var $t = goog.dom.setTextContent;
    if (this.displayTimes_) {
        var time = this.subtitle_.getStartTime();
        this.timestampElem_.style.visibility = 
            time == -1 ? 'hidden' : 'visible';
        if (time != -1)
            $t(this.timestampElem_, this.formatTime_(time));
    }
    $t(this.titleElemInner_, this.subtitle_.getText());    
};
mirosubs.subtitle.SubtitleWidget.prototype.formatTime_ = function(time) {
    var pad = function(number) {
        return (number < 10 ? "0" : "") + number;
    };

    var intTime = parseInt(time);

    var timeString = '';
    var hours = (intTime / 3600) | 0;
    if (hours > 0)
        timeString += (hours + ':');
    var minutes = ((intTime / 60) | 0) % 60;
    if (minutes > 0 || hours > 0) {
        if (hours > 0)
            timeString += (pad(minutes) + ':');
        else
            timeString += (minutes + ':');
    }
    var seconds = intTime % 60;
    if (seconds > 0 || minutes > 0 || hours > 0) {
        if (minutes > 0 || hours > 0)
            timeString += pad(seconds);
        else
            timeString += seconds;
    }
    var frac = parseInt((time - intTime) * 100);
    timeString += ('.' + pad(frac));

    return timeString;        
};
mirosubs.subtitle.SubtitleWidget.prototype.disposeEventHandlers_ = function() {
    if (this.keyHandler_) {
        this.keyHandler_.dispose();
        this.keyHandler_ = null;
    }
    if (this.docClickListener_) {
        this.docClickListener_.dispose();
        this.docClickListener_ = null;
    }
};
mirosubs.subtitle.SubtitleWidget.prototype.disposeInternal = function() {
    mirosubs.subtitle.SubtitleWidget.superClass_.disposeInternal.call(this);
    this.disposeEventHandlers_();
};