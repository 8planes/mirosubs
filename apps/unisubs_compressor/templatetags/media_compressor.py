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

from django import template

register = template.Library()
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

@register.inclusion_tag("uni_compressor/css_links.html")
def include_css_bundle(bundle_name):
    mbu = getattr(settings, "MEDIA_BUNDLE_URLS", {})
    url = mbu.get( bundle_name, None)
    if url is not None:
        urls = ["%s/%s" % (settings.COMPRESS_OUTPUT_DIRNAME, url)]
    else:
        urls = settings.MEDIA_BUNDLES.get(bundle_name)["files"]
        logger.warning("could not find final url for %s" % bundle_name)
    return {
        "urls":urls,
        "MEDIA_URL": settings.MEDIA_URL
    }    
                           
