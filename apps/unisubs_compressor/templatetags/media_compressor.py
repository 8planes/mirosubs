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

should_compress = None

@register.simple_tag
def include_bundle(bundle_name):
    global should_compress
    if should_compress is None:
        should_compress = getattr(settings, "COMPRESS_MEDIA",
                                  not getattr(settings, "DEBUG", False))
    bundle_type = settings.MEDIA_BUNDLES.get(bundle_name)["type"]

    urls = []
    if  should_compress == True:
        base = ""
        if bundle_type == "css":
            base =  "css-compressed/"
        elif bundle_type == "js":
            base = "js/"
        urls += ["%s%s.%s" % ( base, bundle_name, bundle_type)]
    else:
        if bundle_type == "js":
            urls = list(settings.JS_BASE_DEPENDENCIES)
        urls += settings.MEDIA_BUNDLES.get(bundle_name)["files"]
        
        if should_compress:
            logger.warning("could not find final url for %s" % bundle_name)

    return template.loader.render_to_string("uni_compressor/%s_links.html" % bundle_type,{
        "urls":urls,
        "MEDIA_URL": settings.MEDIA_URL,
        "bundle_type": bundle_type,
    })
                           
