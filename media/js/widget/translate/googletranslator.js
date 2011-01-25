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

goog.provide('mirosubs.translate.GoogleTranslator');

/**
 * Uri for jsonp handler
 * @type {goog.Uri}
 */
mirosubs.translate.GoogleTranslator.baseUri_ = new goog.Uri("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0");

/**
 * Jsonp handler for Gogle Translator API
 * @type {goog.net.Jsonp}
 */
mirosubs.translate.GoogleTranslator.jsonp = new goog.net.Jsonp(mirosubs.translate.GoogleTranslator.baseUri_);

/**
 * Maximum length of text to translate
 * @type {number}
 */
mirosubs.translate.GoogleTranslator.queryMaxLen = 4000;

/**
 * Delimiter for stings to translate
 * @type {string}
 */
mirosubs.translate.GoogleTranslator.delimiter = '<dlmt>';

/**
 * Remove delimiter from string
 * @param {string} string that should be claned
 * @return {string}
 */
mirosubs.translate.GoogleTranslator.cleanString = function(str) {
    return str.replace('<dlmt>', '');
};

/**
 * Send request to Google Translating API
 * @param {string} Text to translate
 * @param {?string} Language code of text to translate, left empty for auto-detection
 * @param {string} language code for language of result
 * @param {function({Object})} Callback
 */
mirosubs.translate.GoogleTranslator.translate = function(text, fromLang, toLang, callback) {
    fromLang = fromLang || '';
    mirosubs.translate.GoogleTranslator.jsonp.send({
        q: text,
        langpair: fromLang+'|'+toLang
    }, callback, function() {
        //TODO: show pretty error
        alert('Translating service is unavailable. Try later.');
    });
};

/**
 * Return decorated callback for GoogleTranslator
 * @param {Array.<mirosubs.translate.TranslationWidget>} widgets containing subtitles for translation
 * @param {Function} Callback
 * @param {boolean} show loading indicator or not
 * @return {function({Object})} 
 */
mirosubs.translate.GoogleTranslator.getTranslateWidgetsCallback = function(widgets, callback, addLoadingInticator) {
    /**
     * shortcut
     * @type {string}
     */
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    addLoadingInticator = addLoadingInticator || true;

    if (widgets.length && widgets[0]['showLoadingIndicator']) {
        goog.array.forEach(widgets, function(w){
            w.showLoadingIndicator();
        });      
    }
    
    return function(response) {
        if (widgets.length && widgets[0]['hideLoadingIndicator']) {
            goog.array.forEach(widgets, function(w){
                w.hideLoadingIndicator();
            });      
        };
        if (response.responseStatus == 200) {
            var translations = response.responseData.translatedText.split(d);
            callback(translations, widgets);
        }else{
            alert(response.responseDetails+' This language can be unsupprted by Google Translator.')
            callback([], widgets, response.responseDetails);
        };
    }
};

/**
 * Transalte subtitles from widgets with GoogleTranslator.translate
 * @param {Array.<mirosubs.translate.TranslationWidget>}
 * @param {?string} Language code of text to translate, left empty for auto-detection
 * @param {string} Language code for language of result
 * @param {function(Array.<string>, Array.<mirosubs.translate.TranslationWidget>, ?string)} Callback
 */
mirosubs.translate.GoogleTranslator.translateWidgets = 
function(needTranslating, fromLang, toLang, callback) {
    var ml = mirosubs.translate.GoogleTranslator.queryMaxLen;
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    var cleanStr = mirosubs.translate.GoogleTranslator.cleanString;
    var translate = mirosubs.translate.GoogleTranslator.translate;
    var getCallback = mirosubs.translate.GoogleTranslator.getTranslateWidgetsCallback;
    
    //ml = 250; for debuging multiple requests
    
    /**
     * Array of subtitles to translate in one request(max length < GoogleTranslator.queryMaxLen)
     * @type {Array.<string>}
     */
    var toTranslate = [];
    /**
     * Widgets with subtitles to translate in one request
     * @type {Array.<mirosubs.translate.TranslationWidget>}
     */    
    var widgetsToTranslate = [];
    
    goog.array.forEach(needTranslating, function(w) {
        /**
         * @type {string}
         */
        var t = cleanStr(w.getOriginalValue());
        
        toTranslate.push(t), widgetsToTranslate.push(w);
        
        if (toTranslate.join(d).length >= ml) {
            toTranslate.pop(), widgetsToTranslate.pop();
            
            translate(toTranslate.join(d), fromLang, toLang, getCallback(widgetsToTranslate, callback))
            
            if (t.length > ml) {
                toTranslate = widgetsToTranslate = [];
            } else {
                toTranslate = [t], widgetsToTranslate = [w];
            }
        };
    });
    if (toTranslate.length) {
        translate(toTranslate.join(d), fromLang, toLang, getCallback(widgetsToTranslate, callback));
    };
};