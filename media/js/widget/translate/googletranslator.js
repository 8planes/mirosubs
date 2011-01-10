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

mirosubs.translate.GoogleTranslator.baseUri_ = new goog.Uri("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0");

mirosubs.translate.GoogleTranslator.jsonp = new goog.net.Jsonp(mirosubs.translate.GoogleTranslator.baseUri_);

mirosubs.translate.GoogleTranslator.queryMaxLen = 4000;

mirosubs.translate.GoogleTranslator.delimiter = '<dlmt>';

mirosubs.translate.GoogleTranslator.cleanString = function(str) {
    return str.replace('<dlmt>', '');
};

mirosubs.translate.GoogleTranslator.translate = function(text, fromLang, toLang, callback) {
    fromLang = fromLang || '';
    mirosubs.translate.GoogleTranslator.jsonp.send({
        q: text,
        langpair: fromLang+'|'+toLang
    }, callback, function() {
        //TODO: show pretty error
        alert('Translating servise is unavailable. Try later.');
    });
};

mirosubs.translate.GoogleTranslator.getTranslateWidgetsCallback = function(widgets, callback) {
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    
    return function(response) {
        if (response.responseStatus == 200) {
            var translations = response.responseData.translatedText.split(d);
            callback(translations, widgets);
        }else{
            callback([], widgets, response.responseDetails);
        };
    }
};

mirosubs.translate.GoogleTranslator.translateWidgets = 
function(need_tarnslating, fromLang, toLang, callback) {
    var ml = mirosubs.translate.GoogleTranslator.queryMaxLen;
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    var cleanStr = mirosubs.translate.GoogleTranslator.cleanString;
    var translate = mirosubs.translate.GoogleTranslator.translate;
    var getCallback = mirosubs.translate.GoogleTranslator.getTranslateWidgetsCallback;
    
    //ml = 250; for debuging multiple requests

    var ToTranslate = [];
    var widgetsToTranslate = [];
    
    goog.array.forEach(need_tarnslating, function(w) {
        var t = cleanStr(w.getSubtitle().text);
        
        ToTranslate.push(t), widgetsToTranslate.push(w);
        
        if (ToTranslate.join(d).length >= ml) {
            ToTranslate.pop(), widgetsToTranslate.pop();
            
            translate(ToTranslate.join(d), fromLang, toLang, getCallback(widgetsToTranslate, callback))
            
            if (t.length > ml) {
                ToTranslate, widgetsToTranslate = [];
            } else {
                ToTranslate = [t], widgetsToTranslate = [w];
            }
        };
    });
    if (ToTranslate.length) {
        translate(ToTranslate.join(d), fromLang, toLang, getCallback(widgetsToTranslate, callback));
    };
};