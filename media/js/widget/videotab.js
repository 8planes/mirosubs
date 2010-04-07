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

goog.provide('mirosubs.VideoTab');

mirosubs.VideoTab = function() {
    goog.ui.Component.call(this);
    this.anchorElem_ = null;
    this.imageElem_ = null;
    this.spanElem_ = null;
    this.spinnerGifURL_ = [mirosubs.BASE_URL, mirosubs.IMAGE_DIR, 
                           'spinner.gif'].join('');
    this.logoURL_ = [mirosubs.BASE_URL, mirosubs.IMAGE_DIR, 
                           'small_logo.png'].join('');
    this.imageLoader_ = new goog.net.ImageLoader();
    this.imageLoader_.addImage('spinner', this.spinnerGifURL_);
    this.imageLoader_.start();
};
goog.inherits(mirosubs.VideoTab, goog.ui.Component);

/**
 * Decorate an HTML structure already in the document. Expects:
 * <pre>
 * - div
 *   - a
 *     - img
 *     - span
 * </pre>
 */
mirosubs.VideoTab.prototype.decorateInternal = function(el) {
    mirosubs.VideoTab.superClass_.decorateInternal.call(this, el);
    this.anchorElem_ = el.getElementsByTagName('a')[0];
    this.imageElem_ = this.anchorElem_.getElementsByTagName('img')[0];
    this.spanElem_ = this.anchorElem_.getElementsByTagName('span')[0];
};
mirosubs.VideoTab.prototype.showLoading = function(loading) {
    this.imageElem_.src = loading ? this.spinnerGifURL_ : this.logoURL_;
};
mirosubs.VideoTab.prototype.setText = function(text) {
    goog.dom.setTextContent(this.spanElem_, text);
};
mirosubs.VideoTab.prototype.getAnchorElem = function() {
    return this.anchorElem_;
};
mirosubs.VideoTab.prototype.disposeInternal = function() {
    mirosubs.VideoTab.superClass_.disposeInternal.call(this);
    this.imageLoader_.dispose();
};