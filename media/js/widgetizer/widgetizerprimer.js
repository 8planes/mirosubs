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

mirosubs.video.WidgetizerPrimer.prime = function() {
    var w = window;
    var ytReady = "onYouTubePlayerReady";
    var oldReady = w[ytReady] || function() {};
    var apiIDArrayName = "unisubs_readyAPIIDs";
    var apiIDArray = w[apiIDArrayName] = w[apiidArrayName] || [];
    window[ytReady] = function(apiID) {
        try {
            oldReady(apiID);
        }
        catch (e) {
            // don't care
        }
        if (apiID == "undefined" || !apiID)
            apiID = "";
        apiIDArray.push(apiID);
    };
};

mirosubs.video.WidgetizerPrimer.prime();