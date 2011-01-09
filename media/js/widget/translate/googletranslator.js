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

mirosubs.translate.GoogleTranslator.baseUri = new goog.Uri("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0");

mirosubs.translate.GoogleTranslator.jsonp = new goog.net.Jsonp(mirosubs.translate.GoogleTranslator.baseUri);

mirosubs.translate.GoogleTranslator.queryMaxLen = 4000;

mirosubs.translate.GoogleTranslator.delimiter = '<dlmt>';

mirosubs.translate.GoogleTranslator.cleanString = function(str){
    return str.replace('<dlmt>', '');
};

mirosubs.translate.GoogleTranslator.translate = function(text, fromLang, toLang, callback){
    fromLang = fromLang || '';
    mirosubs.translate.GoogleTranslator.jsonp.send({
        q: text,
        langpair: fromLang+'|'+toLang
    }, callback, function(){
        //TODO: show pretty error
        alert('Translating servise is unavailable. Try later.')
    });
};

mirosubs.translate.GoogleTranslator.get_translate_widgets_callback = function(widgets, callback){
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    
    return function(response){
        if (response.responseStatus == 200){
            var translations = response.responseData.translatedText.split(d);
            callback(translations, widgets);
        }else{
            callback([], widgets, response.responseDetails);
        };
    }
};

mirosubs.translate.GoogleTranslator.translate_widgets = 
function(need_tarnslating, fromLang, toLang, callback){
    var ml = mirosubs.translate.GoogleTranslator.queryMaxLen;
    var d = mirosubs.translate.GoogleTranslator.delimiter;
    var clean_str = mirosubs.translate.GoogleTranslator.cleanString;
    var translate = mirosubs.translate.GoogleTranslator.translate;
    var get_callback = mirosubs.translate.GoogleTranslator.get_translate_widgets_callback;
    
    //ml = 250; for debuging multiple requests

    var to_translate = [];
    var widgets_to_translate = [];
    
    goog.array.forEach(need_tarnslating, function(w){
        var t = clean_str(w.getSubtitle().text);
        
        to_translate.push(t), widgets_to_translate.push(w);
        
        if (to_translate.join(d).length >= ml){
            to_translate.pop(), widgets_to_translate.pop();
            
            translate(to_translate.join(d), fromLang, toLang, get_callback(widgets_to_translate, callback))
            
            if (t.length > ml){
                to_translate, widgets_to_translate = [];
            }else{
                to_translate = [t], widgets_to_translate = [w];
            }
        };
    });
    if (to_translate.length){
        translate(to_translate.join(d), fromLang, toLang, get_callback(widgets_to_translate, callback));
    };
};