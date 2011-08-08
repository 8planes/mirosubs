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

goog.provide('mirosubs.SRTWriter');

mirosubs.SRTWriter.toSRT = function(jsonSubs) {
    var stringBuffer = new goog.string.StringBuffer();
    for (var i = 0; i < jsonSubs.length; i++)
        mirosubs.SRTWriter.subToSrt_(jsonSubs[i], i, stringBuffer);
    return stringBuffer.toString();
};

mirosubs.SRTWriter.subToSrt_ = function(sub, index, stringBuffer) {
    stringBuffer.
        append(index + 1).
        append("\n");
    mirosubs.SRTWriter.writeSrtTimeLine_(sub, stringBuffer);
    stringBuffer.
        append(sub['text']).
        append("\n\n");
};

mirosubs.SRTWriter.writeSrtTimeLine_ = function(sub, stringBuffer) {
    mirosubs.SRTWriter.writeSrtTime_(sub['start_time'], stringBuffer);
    stringBuffer.append(' --> ');
    mirosubs.SRTWriter.writeSrtTime_(sub['end_time'], stringBuffer);
    stringBuffer.append('\n');
};

mirosubs.SRTWriter.writeSrtTime_ = function(seconds, stringBuffer) {
    if (seconds == -1 || !goog.isDefAndNotNull(seconds)) {
        stringBuffer.append("99:59:59,000");
    }
    else {
        var secondsInt = Math.floor(seconds);
        var p = goog.string.padNumber;
        stringBuffer.
            append(p(Math.floor(secondsInt / 3600) , 2)).
            append(':').
            append(p(Math.floor(secondsInt / 60) % 60, 2)).
            append(':').
            append(p(secondsInt % 60, 2)).
            append(',').
            append(p(Math.floor(seconds * 1000) % 1000, 3));
    }
};
