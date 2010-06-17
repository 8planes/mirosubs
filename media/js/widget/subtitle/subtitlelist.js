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
 * @param {mirosubs.subtitle.EditableCaptionSet} captionSet
 */
mirosubs.subtitle.SubtitleList = function(videoPlayer, captionSet,
                                          displayTimes, opt_showBeginMessage) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    this.captionSet_ = captionSet;
    this.displayTimes_ = displayTimes;
    this.currentActiveSubtitle_ = null;
    /**
     * A map of captionID to mirosubs.subtitle.SubtitleWidget
     */
    this.subtitleMap_ = {};
    this.currentlyEditing_ = false;
    this.showBeginMessage_ = opt_showBeginMessage ? true : false;
    this.showingBeginMessage_ = false;
};
goog.inherits(mirosubs.subtitle.SubtitleList, goog.ui.Component);
mirosubs.subtitle.SubtitleList.prototype.createDom = function() {
    var dh = this.getDomHelper();
    var $d = goog.bind(dh.createDom, dh);
    var $t = goog.bind(dh.createTextNode, dh);
    this.setElementInternal($d('ul', 'mirosubs-titlesList'));
    if (this.captionSet_.count() == 0 && this.showBeginMessage_) {
        this.showingBeginMessage_ = true;
        goog.dom.classes.add(this.getElement(), 'mirosubs-beginTab');
        this.getElement().appendChild(
            $d('li', 'mirosubs-beginTabLi',
               $t('To begin, press TAB to play'),
               $d('br'),
               $t('and start typing!')));
    }
    else {
        var i;
        for (i = 0; i < this.captionSet_.count(); i++)
            this.addSubtitle(this.captionSet_.caption(i));
    }
};
mirosubs.subtitle.SubtitleList.prototype.enterDocument = function() {
    mirosubs.subtitle.SubtitleList.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(
            this.captionSet_,
            mirosubs.subtitle.EditableCaptionSet.CLEAR_ALL,
            this.captionsCleared_).
        listen(
            this.captionSet_,
            mirosubs.subtitle.EditableCaptionSet.CLEAR_TIMES,
            this.captionTimesCleared_);
};
mirosubs.subtitle.SubtitleList.prototype.captionsCleared_ = function(event) {
    this.subtitleMap_ = {};
    this.removeChildren(true);
};
mirosubs.subtitle.SubtitleList.prototype.captionTimesCleared_ = function(e) {
    var subtitleWidgets = goog.object.getValues(this.subtitleMap_);
    goog.array.forEach(subtitleWidgets, function(w) { w.clearTimes(); });
};
/**
 *
 * @param {mirosubs.subtitle.EditableCaption} subtitle
 *
 */
mirosubs.subtitle.SubtitleList.prototype.addSubtitle =
    function(subtitle, opt_scrollDown)
{
    if (this.showingBeginMessage_) {
        goog.dom.removeChildren(this.getElement());
        goog.dom.classes.remove(this.getElement(), 'mirosubs-beginTab');
        this.showingBeginMessage_ = false;
    }
    var subtitleWidget =
        new mirosubs.subtitle.SubtitleWidget(
            subtitle,
            goog.bind(this.setCurrentlyEditing_, this),
            this.displayTimes_);
    this.addChild(subtitleWidget, true);
    this.subtitleMap_[subtitle.getCaptionID()] = subtitleWidget;
    if (opt_scrollDown && typeof(opt_scrollDown) == 'boolean')
        this.scrollToCaption(subtitle.getCaptionID());
};
mirosubs.subtitle.SubtitleList.prototype.clearActiveWidget = function() {
    if (this.currentActiveSubtitle_ != null) {
        this.currentActiveSubtitle_.setActive(false);
        this.currentActiveSubtitle_ = null;
    }
};
/**
 * @param {boolean} taller
 */
mirosubs.subtitle.SubtitleList.prototype.setTaller = function(taller) {
    if (taller)
        goog.dom.classes.add(this.getElement(), 'taller');
    else
        goog.dom.classes.remove(this.getElement(), 'taller');
};
mirosubs.subtitle.SubtitleList.prototype.setActiveWidget = function(captionID) {
    this.scrollToCaption(captionID);
    this.clearActiveWidget();
    var subtitleWidget = this.subtitleMap_[captionID];
    subtitleWidget.setActive(true);
    this.currentActiveSubtitle_ = subtitleWidget;
};
mirosubs.subtitle.SubtitleList.prototype.getActiveWidget = function() {
    return this.currentActiveSubtitle_;
};
mirosubs.subtitle.SubtitleList.prototype.scrollToCaption = function(captionID) {
    var subtitleWidget = this.subtitleMap_[captionID];
    goog.style.scrollIntoContainerView(subtitleWidget.getElement(),
                                       this.getElement(), true);
};
mirosubs.subtitle.SubtitleList.prototype.setCurrentlyEditing_ =
    function(editing, timeChanged, subtitleWidget)
{
    this.currentlyEditing_ = editing;
    if (editing) {
        this.videoPlayer_.pause();
    }
    else {
        var subStartTime = subtitleWidget.getSubtitle().getStartTime();
        if (timeChanged) {
            this.videoPlayer_.playWithNoUpdateEvents(subStartTime, 2);
        }
    }
};
mirosubs.subtitle.SubtitleList.prototype.isCurrentlyEditing = function() {
    return this.currentlyEditing_;
};
