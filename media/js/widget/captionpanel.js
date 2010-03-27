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

goog.provide('mirosubs.CaptionPanel');

mirosubs.CaptionPanel = function(videoID, videoPlayer, nullWidget) {
    goog.ui.Component.call(this);
    this.videoID_ = videoID;
    this.videoPlayer_ = videoPlayer;
    this.nullWidget_ = nullWidget;
    this.mainPanel_ = null;
};
goog.inherits(mirosubs.CaptionPanel, goog.ui.Component);

/**
 *
 * @param {function(boolean)} callback 
 */
mirosubs.CaptionPanel.prototype.startSubtitling = function(callback) {
    var that = this;
    mirosubs.Rpc.call("start_editing" + (this.nullWidget_ ? '_null' : ''), 
                      {"video_id": this.videoID_},
                      function(result) {
                          callback(result["can_edit"]);
                          if (result["can_edit"])
                              that.startSubtitlingImpl_(result["version"], 
                                                        result["existing"]);
                          else {
                              if (result["owned_by"])
                                  alert("Sorry, this video is owned by " + 
                                        result["owned_by"]);
                              else
                                  alert("Sorry, this video is locked by " +
                                        result["locked_by"]);
                          }
                      });
};

mirosubs.CaptionPanel.prototype.updateLoginState = function() {
    if (this.mainPanel_ != null) {
        if (mirosubs.currentUsername != null)
            this.mainPanel_.showLoggedIn(mirosubs.currentUsername);
        else
            this.mainPanel_.showLoggedOut();
    }
};

mirosubs.CaptionPanel.prototype.startSubtitlingImpl_ = 
    function(version, existingCaptions) {
    this.addChild(this.mainPanel_ = new mirosubs.subtitle
                  .MainPanel(this.videoPlayer_,
                             new mirosubs.subtitle.MSServerModel(this.videoID_,
                                                                 version,
                                                                 this.nullWidget_),
                             existingCaptions),
                  true);
};

mirosubs.CaptionPanel.prototype.languageSelected = function(languageCode, captions) {
    this.removeChildren();
    if (this.playManager_)
        this.playManager_.dispose();
    this.playManager_ = new mirosubs.play.Manager(this.videoPlayer_, captions);
};

mirosubs.CaptionPanel.prototype.addNewLanguage = function(captions, languages) {
    this.addChild(new mirosubs.translate.MainPanel(
        this.videoPlayer_, this.videoID_, captions, languages, this.nullWidget_), 
                  true);
};