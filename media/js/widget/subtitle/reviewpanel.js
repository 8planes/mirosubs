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
                                         serverModel, captionManager) {
    mirosubs.subtitle.SyncPanel.call(this, subtitles, videoPlayer,
                                     serverModel, captionManager);
};
goog.inherits(mirosubs.subtitle.ReviewPanel, mirosubs.subtitle.SyncPanel);
/**
 * @override
 */
mirosubs.subtitle.ReviewPanel.prototype.createRightPanelInternal =
    function()
{
    var helpContents = new mirosubs.RightPanel.HelpContents(
        "FINAL STEP: Review and make corrections",
        [["Now it's time to watch your subtitles, making changes if ",
          "neccesary. Click on any subtitle to edit its text."]
         .join(''),
         ["Adjust subtitle timing by dragging their edges in the ",
          "timeline to the left and watching the results."].join(''),
         ["You can also edit timing by rolling over any timestamp, ",
          "and clicking the left/right buttons that appear. After ",
          "you click, your change will play back."].join(''),
         "You can still use the down arrow too, to start the next subtitle."],
        3, 2);
    return new mirosubs.RightPanel(
        this.serverModel, helpContents, [],
        this.makeKeySpecsInternal(), false, "Done?",
        "Submit your work");
};