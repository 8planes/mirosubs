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

goog.provide('mirosubs.HowToVideoPanel');

/**
 * @constructor
 * @param {mirosubs.HowToVideoPanel.VideoChoice} videoChoice
 */
mirosubs.HowToVideoPanel = function(videoChoice) {
    goog.ui.Component.call(this);
    if (mirosubs.video.supportsOgg())
        this.videoPlayer_ = videoChoice[0].createPlayer();
    else if (mirosubs.video.supportsH264())
        this.videoPlayer_ = videoChoice[1].createPlayer();
    else
        this.videoPlayer_ = videoChoice[2].createPlayer();
};
goog.inherits(mirosubs.HowToVideoPanel, goog.ui.Component);

mirosubs.HowToVideoPanel.CONTINUE = 'continue';
mirosubs.HowToVideoPanel.VideoChoice = {
    TRANSCRIBE: [
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-overviewtypingogg899.ogv'),
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-overviewtypingmp4598.m4v'),
        new mirosubs.video.YoutubeVideoSource('w7jmT6o0Nk0')
    ],
    SYNC: [
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-syncingogg217.ogv'),
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-syncingmp4898.m4v'),
        new mirosubs.video.YoutubeVideoSource('w7jmT6o0Nk0')],
    REVIEW: [
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-reviewogg196.ogv'),
        new mirosubs.video.Html5VideoSource(
            'http://blip.tv/file/get/Miropcf-reviewmp4769.m4v'),
        new mirosubs.video.YoutubeVideoSource('w7jmT6o0Nk0')]
};

mirosubs.HowToVideoPanel.prototype.getContentElement = function() {
    return this.contentElement_;
};

mirosubs.HowToVideoPanel.prototype.createDom = function() {
    mirosubs.HowToVideoPanel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.contentElement_ = $d('div');
    var el = this.getElement();
    el.className = 'mirosubs-howtopanel';
    el.appendChild($d('h2', null, 'How-To Video'));
    el.appendChild(this.contentElement_);
    this.skipVideosSpan_ = $d('span');
    el.appendChild($d('div', null, this.skipVideosSpan_,
                      goog.dom.createTextNode(' Skip these videos')));
    this.continueLink_ = 
        $d('a', 
           {'className': 'mirosubs-smallButton', 
            'href': '#'}, 
           $d('span', null, 'Continue'))
    el.appendChild(this.continueLink_);
    var vidPlayer = new goog.ui.Component();
    vidPlayer.addChild(this.videoPlayer_, true);
    this.addChild(vidPlayer, true);
};

mirosubs.HowToVideoPanel.prototype.enterDocument = function() {
    mirosubs.HowToVideoPanel.superClass_.enterDocument.call(this);
    if (!this.skipVideosCheckbox_) {
        this.skipVideosCheckbox_ = new goog.ui.Checkbox();
        this.skipVideosCheckbox_.decorate(this.skipVideosSpan_);
        this.skipVideosCheckbox_.setLabel(
            this.skipVideosCheckbox_.getElement().parentNode);
    }
    this.getHandler().listen(this.continueLink_, 'click', this.continue_);
};

mirosubs.HowToVideoPanel.prototype.continue_ = function() {
    this.dispatchEvent(mirosubs.HowToVideoPanel.CONTINUE);
};

mirosubs.HowToVideoPanel.prototype.disposeInternal = function() {
    mirosubs.HowToVideoPanel.superClass_.disposeInternal.call(this);
    this.videoPlayer_.pause();
    this.videoPlayer_.dispose();
};