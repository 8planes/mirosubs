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

/**
 * @fileoverview Meant to be used in mirosubs.finishfaildialog.Dialog. 
 *    Corresponds to 'reattempt upload' state of that dialog.
 */

goog.provide('mirosubs.finishfaildialog.ReattemptUploadPanel');

/**
 * @constructor
 * @param {mirosubs.subtitle.EditableCaptionSet} captionSet
 * @param {function()} saveFn function to reattempt the sub save.
 */
mirosubs.finishfaildialog.ReattemptUploadPanel = function(captionSet, saveFn) {
    goog.ui.Component.call(this);
    this.captionSet_ = captionSet;
    this.saveFn_ = saveFn;
};
goog.inherits(mirosubs.finishfaildialog.ReattemptUploadPanel, goog.ui.Component);

mirosubs.finishfaildialog.ReattemptUploadPanel.prototype.createDom = function() {
    mirosubs.finishfaildialog.ReattemptUploadPanel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.saveAgainLink_ = $d('a', {'href':'#'}, 'Try saving your subtitles again');
    this.downloadLink_ = $d('a', {'href': '#'}, 'Download your subtitles to your computer');
    this.logLink_ = $d('a', {'href': '#'}, 'subtitling log');
    this.saveContainer_ = $d('p', null, this.saveAgainLink_);
    goog.dom.append(
        this.getElement(),
        $d('p', null, 'We failed to save your subtitles. Don\'t worry, your work is not lost. We\'re not totally sure, but it looks like your network connection is not great.'),
        this.saveContainer_,
        $d('p', null, this.downloadLink_));
};

mirosubs.finishfaildialog.ReattemptUploadPanel.prototype.enterDocument = function() {
    mirosubs.finishfaildialog.ReattemptUploadPanel.superClass_.enterDocument.call(this);
    this.getHandler()
        .listen(
            this.saveAgainLink_, 'click',
            this.saveAgainClicked_)
        .listen(
            this.downloadLink_, 'click',
            this.downloadClicked_);
};

mirosubs.finishfaildialog.ReattemptUploadPanel.prototype.saveAgainClicked_ = function(e) {
    e.preventDefault();
    this.saveContainer_.innerHTML = "Saving...";
    this.saveFn_();
};

mirosubs.finishfaildialog.ReattemptUploadPanel.prototype.downloadClicked_ = function(e) {
    e.preventDefault();
    mirosubs.finishfaildialog.CopyDialog.showForSubs(
        this.captionSet_.makeJsonSubs());
};

mirosubs.finishfaildialog.ReattemptUploadPanel.prototype.showTryAgain = function() {
    goog.dom.removeChildren(this.saveContainer_);
    this.saveAgainLink_.innerHTML = "Try again.";
    goog.dom.append(
        this.saveContainer_,
        goog.dom.createTextNode('Okay, that didn\'t work. '),
        this.saveAgainLink_);
};