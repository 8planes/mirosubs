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
from videos.types import video_type_registrar, VideoTypeError
import feedparser
from socket import gaierror
from django.utils.translation import ugettext_lazy as _

feed_parsers = []

class FeedParserError(Exception):
    pass

class VideoTypeParseError(FeedParserError, VideoTypeError):
    """
    This is wrapper for VideoTypeError, just to catch these errors with 
    "except FeedParserError" and allow catch with "except VideoTypeError"
    """
    pass

class FeedParser(object):
    """
    This class allow get videos fron feed entries. 
    See videos.tests.TestFeedParser for details.
    """
    
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.feed = feedparser.parse(feed_url)
        self.parser = None
        
    def items(self, reverse=False, until=False, ignore_error=False):
        """
        Iterator witch parse every entry and return VideoType instance if possible and
        additional info. Iterate entries from the most old to the newest 
        """
        if reverse:
            entries = self.feed['entries']
        else:
            entries = self.feed['entries'][::-1]
            
        for entry in entries:
            if until and entry.link == until:
                break
            
            vt, info, entry = None, {}, entry
            
            if self.parser:
                #little optimization. we save last success parser, so should not
                #check all again. As feed can contain a lot of entries, this
                #can be useful
                try:
                    vt, info = self._parse(entry, self.parser)
                except FeedParserError, e:
                    if not ignore_error:
                        raise e
            
            if vt is None:
                for parser in feed_parsers:
                    if parser == self.parser:
                        #we have parsed with this parser
                        continue
                    
                    try:
                        vt, info = self._parse(entry, parser)
                    except FeedParserError, e:
                        if not ignore_error:
                            raise e
                        
                    if vt:
                        self.parser = parser
                        break
                    
            yield vt, info, entry
    
    def _parse(self, entry, parser):
        """
        This is just to incapsulate all exception handling in one place 
        """
        try:
            return parser(entry)
        except VideoTypeError, e:
            raise VideoTypeParseError(e)
        except gaierror:
            raise FeedParserError(_(u'Feed is unavailable now.'))
        
class BaseFeedEntryParser(object):
    
    def get_video_type(self, entry):
        raise Exception('Not implemented')
    
    def get_video_info(self, entry):
        raise Exception('Not implemented')
    
    def __call__(self, entry):
        vt = self.get_video_type(entry)
        if vt:
            info = self.get_video_info(entry)
        else:
            info = {}
        return vt, info
    
class LinkFeedEntryParser(BaseFeedEntryParser):
    """
    This feed entry parser just check "link" atribute of entry. 
    So this works for sites witch are supported by UniSub. 
    For example: Youtube, Vimeo, Blip.Tv.
    For development can use these links:
    https://gdata.youtube.com/feeds/api/users/universalsubtitles/uploads
    """
    
    def get_video_type(self, entry):
        vt = None
        try:
            vt = video_type_registrar.video_type_for_url(entry['link'])
        except KeyError:
            pass
        return vt
    
    def get_video_info(self, entry):
        return {}

feed_parsers.append(LinkFeedEntryParser())

class VideodownloadFeedEntryParser(BaseFeedEntryParser):
    """
    This parser check "videodownload" attribute. 
    It was developed to parse MIT feed.
    For development can use these links:
    http://ocw.mit.edu/rss/new/ocw_youtube_videos.xml
    """
    
    def get_video_type(self, entry):
        vt = None
        try:
            vt = video_type_registrar.video_type_for_url(entry['videodownload'])
        except KeyError:
            pass
        return vt
    
    def get_video_info(self, entry):
        return {}
    
feed_parsers.append(VideodownloadFeedEntryParser())