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
goog.provide('mirosubs.translate.GoogleTranslator.Transaction');

mirosubs.translate.GoogleTranslator.TRANSACTION_ID = 0;

/**
 * @constructor
 */
mirosubs.translate.GoogleTranslator.Transaction = function(){
    this.id = ++mirosubs.translate.GoogleTranslator.TRANSACTION_ID;
    this.actions = [];
    this.withError = false;
};

mirosubs.translate.GoogleTranslator.Transaction.prototype.add = function(toTranslate, fromLang, toLang, widgets, callback){
    this.actions.push([toTranslate, fromLang, toLang, this.getCallback_(widgets, callback)]);
};

mirosubs.translate.GoogleTranslator.Transaction.prototype.onError = function(response){
    if ( ! this.withError){
        this.withError = true;
        alert('Cannot complete automated translation. Error: "'+response['responseDetails']+'".');
    }
};

mirosubs.translate.GoogleTranslator.Transaction.prototype.getCallback_ = function(widgets, callback){
    /**
     * shortcut
     * @type {string}
     */
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    var transaction = this;
    
    if (widgets.length && widgets[0].showLoadingIndicator) {
        goog.array.forEach(widgets, function(w){
            w.showLoadingIndicator();
        });      
    }
    
    return function(response) {
        if (widgets.length && widgets[0].hideLoadingIndicator) {
            goog.array.forEach(widgets, function(w){
                w.hideLoadingIndicator();
            });      
        }
        if (response['responseStatus'] === 200) {
            var translations = response['responseData']['translatedText'].split(d);
            
            var encoded = [];
            for (var i=0, len=translations.length; i<len; i++){
                encoded.push(goog.string.unescapeEntities(translations[i]));
            };

            callback(encoded, widgets);
        }else{
            transaction.onError(response);
            callback([], widgets, response['responseDetails']);
        };
    }    
};

mirosubs.translate.GoogleTranslator.Transaction.prototype.start = function(){
    for (var i=0, len=this.actions.length; i<len; i++){
        mirosubs.translate.GoogleTranslator.translate.apply(null, this.actions[i]);
    }
};

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
mirosubs.translate.GoogleTranslator.queryMaxLen = 1000;

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
 * @param {string} text Text to translate
 * @param {string=} fromLang Language code of text to translate, left empty for auto-detection
 * @param {string} toLang Language code for language of result
 * @param {function({Object})} callback Callback
 */
mirosubs.translate.GoogleTranslator.translate = function(text, fromLang, toLang, callback) {
    fromLang = fromLang || '';
    mirosubs.translate.GoogleTranslator.jsonp.send({
        'q': text,
        'langpair': fromLang+'|'+toLang
    }, callback, function() {
        //TODO: show pretty error
        //Translating service is unavailable. Try later.
    });
};

/**
 * Transalte subtitles from widgets with GoogleTranslator.translate
 * @param {Array.<mirosubs.translate.TranslationWidget>} needTranslating
 * @param {?string} fromLang Language code of text to translate, left empty for auto-detection
 * @param {string} toLang Language code for language of result
 * @param {function(Array.<string>, Array.<mirosubs.translate.TranslationWidget>, ?string)} callback
 */
mirosubs.translate.GoogleTranslator.translateWidgets = 
function(needTranslating, fromLang, toLang, callback) {
    var ml = mirosubs.translate.GoogleTranslator.queryMaxLen;
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    var cleanStr = mirosubs.translate.GoogleTranslator.cleanString;
    var translate = mirosubs.translate.GoogleTranslator.translate;
    
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
    var transaction = new mirosubs.translate.GoogleTranslator.Transaction();
    
    goog.array.forEach(needTranslating, function(w) {
        /**
         * @type {string}
         */
        var t = cleanStr(w.getOriginalValue());
        
        toTranslate.push(t), widgetsToTranslate.push(w);
        
        if (toTranslate.join(d).length >= ml) {
            toTranslate.pop(), widgetsToTranslate.pop();
            
            transaction.add(toTranslate.join(d), fromLang, toLang, widgetsToTranslate, callback);
            
            if (t.length > ml) {
                toTranslate = widgetsToTranslate = [];
            } else {
                toTranslate = [t], widgetsToTranslate = [w];
            }
        };
    });
    if (toTranslate.length) {
        transaction.add(toTranslate.join(d), fromLang, toLang, widgetsToTranslate, callback);
    };
    transaction.start();
};

mirosubs.translate.GoogleTranslator.isTranslateable = function() {
    if (!mirosubs.translate.GoogleTranslator.Languages_ ) {
        /* 
         * @private 
         */
        mirosubs.translate.GoogleTranslator.Languages_ = new goog.structs.Set([
            'af','sq','am','ar','hy','az',
'eu','be','bn','bh','br','bg','my','ca','chr','zh','zh-cn','zh-tw','co','hr','cs',
'da','dv','nl','en','et','fo','tl','fi','fr','fy','gl','ka','de','el','gu',
'ht','iw','hi','hu','is','id','iu','ga','it','ja','jw','kn','kk','km','ko','ku',
'ky','lo','la','lv','lt','lb','mk','ms','ml','mt','mi','mr','mn','ne','no','oc',
'or','ps','fa','pl','pt','pt-pt','pa','qu','ro','ru','sa','gd','sr','sd','si',
'sk','sl','es','su','sw','sv','syr','tg','ta','tt','te','th','bo','to','tr','uk',
'ur','uz','ug','vi','cy','yi','yo','']);
    }
    return mirosubs.translate.GoogleTranslator.Languages_.containsAll(arguments);
}
