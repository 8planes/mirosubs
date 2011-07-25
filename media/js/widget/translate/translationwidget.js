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

goog.provide('mirosubs.translate.TranslationWidget');

/**
 * @constructor
 * @param {Object.<string, *>} subtitle Base language subtitle in json format
 * @param {mirosubs.subtitle.EditableCaption} translation
 */
mirosubs.translate.TranslationWidget = function(subtitle,
                                                translation) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    /**
     * @type {mirosubs.subtitle.EditableCaption}
     */
    this.translation_ = translation;
};
goog.inherits(mirosubs.translate.TranslationWidget, goog.ui.Component);

mirosubs.translate.TranslationWidget.prototype.getSubtitle = function(){
    return this.subtitle_;
};

mirosubs.translate.TranslationWidget.prototype.getOriginalValue = function(){
    return this.subtitle_.text;
};

mirosubs.translate.TranslationWidget.prototype.getSubJson = function() {
    return {
        'subtitle_id': this.getCaptionID(),
        'text': this.translateInput_.value
    };
};

mirosubs.translate.TranslationWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.setElementInternal(
        $d('li', null,
           $d('div', null,
              $d('span', 'mirosubs-title mirosubs-title-notime', this.subtitle_['text']),
              this.loadingIndicator_ = $d('span', 'mirosubs-loading-indicator', 'loading...')
           ),
           this.translateInput_ = $d('textarea', 'mirosubs-translateField')
        )
    );
    
    this.getHandler()
        .listen(
            this.translateInput_, goog.events.EventType.BLUR,
            goog.bind(this.inputLostFocus_, this, true))
        .listen(
            this.translateInput_, goog.events.EventType.FOCUS,
            this.inputGainedFocus_);
    this.translateInput_.value = this.translation_ ? this.translation_.getText() : '';
};

mirosubs.translate.TranslationWidget.prototype.inputGainedFocus_ = function(event) {
    this.onFocusText_ = this.translateInput_.value;
};

mirosubs.translate.TranslationWidget.prototype.inputLostFocus_ = function(track) {
    var value = goog.string.trim(this.translateInput_.value);
    var edited = value != this.onFocusText_;
    if (track && edited) {
        if (this.onFocusText_ == "")
            mirosubs.SubTracker.getInstance().trackAdd(this.getCaptionID());
        else
            mirosubs.SubTracker.getInstance().trackEdit(this.getCaptionID());
    }
    this.translation_.setText(value);
};


mirosubs.translate.TranslationWidget.prototype.setTranslationContent = function(value){
    this.translateInput_.value = value;
    this.inputLostFocus_(false);
};

mirosubs.translate.TranslationWidget.prototype.setEnabled = function(enabled) {
    this.translateInput_.disabled = !enabled;
    if (!enabled)
        this.translateInput_.value = '';
};

mirosubs.translate.TranslationWidget.prototype.getCaptionID = function() {
    return this.subtitle_['subtitle_id'];
};

/**
 * Return if translate input has some value
 * @return {boolean}
 */
mirosubs.translate.TranslationWidget.prototype.isEmpty = function(){
    return ! goog.string.trim(this.translateInput_.value);
};

mirosubs.translate.TranslationWidget.prototype.showLoadingIndicator = function(){
    mirosubs.style.showElement(this.loadingIndicator_, true);
};

mirosubs.translate.TranslationWidget.prototype.hideLoadingIndicator = function(){
    mirosubs.style.showElement(this.loadingIndicator_, false);
};