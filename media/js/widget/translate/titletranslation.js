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

goog.provide('mirosubs.translate.TitleTranslation');

mirosubs.translate.TitleTranslationWidget = function(videoTitle,
                                                unitOfWork) {
    goog.ui.Component.call(this);
    this.videoTitle_ = videoTitle;
    this.unitOfWork_ = unitOfWork;
    this.translation_ = null;
};
goog.inherits(mirosubs.translate.TitleTranslationWidget, goog.ui.Component);

mirosubs.translate.TitleTranslationWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.setElementInternal(
        $d('li', null,
           $d('div', null,
              $d('span', 'mirosubs-title mirosubs-title-notime', 'TITLE: '+this.videoTitle_),
              this.loadingIndicator_ = $d('span', 'mirosubs-loading-indicator', 'loading...')
           ),
           this.translateInput_ = $d('textarea', 'mirosubs-translateField')
        )
    );

    this.getHandler().listen(
        this.translateInput_, goog.events.EventType.BLUR,
        this.inputLostFocus_);
};

mirosubs.translate.TranslationWidget.prototype.inputLostFocus_ = function(event) {
    this.translation_ = this.translateInput_.value;
};