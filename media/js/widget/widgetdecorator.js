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

goog.provide('mirosubs.widget.WidgetDecorator');

/**
 * @private
 * @constructor
 * @param {mirosubs.video.AbstractVideoPlayer} videoPlayer
 */
mirosubs.widget.WidgetDecorator = function(videoPlayer) {
    this.videoPlayer_ = videoPlayer;
    this.videoTab_ = new mirosubs.widget.VideoTab(true);
    this.videoTab_.render();
    this.videoTab_.show(false);
    this.videoTab_.showLoading();
    this.handler_ = new goog.events.EventHandler(this);
    if (this.videoPlayer_.areDimensionsKnown())
        this.videoDimensionsKnown_();
    else
        this.handler_.listen(
            this.videoPlayer_,
            mirosubs.video.AbstractVideoPlayer.EventType.DIMENSIONS_KNOWN,
            this.videoDimensionsKnown_);
    var args = {
        'video_url': videoPlayer.getVideoSource().getVideoURL(),
        'is_remote': mirosubs.isFromDifferentDomain()
    };
    if (this.videoPlayer_.getVideoSource() instanceof 
        mirosubs.video.Html5VideoSource)
        args['additional_video_urls'] = 
            this.videoPlayer_.getVideoSource().getAlternateURLs();
    this.controller_ = new mirosubs.widget.WidgetController(
        this.videoPlayer_.getVideoSource().getVideoURL(),
        this.videoPlayer_,
        this.videoTab_);
    mirosubs.Rpc.call(
        'show_widget', args, 
        goog.bind(this.controller_.initializeState, 
                  this.controller_));

    mirosubs.widget.Widget.widgetsCreated_.push(this);
};

/**
 *
 * @param {mirosubs.video.AbstractVideoPlayer} videoPlayer should already
 *     be attached to page.
 */
mirosubs.widget.WidgetDecorator.decorate = function(videoPlayer) {
    return new mirosubs.widget.WidgetDecorator(videoPlayer);
};

mirosubs.widget.WidgetDecorator.prototype.videoDimensionsKnown_ = function() {
    mirosubs.attachToLowerLeft(
        this.videoPlayer_.getElement(),
        this.videoTab_.getElement());
    // we're doing this because there might be several videos on the page
    // that are pushing things down on the page as they load
    this.dimensionsTimer_ = new goog.Timer(500);
    this.handler_.listen(this.dimensionsTimer_,
                         goog.Timer.TICK,
                         this.repositionTimerTick_);
    this.repositionCount_ = 0;
    this.dimensionsTimer_.start();
    // also listen for page resize.
    var vsm = new goog.dom.ViewportSizeMonitor();
    this.handler_.listen(
        vsm, goog.events.EventType.RESIZE,
        this.reposition_);
};
mirosubs.widget.WidgetDecorator.prototype.repositionTimerTick_ =
    function(event) 
{
    this.reposition_();
    this.repositionCount_++;
    if (this.repositionCount_ > 80) // 40 seconds
        this.dimensionsTimer_.stop();
};
mirosubs.widget.WidgetDecorator.prototype.reposition_ = function() {
    mirosubs.repositionToLowerLeft(
        this.videoPlayer_.getElement(),
        this.videoTab_.getElement());
};

mirosubs.widget.WidgetDecorator.prototype.playAt = function(time) {
    this.videoPlayer_.setPlayheadTime(time);
    this.videoPlayer_.play();
};

mirosubs.widget.WidgetDecorator.prototype.play = function() {
    this.videoPlayer_.play();
};

mirosubs.widget.WidgetDecorator.prototype.pause = function() {
    this.videoPlayer_.pause();
};

mirosubs.widget.WidgetDecorator.prototype.openMenu = function() {
    this.controller_.openMenu();
};

mirosubs.widget.WidgetDecorator.exportJSSymbols = function(){
        goog.exportProperty(
        mirosubs.widget.WidgetDecorator.prototype,
        "play",
        mirosubs.widget.WidgetDecorator.prototype.play );
    goog.exportProperty(
        mirosubs.widget.WidgetDecorator.prototype,
        "pause",
        mirosubs.widget.WidgetDecorator.prototype.pause );
    goog.exportProperty(
        mirosubs.widget.WidgetDecorator.prototype,
        "playAt",
        mirosubs.widget.WidgetDecorator.prototype.playAt );

    goog.exportProperty(
        mirosubs.widget.WidgetDecorator.prototype,
        "openMenu",
        mirosubs.widget.WidgetDecorator.prototype.openMenu );

    goog.exportSymbol(
        "mirosubs.widget.Widget.getWidgetByURL",
        mirosubs.widget.Widget.getWidgetByURL);
   goog.exportSymbol(
        "mirosubs.widget.Widget.getAllWidgets",
        mirosubs.widget.Widget.getAllWidgets);
}
