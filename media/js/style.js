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
 * @fileoverview Rewrite of some goog.style that always sets !important,
 *     for use with cleanslatecss.
 */

goog.provide('mirosubs.style');

mirosubs.style.makeCssPropertyRegex_ = function(property) {
    return new RegExp('\\s*' + property + '\\s*:\\s*[^;]*;', 'i');
};

mirosubs.style.findCssProperty_ = function(css, property) {
    return css.match(mirosubs.style.makeCssPropertyRegex_(property));
};

/**
 *
 * @param {Element} elem
 * @param {string} property
 * @param {?string} value or null (to unset)
 */
mirosubs.style.setProperty = function(elem, property, value) {
    elem.style.cssText = mirosubs.style.setPropertyInString(
        elem.style.cssText, property, value);
};

mirosubs.style.setPropertyInString = function(cssString, property, value) {
    var oldDeclaration = mirosubs.style.findCssProperty_(
        cssString, property);
    var newDeclaration = 
        goog.isNull(value) ? 
            '' : [property, ':', value, ' !important;'].join('');
    if (oldDeclaration)
        return cssString.replace(oldDeclaration[0], newDeclaration);
    else {
        cssString = goog.string.trim(cssString);
        if (cssString.length > 0 && !goog.string.endsWith(cssString, ';'))
            cssString += ';';
        return cssString + newDeclaration;
    }
};

/**
 * Sets the width/height values of an element.  If an argument is numeric,
 * or a goog.math.Size is passed, it is assumed to be pixels and will add
 * 'px' after converting it to an integer in string form. (This just sets the
 * CSS width and height properties so it might set content-box or border-box
 * size depending on the box model the browser is using.)
 *
 * @param {Element} element Element to set the size of.
 * @param {string|number|goog.math.Size} w Width of the element, or a
 *     size object.
 * @param {string|number=} opt_h Height of the element. Required if w is not a
 *     size object.
 */
mirosubs.style.setSize = function(element, w, opt_h) {
    var wh = mirosubs.style.processWidthHeightArgs_(w, opt_h);
    mirosubs.style.setWidth(element, /** @type {string|number} */ (wh[0]));
    mirosubs.style.setHeight(element, /** @type {string|number} */ (wh[1]));
};

mirosubs.style.setSizeInString = function(cssString, w, opt_h) {
    var wh = mirosubs.style.processWidthHeightArgs_(w, opt_h);
    cssString = mirosubs.style.setPropertyInString(
        cssString, 'width', mirosubs.style.getPixelStyleValue_(wh[0]));
    return mirosubs.style.setPropertyInString(
        cssString, 'height', mirosubs.style.getPixelStyleValue_(wh[1]));
};

mirosubs.style.processWidthHeightArgs_ = function(w, opt_h) {
    var h;
    if (w instanceof goog.math.Size) {
        h = w.height;
        w = w.width;
    } else {
        if (opt_h == undefined) {
            throw Error('missing height argument');
        }
        h = opt_h;
    }
    return [w, h];
};

mirosubs.style.getPixelStyleValue_ = function(value, round) {
    return goog.isNumber(value) ? 
        ((round ? Math.round(value) : value) + 'px') : value;
};

mirosubs.style.setPixelStyleProperty_ = function(property, round, element, value) {
    mirosubs.style.setProperty(
        element, property, 
        /** @type {string} */(mirosubs.style.getPixelStyleValue_(value)));
};

mirosubs.style.setHeight = goog.partial(
    mirosubs.style.setPixelStyleProperty_, 'height', true);

mirosubs.style.setWidth = goog.partial(
    mirosubs.style.setPixelStyleProperty_, 'width', true);

mirosubs.style.setPosition = function(el, opt_arg1, opt_arg2) {
    var x, y;
    var buggyGeckoSubPixelPos = goog.userAgent.GECKO &&
        (goog.userAgent.MAC || goog.userAgent.X11) &&
        goog.userAgent.isVersion('1.9');

    if (goog.isDefAndNotNull(opt_arg1) && 
        opt_arg1 instanceof goog.math.Coordinate) {
        x = opt_arg1.x;
        y = opt_arg1.y;
    } else {
        x = opt_arg1;
        y = opt_arg2;
    }

    if (goog.isDefAndNotNull(x))
        mirosubs.style.setPixelStyleProperty_(
            'left', buggyGeckoSubPixelPos, el,
            /** @type {number|string} */ (x));
    if (goog.isDefAndNotNull(y))
        mirosubs.style.setPixelStyleProperty_(
            'top', buggyGeckoSubPixelPos, el,
            /** @type {number|string} */ (y));
};

mirosubs.style.showElement = function(el, display) {
    mirosubs.style.setProperty(el, 'display', display ? null : 'none');
};

mirosubs.style.setVisibility = function(el, visible) {
    mirosubs.style.setProperty(
        el, 'visibility', visible ? 'visible' : 'hidden');
};