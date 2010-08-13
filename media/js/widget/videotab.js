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

goog.provide('mirosubs.widget.VideoTab');

mirosubs.widget.VideoTab = function() {
    goog.ui.Component.call(this);
    this.anchorElem_ = null;
    this.imageElem_ = null;
    this.spanElem_ = null;
    this.spinnerGifURL_ = mirosubs.imageAssetURL('spinner.gif');
    this.logoURL_ = mirosubs.imageAssetURL('small_logo.png');
    this.imageLoader_ = new goog.net.ImageLoader();
    this.imageLoader_.addImage('spinner', this.spinnerGifURL_);
    this.imageLoader_.addImage('small_logo', this.logoURL_);
    this.imageLoader_.start();
};
goog.inherits(mirosubs.widget.VideoTab, goog.ui.Component);

mirosubs.widget.VideoTab.InitialState = {
    SUBTITLE_ME: 0,
    CHOOSE_LANGUAGE: 1
};

mirosubs.widget.VideoTab.Messages = {
    SUBTITLE_ME: 'Subtitle me',
    CHOOSE_LANGUAGE : 'Choose language'
};

mirosubs.widget.VideoTab.prototype.createDom = function() {
    mirosubs.widget.VideoTab.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-videoTab';
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.imageElem_ = $d('img', {'alt': 'small logo'});
    this.spanElem_ = $d('span', 'mirosubs-tabText');
    this.anchorElem_ = 
        $d('a', {'className': 'mirosubs-subtitleMeLink', 'href':'#'},
           this.imageElem_, this.spanElem_);
    this.getElement().appendChild(this.anchorElem_);
};

mirosubs.widget.VideoTab.prototype.showLoading = function(loading) {
    this.imageElem_.src = loading ? this.spinnerGifURL_ : this.logoURL_;
};

mirosubs.widget.VideoTab.prototype.setText = function(text) {
    goog.dom.setTextContent(this.spanElem_, text);
};
mirosubs.widget.VideoTab.prototype.getAnchorElem = function() {
    return this.anchorElem_;
};
mirosubs.widget.VideoTab.prototype.disposeInternal = function() {
    mirosubs.widget.VideoTab.superClass_.disposeInternal.call(this);
    this.imageLoader_.dispose();
};
