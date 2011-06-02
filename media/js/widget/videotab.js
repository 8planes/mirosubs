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

/**
 * @constructor
 * @param {boolean=} opt_forAnchoring If true, will add a style that gives 
 *     the tab absolute position.
 */
mirosubs.widget.VideoTab = function(opt_forAnchoring) {
    goog.ui.Component.call(this);
    this.anchorElem_ = null;
    this.imageElem_ = null;
    this.spanElem_ = null;
    this.nudgeElem_ = null;
    this.nudgeSpanElem_ = null;
    this.nudgeClickCallback_ = null;
    this.shareSpanElem_ = null;
    this.shareElem_ = null;
    this.showingError_ = false;
    this.forAnchoring_ = !!opt_forAnchoring;
    this.spinnerGifURL_ = mirosubs.imageAssetURL('spinner.gif');
    this.logoURL_ = mirosubs.imageAssetURL('small_logo.png');
    this.imageLoader_ = new goog.net.ImageLoader();
    this.imageLoader_.addImage('spinner', this.spinnerGifURL_);
    this.imageLoader_.addImage('small_logo', this.logoURL_);
    this.imageLoader_.start();
};
goog.inherits(mirosubs.widget.VideoTab, goog.ui.Component);

mirosubs.widget.VideoTab.prototype.createDom = function() {
    mirosubs.widget.VideoTab.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-videoTab mirosubs-videoTab-' + 
        (this.forAnchoring_ ? 'anchoring' : 'static');
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.imageElem_ = $d('img', {'alt': 'small logo'});
    this.spanElem_ = $d('span', 'mirosubs-tabTextchoose');
    this.anchorElem_ = 
        $d('a', {'className': 'mirosubs-subtitleMeLink', 'href':'#'},
           this.imageElem_, this.spanElem_);
    this.nudgeSpanElem_ = $d('span', 'mirosubs-tabTextfinish', 'NUDGE TEXT');
    this.nudgeElem_ = $d('a', {'href':'#'}, this.nudgeSpanElem_);
    this.getElement().appendChild(this.anchorElem_);
    this.getElement().appendChild(this.nudgeElem_);
};

mirosubs.widget.VideoTab.prototype.enterDocument = function() {
    mirosubs.widget.VideoTab.superClass_.enterDocument.call(this);
    this.showNudge(false);
    this.getHandler().
        listen(this.nudgeElem_, 'click', this.nudgeClicked_);
};

mirosubs.widget.VideoTab.prototype.getMenuAnchor = function() {
    return this.anchorElem_;
};

mirosubs.widget.VideoTab.prototype.showLoading = function() {
    this.imageElem_.src = this.spinnerGifURL_;
    goog.dom.setTextContent(this.spanElem_, "Loading");
};

mirosubs.widget.VideoTab.prototype.showError = function() {
    this.imageElem_.src = this.logoURL_;
    goog.dom.setTextContent(this.spanElem_, "Subs Unavailable");
    this.showingError_ = true;
};

mirosubs.widget.VideoTab.prototype.isShowingError = function() {
    return this.showingError_;
};

/**
 * Just stops loading. If state has changed, stop loading by
 * calling showContent instead.
 *
 */
mirosubs.widget.VideoTab.prototype.stopLoading = function() {
    this.imageElem_.src = this.logoURL_;
    if (this.text_)
        goog.dom.setTextContent(this.spanElem_, this.text_);
};

/**
 * Stops loading, and shows text appropriate for content.
 * @param {boolean} hasSubtitles Do subs currently exist for this video?
 * @param {mirosubs.widget.SubtitleState=} opt_playSubState Subtitles 
 *     that are currently loaded to play in widget.
 */
mirosubs.widget.VideoTab.prototype.showContent = function(
    hasSubtitles, opt_playSubState) 
{
    this.imageElem_.src = this.logoURL_;
    var text;
    if (opt_playSubState)
        text = opt_playSubState.LANGUAGE ? 
            mirosubs.languageNameForCode(opt_playSubState.LANGUAGE) :
            "Original Language";
    else
        text = hasSubtitles ? "Select Language" : "Subtitle Me";
    this.text_ = text;
    goog.dom.setTextContent(this.spanElem_, text);
};

mirosubs.widget.VideoTab.prototype.getAnchorElem = function() {
    return this.anchorElem_;
};

mirosubs.widget.VideoTab.prototype.nudgeClicked_ = function(e) {
    e.preventDefault();
    mirosubs.Tracker.getInstance().track('Clicks_Improve_Subtitles_or_translation');
    if (this.nudgeClickCallback_)
        this.nudgeClickCallback_();
};

mirosubs.widget.VideoTab.prototype.showNudge = function(shows) {
    mirosubs.style.setVisibility(this.nudgeElem_, shows);
    mirosubs.style.setVisibility(this.nudgeSpanElem_, shows);
     if (shows){
         mirosubs.style.setProperty(this.nudgeElem_, 'width', null);
        
     }else{
         mirosubs.style.setWidth(this.nudgeElem_, 0);
     }
    return;
};

/*
 * Creates the share button next to the 'subtitle me', only if 
 * this is an off site widget. When clicked will be taken to the
 * url provided.
 * @param shareURL {goog.URI} The url for the 'share' link.
 * @param newWindow {bool=} If true will open on new window.
 */
mirosubs.widget.VideoTab.prototype.createShareButton = function (shareURL, newWindow){
    if (!mirosubs.isEmbeddedInDifferentDomain()){
        // no point in taking to the unisubs site if we're here already
        return;
    }
    if(!this.shareElem_){
        var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
        this.shareSpanElem_ = $d('span', {'href':'', 'class':'mirosubs-tabTextShare'}, 'Share');
        this.shareElem_ = $d('a', {'href':'', 'class':''}, this.shareSpanElem_);
        this.getElement().appendChild(this.shareElem_);    
    }
    var target= newWindow ? "_blank" : "_self";
    goog.dom.setProperties(this.shareElem_, {"href": shareURL.toString(), "target":target});
};

mirosubs.widget.VideoTab.prototype.updateNudge = function(text, fn) {
    goog.dom.setTextContent(this.nudgeSpanElem_, text);
    this.nudgeClickCallback_ = fn;
};
mirosubs.widget.VideoTab.prototype.show = function(shown) {
    mirosubs.style.showElement(this.getElement(), shown);
};
mirosubs.widget.VideoTab.prototype.disposeInternal = function() {
    mirosubs.widget.VideoTab.superClass_.disposeInternal.call(this);
    this.imageLoader_.dispose();
};
