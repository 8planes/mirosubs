# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

"""
Functionality for generating srt files.
"""

def captions_and_translations_to_srt(captions_and_translations):
    # TODO: note this loads the entire string into memory, which will not 
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in len(captions_and_translations):
        translation_to_srt(captions_and_translations[i][1],
                           captions_and_translations[i][0],
                           i, output)
    srt = output.getvalue()
    output.close()
    return srt

def captions_to_srt(subtitles):
    # TODO: note this loads the entire string into memory, which will not 
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in len(subtitles):
        subtitle_to_srt(subtitles[i], i, output)
    srt = output.getvalue()
    output.close()
    return srt

def translation_to_srt(translation, video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text if translation is None \
                         else translation.translation_text, 
                         video_caption, index, output)

def subtitle_to_srt(video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text,
                         video_caption, index, output)

def subtitle_to_srt_impl(text, video_caption, index, output):
    output.write(str(index + 1))
    output.write("\n")
    write_srt_time_line(video_caption, output)
    output.write(text)
    output.write("\n")

def write_srt_time_line(video_caption, output):
    write_srt_time(video_caption.start_time, output)
    output.write(" --> ")
    write_srt_time(video_caption.end_time, output)
    output.write("\n")

def write_srt_time(seconds, output):
    seconds_int = int(seconds)
    write_padded_num((seconds_int / 3600) % 60, 2, output)
    output.write(":")
    write_padded_num((seconds_int / 60) % 60, 2, output)
    output.write(":")
    write_padded_num(seconds_int % 60, 2, output)
    output.write(".")
    write_padded_num(int(seconds * 1000) % 1000, 3, output)

def write_padded_num(num, numchars, output):
    strnum = str(num)
    numzeros = numchars - len(strnum)
    for i in range(numzeros):
        output.write("0")
    output.write(strnum)
