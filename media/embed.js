

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
    var innerStyle = '/* Should only contain css for the actual widget */\u000Adiv.mirosubs\u002Dwidget {\u000A    position: relative !important\u003B\u000A}\u000A.mirosubs\u002DvideoDiv {\u000A    text\u002Dalign: center !important\u003B\u000A}';

    var scriptsToLoad = [
      
        'http://mirosubs.example.com:8000/site_media/js/mirosubs.js',
      
        'http://mirosubs.example.com:8000/site_media/js/rpc.js',
      
        'http://mirosubs.example.com:8000/site_media/js/clippy.js',
      
        'http://mirosubs.example.com:8000/site_media/js/flash.js',
      
        'http://mirosubs.example.com:8000/site_media/js/spinner.js',
      
        'http://mirosubs.example.com:8000/site_media/js/sliderbase.js',
      
        'http://mirosubs.example.com:8000/site_media/js/closingwindow.js',
      
        'http://mirosubs.example.com:8000/site_media/js/loadingdom.js',
      
        'http://mirosubs.example.com:8000/site_media/js/tracker.js',
      
        'http://mirosubs.example.com:8000/site_media/js/style.js',
      
        'http://mirosubs.example.com:8000/site_media/js/messaging/simplemessage.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/video.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/captionview.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/abstractvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/flashvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/html5videoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/youtubevideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/jwvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/flvvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/videosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/html5videosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/youtubevideosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/brightcovevideosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/brightcovevideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/flvvideosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/bliptvplaceholder.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/controlledvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/vimeovideosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/vimeovideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/dailymotionvideosource.js',
      
        'http://mirosubs.example.com:8000/site_media/js/video/dailymotionvideoplayer.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/model.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/videolanguage.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/videolanguages.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/tolanguage.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/tolanguages.js',
      
        'http://mirosubs.example.com:8000/site_media/js/startdialog/dialog.js',
      
        'http://mirosubs.example.com:8000/site_media/js/requestdialog.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/subtitle/editablecaption.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/subtitle/editablecaptionset.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/usersettings.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/logindialog.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/videotab.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/howtovideopanel.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/dialog.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/captionmanager.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/rightpanel.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/basestate.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/subtitlestate.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/dropdowncontents.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/playcontroller.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/subtitlecontroller.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/subtitledialogopener.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/opendialogargs.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/dropdown.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/play/manager.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/widgetcontroller.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/widget.js',
      
        'http://mirosubs.example.com:8000/site_media/js/widget/crossdomainembed.js'
      ];

    var siteConfig = {
        siteURL: 'http://mirosubs.example.com:8000',
        mediaURL: 'http://mirosubs.example.com:8000/site_media/'
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
    if (typeof(mirosubs) == 'undefined' && !window.MiroSubsLoading) {
        window.MiroSubsLoading = true;
        for (var i = 0; i < scriptsToLoad.length; i++) {
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
        css.href = 'http://mirosubs.example.com:8000/site_media/css/mirosubs-widget.css';
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
