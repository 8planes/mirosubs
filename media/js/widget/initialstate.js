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

goog.provide('mirosubs.widget.InitialState');

mirosubs.widget.InitialState = function(widget, videoURL, baseState) {
    mirosubs.widget.WidgetState.call(this, widget);
    this.videoURL_ = videoURL;
    this.baseState_ = baseState;
    
    this.videoTabText_ = "Subtitle Me";
};

goog.inherits(mirosubs.widget.InitialState, mirosubs.widget.WidgetState);

mirosubs.widget.InitialState.prototype.initialize = function(callback) {
    var that = this;
    mirosubs.Rpc.call(
        'show_widget', {
            'video_url' : this.videoURL_,
            'base_state': this.baseState_.ORIGINAL_PARAM
        },
        function (result) {
            if (result['subtitles'].length > 0)
                that.videoTabText_ = "Choose Language";
            callback(result); 
        });
};

mirosubs.widget.InitialState.prototype.getVideoTabText = function() {
    return this.videoTabText_;
};
