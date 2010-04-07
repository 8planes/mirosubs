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

goog.provide('mirosubs.subtitle.ReviewPanel');

mirosubs.subtitle.ReviewPanel = function(subtitles, videoPlayer, 
                                         captionManager) {
    mirosubs.subtitle.SyncPanel.call(this, subtitles, videoPlayer, 
                                     captionManager);
};
goog.inherits(mirosubs.subtitle.ReviewPanel, mirosubs.subtitle.SyncPanel);
/**
 * @override
 */
mirosubs.subtitle.ReviewPanel.prototype.createRightPanel = 
    function(serverModel) 
{
    var helpContents = new mirosubs.RightPanel.HelpContents(
        "STEP 3: Review and make corrections",
        [["Now it's time to watch your subtitles, making changes if ", 
          "neccesary. Double click on any subtitle to edit its text."]
         .join(''),
         ["If a subtitle changes too late, skip back and tap spacebar ",
          "when it should change. If a subtitle changes too soon, hold ", 
          "down spacebar to delay it until you let go."].join(''),
         ["You can also edit timing with your mouse. Just rollover any ", 
          "timestamp, and click the up/down buttons that appear."].join('')],
        "Watch a video about how to edit",
        "http://youtube.com");
    var KC = goog.events.KeyCodes;
    // FIXME: Tiny bit of duplication. Can be fixed thru inheritance from 
    // common abstract superclass
    var keySpecs = [
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-begin', 'mirosubs-spacebar', 'spacebar', 
            'Advance/Delay Subtitle', KC.SPACE),
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-play', 'mirosubs-tab', 'tab', 'Play/Pause', KC.TAB),
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-skip', 'mirosubs-control', 'control', 
            'Skip Back 8 Seconds', KC.CTRL)
    ];
    return new mirosubs.RightPanel(
        serverModel, helpContents, keySpecs, true, "Done?", 
        "Submit your work");
};