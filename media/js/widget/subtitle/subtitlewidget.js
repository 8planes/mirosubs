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

mirosubs.subtitle.SubtitleWidget = function(subtitle, editingFn, displayTimes) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    this.editingFn_ = editingFn;
    this.displayTimes_ = displayTimes;
    this.keyHandler_ = null;
    this.timeSpinner_ = null;
};
goog.inherits(mirosubs.subtitle.SubtitleWidget, goog.ui.Component);

mirosubs.subtitle.SubtitleWidget.prototype.getContentElement = function() {
    return this.contentElement_;
};
mirosubs.subtitle.SubtitleWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.contentElement_ = $d('span', 'mirosubs-timestamp');
    this.setElementInternal(
        $d('li', null,
           this.contentElement_,
           this.titleElem_ = 
           $d('span', {'className':'mirosubs-title'},
              this.titleElemInner_ = 
              $d('span'))));
    if (!this.displayTimes_) {
        goog.dom.classes.add(this.titleElem_, 'mirosubs-title-notime');
        this.contentElement_.style.display = 'none';
    }
    else {
        this.timeSpinner_ = new mirosubs.Spinner(
            this.subtitle_.getStartTime(), 
            goog.bind(this.subtitle_.getMinStartTime, this.subtitle_),
            goog.bind(this.subtitle_.getMaxStartTime, this.subtitle_), 
            mirosubs.formatTime);
        this.addChild(this.timeSpinner_, true);
    }
    this.textareaElem_ = null;
    this.keyHandler_ = null;
    this.docClickListener_ = null;
    this.updateValues_();
    this.showingTextarea_ = false
    this.editing_ = false;
};
mirosubs.subtitle.SubtitleWidget.prototype.enterDocument = function() {
    mirosubs.subtitle.SubtitleWidget.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.subtitle_,
        mirosubs.subtitle.EditableCaption.CHANGE,
        this.updateValues_);
    this.getHandler().listen(
        this.titleElem_,
        goog.events.EventType.CLICK,
        this.clicked_);
    if (this.timeSpinner_)
        this.getHandler().listen(
            this.timeSpinner_, 
            goog.object.getValues(mirosubs.Spinner.EventType),
            this.timeSpinnerListener_);
};
mirosubs.subtitle.SubtitleWidget.prototype.setActive = function(active) {
    var c = goog.dom.classes;
    if (active)
        c.add(this.getElement(), 'active');
    else
        c.remove(this.getElement(), 'active');
};
mirosubs.subtitle.SubtitleWidget.prototype.timeSpinnerListener_ = 
    function(event) 
{
    var et = mirosubs.Spinner.EventType;
    if (event.type == et.ARROW_PRESSED)
        this.setEditing_(true);
    else if (event.type == et.VALUE_CHANGED) {
        this.subtitle_.setStartTime(event.value);
        this.setEditing_(false);
    }
};
mirosubs.subtitle.SubtitleWidget.prototype.setEditing_ = function(editing) {
    this.editingFn_(editing, this);
    this.editing_ = editing;
    if (!editing)
        this.updateValues_();
};
/**
 *
 * @return {mirosub.subtitle.EditableCaption} The subtitle for this widget.
 */
mirosubs.subtitle.SubtitleWidget.prototype.getSubtitle = function() {
    return this.subtitle_;
};
mirosubs.subtitle.SubtitleWidget.prototype.clicked_ = function(event) {
    if (this.showingTextarea_)
        return;
    if (mirosubs.subtitle.SubtitleWidget.editing_) {
        mirosubs.subtitle.SubtitleWidget.editing_.switchToView_();
        return;
    }
    mirosubs.subtitle.SubtitleWidget.editing_ = this;
    this.setEditing_(true);
    this.showingTextarea_ = true;
    this.docClickListener_ = new goog.events.EventHandler();
    var that = this;
    this.docClickListener_.listen(
        document, goog.events.EventType.CLICK,
        function(event) {
            if (event.target != that.textareaElem_) {
                that.switchToView_();
            }
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
    mirosubs.subtitle.SubtitleWidget.editing_ = null;
    this.getHandler().unlisten(this.keyHandler_);
    this.disposeEventHandlers_();
    this.subtitle_.setText(this.textareaElem_.value);
    goog.dom.removeNode(this.textareaElem_);
    this.titleElem_.appendChild(this.titleElemInner_);
    this.showingTextarea_ = false;
    this.setEditing_(false);
};
mirosubs.subtitle.SubtitleWidget.prototype.clearTimes = function() {
    this.contentElement_.style.visibility = 'hidden';
};
mirosubs.subtitle.SubtitleWidget.prototype.updateValues_ = function() {
    if (this.editing_)
        return;
    if (this.displayTimes_) {
        var time = this.subtitle_.getStartTime();
        this.contentElement_.style.visibility = 
            time == -1 ? 'hidden' : 'visible';
        if (time != -1)
            this.timeSpinner_.setValue(time);
    }
    goog.dom.setTextContent(this.titleElemInner_, 
                            this.subtitle_.getText());
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