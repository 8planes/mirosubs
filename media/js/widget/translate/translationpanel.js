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

goog.provide('mirosubs.translate.TranslationPanel');

// FIXME: I think that since the latest translation changes, this class no 
//     longer really does anything. Probably just go straight to TranslationList
//     instead of using this as an intermediary.

/**
 *
 *
 * @constructor
 * @param {mirosubs.subtitle.EditableCaptionSet} captionSet
 * @param {mirosubs.subtitle.SubtitleState} standardSubState
 */
mirosubs.translate.TranslationPanel = function(captionSet,
                                               standardSubState) {
    goog.ui.Component.call(this);
    this.captionSet_ = captionSet
    this.standardSubState_ = standardSubState;
    this.contentElem_ = null;
};
goog.inherits(mirosubs.translate.TranslationPanel, goog.ui.Component);

mirosubs.translate.TranslationPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};
mirosubs.translate.TranslationPanel.prototype.createDom = function() {
    mirosubs.translate.TranslationPanel.superClass_.createDom.call(this);
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    el.appendChild(this.contentElem_ = $d('div'));
    this.translationList_ =
        new mirosubs.translate.TranslationList(
            this.captionSet_,
            this.standardSubState_.SUBTITLES,
            this.standardSubState_.TITLE);
    this.addChild(this.translationList_, true);
    this.translationList_.getElement().className =
        "mirosubs-titlesList";
};
mirosubs.translate.TranslationPanel.prototype.getTranslationList = function(){
    return this.translationList_;
};
