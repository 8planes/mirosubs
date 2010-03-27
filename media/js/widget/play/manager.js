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

goog.provide('mirosubs.play.Manager');

mirosubs.play.Manager = function(videoPlayer, captions) {
    goog.Disposable.call(this);
    this.videoPlayer_ = videoPlayer;
    this.captionManager_ = new mirosubs.CaptionManager(videoPlayer.getPlayheadFn());
    this.captionManager_.addCaptions(captions);
    goog.events.listen(this.captionManager_,
                       mirosubs.CaptionManager.EventType.CAPTION,
                       this.captionReached_, false, this);
};
goog.inherits(mirosubs.play.Manager, goog.Disposable);
mirosubs.play.Manager.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.videoPlayer_.showCaptionText(c ? c['caption_text'] : '');
};
mirosubs.play.Manager.prototype.disposeInternal = function() {
    mirosubs.play.Manager.superClass_.disposeInternal.call(this);
    this.captionManager_.dispose();
};