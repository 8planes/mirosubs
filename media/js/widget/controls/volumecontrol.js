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

goog.provide('mirosubs.controls.VolumeControl');

mirosubs.controls.VolumeControl = function(videoPlayer) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
};
goog.inherits(mirosubs.controls.VolumeControl, goog.ui.Component);

mirosubs.controls.VolumeControl.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var el = $d('span', 'mirosubs-volume');
    this.setElementInternal(el);
    this.volumeButton_ = $d('span');
    goog.dom.a11y.setRole(
        this.volumeButton_, goog.dom.a11y.Role.BUTTON);
    this.getElement().appendChild(this.volumeButton_);
    this.volumeSlider_ = new mirosubs.controls.VolumeSlider();
    this.addChild(this.volumeSlider_);
};

mirosubs.controls.VolumeControl.prototype.enterDocument = function() {
    mirosubs.controls.VolumeControl.superClass_.enterDocument.call(this);
    
};