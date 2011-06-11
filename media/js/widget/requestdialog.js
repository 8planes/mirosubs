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

goog.provide('mirosubs.widget.RequestDialog');

/**
 * @constructor
 * @param {string} videoID
 */
mirosubs.widget.RequestDialog = function(videoID) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.videoID_ = videoID;
    this.model_ = null;
};
goog.inherits(mirosubs.widget.RequestDialog, goog.ui.Dialog);

mirosubs.widget.RequestDialog.prototype.createDom = function() {
    mirosubs.widget.RequestDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    var el = this.getElement();
    el.appendChild(
        $d('h3', null, 'Request subtitles'));
    this.contentDiv_ = $d('div', null, "Loading...");
    el.appendChild(this.contentDiv_);
};

mirosubs.widget.RequestDialog.prototype.enterDocument = function() {
    mirosubs.widget.RequestDialog.superClass_.enterDocument.call(this);
    this.connectEvents_();
};

mirosubs.widget.RequestDialog.prototype.connectEvents_ = function() {
};
