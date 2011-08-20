{% load escapejs media_compressor %}

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
 *     null_widget: true, // if true, runs in demo mode that does not save work.
 *     debug_js: false,
 *     subtitle_immediately: false,
 *     translate_immediately: false,
 *     base_state: { // omit this param altogether to not load subs at the beginning.
 *         language: 'es',  // omit for native language
 *         revision: 3,     // omit for latest revision
 *         start_playing: false // if true, will start playing as soon as subs load. omit or set to false otherwise.
 *     }
 * })
 * &lt;/script&gt;
 * </pre>
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

    var scriptsToLoad = ["{{js_file}}"];

    var siteConfig = {
        siteURL: 'http://{{current_site.domain}}',
        mediaURL: '{{MEDIA_URL}}'
    };

    var scripts = document.getElementsByTagName('script');
    var script = scripts[scripts.length - 1];
    var widgetConfig = 
        (new Function('return ' + script.innerHTML.replace(/\n|\r/g, '')))();

    var $c = function(tag) { return document.createElement(tag); };
    var containingElement = $c('span');
    containingElement.style.cssText = "display: block !important;";

    containingElement.className = 'cleanslate';

    if (/MSIE 6/i.test(navigator.userAgent)) {
        containingElement.innerHTML = 
            "Sorry, <a href='http://universalsubtitles.org'>Universal " +
            "Subtitles</a> doesn't " +
            "support your browser yet. Upgrade your browser or " +
            "<a href='http://getfirefox.com'>Try Firefox</a>.";
        window.attachEvent(
            'onload',
            function(e) {
                script.parentNode.insertBefore(containingElement, script);
            });
        return;
    }

    var styleElement = $c('style');
    if ('textContent' in styleElement)
        styleElement.textContent = innerStyle;
    else {
        // IE
        styleElement.setAttribute("type", "text/css")
        styleElement.styleSheet.cssText = innerStyle;
    }
    containingElement.appendChild(styleElement);

    var widgetSpan = $c('span');
    widgetSpan.className = 'mirosubs-widget';
    widgetSpan.style.cssText = "display: block !important;";
    containingElement.appendChild(widgetSpan);

    var head = document.getElementsByTagName('head')[0];
    if (typeof(MiroSubsCrossDomainLoaded) == 'undefined' && !window.MiroSubsLoading) {
        window.MiroSubsLoading = true;
        for (var i = 0; i < scriptsToLoad.length; i++) {
            console.log('adding script ' + scriptsToLoad[i]);
            var curScript = $c('script');
            curScript.type = 'text/javascript';
            curScript.src = scriptsToLoad[i];
            curScript.charset = 'UTF-8';
            head.appendChild(curScript);
        }
    }

    if (!window.MiroCSSLoading) {
        window.MiroCSSLoading = true;
        var css = $c('link');
        css.type = 'text/css';
        css.rel = 'stylesheet';
        css.href = '{{MEDIA_URL}}{% url_for "widget-css" %}';
        css.media = 'screen';
        head.appendChild(css);
    }

    var insertCalled = false;

    var insert = function() {
        if (insertCalled)
            return;
        insertCalled = true;
        script.parentNode.insertBefore(containingElement, script);
        if (typeof(mirosubs) != 'undefined' &&
            typeof(mirosubs.widget) != 'undefined' &&
            typeof(mirosubs.widget.CrossDomainEmbed) != 'undefined')
            mirosubs.widget.CrossDomainEmbed.embed(widgetSpan, widgetConfig, siteConfig);
        else {
            if (typeof(MiroSubsToEmbed) == 'undefined')
                window.MiroSubsToEmbed = [];
            window.MiroSubsToEmbed.push([widgetSpan, widgetConfig, siteConfig]);
        }
    }

    if (!document.attachEvent)
        insert(); // not IE
    else {
        // IE
        document.attachEvent("onreadystatechange", function() {
            if (document.readyState == "complete") {
                document.detachEvent("onreadystatechange", arguments.callee);
                insert();
            }
        });
        if (document.documentElement.doScroll && window == window.top)
            (function() {
                if (insertCalled)
                    return;
                try {
                    // Thanks to Diego Perini: http://javascript.nwbox.com/IEContentLoaded/
                    document.documentElement.doScroll('left');
                }
                catch (error) {
                    setTimeout(arguments.callee, 0);
                    return;
                }
                insert();
            })();
    }
})();
