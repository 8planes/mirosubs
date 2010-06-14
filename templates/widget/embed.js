{% load escapejs %}

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

/**
 * @fileoverview Used for embedding widgets on websites on non-Unisubs domains.
 * 
 * Embed scheme is:
 * <pre>
 * &lt;script type="text/javascript" src="http://url/for/embed.js"&gt;
 * ({
 *     video_url : "http://url/for/video" | video_element: [video element] (currently unsupported),
 *     null_widget: true,
 *     debug_js: false,
 *     subtitle_immediately: false,
 *     autoplay_language: null // blank string for original, or language code for other
 * })
 * &lt;/script&gt;
 *
 * If a video_url is provided instead of video_element, then the widget will
 * generate a video element (or youtube embed element or whatever) and insert it
 * right before the script tag, along with the widget elements/machinery.
 *
 * If a video_element is provided instead of a video_url, then the widget will
 * "wrap" the element. The element can either be a video element or an 
 * object/embed element for a youtube video. This feature is unsupported/experimental
 * right at the moment.
 */

(function() {
    var innerStyle = '{% escapejs %}{% include "widget/widget.css" %}{% endescapejs %}';

    var scriptsToLoad = [
      {% for dep in js_dependencies %}
        '{{dep|safe}}'{% if not forloop.last %},{% endif %}
      {% endfor %}];

    var siteConfig = {
        siteURL: 'http://{{site.domain}}',
        mediaURL: '{{MEDIA_URL}}'
    };

    var scripts = document.getElementsByTagName('script');
    var script = scripts[scripts.length - 1];
    var widgetConfig = (new Function('return ' + 
                               script.innerHTML.replace(/\n|\r/g, '')))();

    var $c = document.createElement;

    var containingElement = $c('div');
    var styleElement = $c('style');
    containingElement.appendChild(styleElement);

    var widgetDiv = $c('div');
    widgetDiv.className = 'mirosubs-widget';
    containingElement.appendChild(widgetDiv);
    script.parentNode.insertBefore(containingElement, script);

    var head = document.getElementsByTagName('head')[0];
    if (typeof(mirosubs) != 'undefined' &&
        typeof(mirosubs.widget) != 'undefined' &&
        typeof(mirosubs.widget.CrossDomainEmbed) != 'undefined')
        mirosubs.widget.CrossDomainEmbed.embed(widgetDiv, widgetConfig, siteConfig);
    else {
        if (!window.MiroSubsLoading) {
            window.MiroSubsLoading = true;
            for (var i = 0; i < scriptsToLoad.length; i++) {
                var curScript = $c('script');
                curScript.type = 'text/javascript';
                curScript.src = scriptsToLoad[i];
                curScript.charset = 'UTF-8';
                head.appendChild(curScript);
            }
        }
        if (typeof(MiroSubsToEmbed) == 'undefined')
            window.MiroSubsToEmbed = [];
        window.MiroSubsToEmbed.push([widgetDiv, widgetConfig, siteConfig]);
    }
    if (!window.MiroCSSLoading) {
        window.MiroCSSLoading = true;
        var css = $c('link');
        css.type = 'text/css';
        css.rel = 'stylesheet';
        css.href = '{{MEDIA_URL}}css/mirosubs-widget.css';
        css.media = 'screen';
        head.appendChild(css);
    }
})();