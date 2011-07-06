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

goog.provide('mirosubs.widget.ResumeEditingRecord');

/**
 * @constructor
 */
mirosubs.widget.ResumeEditingRecord = function(videoID, sessionPK, openDialogArgs) {
    this.videoID_ = videoID;
    this.sessionPK_ = sessionPK;
    this.openDialogArgs_ = openDialogArgs;
};

mirosubs.widget.ResumeEditingRecord.STORAGE_KEY_ = "_unisubs_editing";

mirosubs.widget.ResumeEditingRecord.prototype.matches = function(videoID, openDialogArgs) {
    return videoID == this.videoID_ &&
        this.openDialogArgs_.matches(openDialogArgs);
};

mirosubs.widget.ResumeEditingRecord.prototype.save = function() {
    mirosubs.saveInLocalStorage(
        mirosubs.widget.ResumeEditingRecord.STORAGE_KEY_,
        goog.json.serialize({
            'videoID': this.videoID_,
            'sessionPK': this.sessionPK_,
            'openDialogArgs': this.openDialogArgs_.toObject()
        }));
        
};

mirosubs.widget.ResumeEditingRecord.prototype.getSavedSubtitles = function() {
    if (!this.savedSubtitles_) {
        var savedSubtitles = mirosubs.widget.SavedSubtitles.fetchLatest();
        if (savedSubtitles && savedSubtitles.SESSION_PK == this.sessionPK_)
            this.savedSubtitles_ = savedSubtitles;
        else
            this.savedSubtitles_ = null;
    }
    return this.savedSubtitles_;
};

mirosubs.widget.ResumeEditingRecord.clear = function() {
    mirosubs.removeFromLocalStorage(
        mirosubs.widget.ResumeEditingRecord.STORAGE_KEY_);
};

mirosubs.widget.ResumeEditingRecord.fetch = function() {
    var jsonText = mirosubs.fetchFromLocalStorage(
        mirosubs.widget.ResumeEditingRecord.STORAGE_KEY_);
    if (jsonText) {
        var obj = goog.json.parse(jsonText);
        return new mirosubs.widget.ResumeEditingRecord(
            obj['videoID'],
            obj['sessionPK'], 
            mirosubs.widget.OpenDialogArgs.fromObject(
                obj['openDialogArgs']));
    }
    else
        return null;
};