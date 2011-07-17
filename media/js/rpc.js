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


goog.provide('mirosubs.Rpc');

/**
 * In milliseconds
 * @type {number}
 */
mirosubs.Rpc.TIMEOUT_ = 15000;

if (goog.DEBUG) {
    mirosubs.Rpc.logger_ =
        goog.debug.Logger.getLogger('mirosubs.Rpc');
}

mirosubs.Rpc.baseURL = function() {
    return [mirosubs.siteURL(), 
            '/widget/',
            mirosubs.IS_NULL ? 'null_' : '',
            'rpc/'].join('');
};

mirosubs.Rpc.callXhr_ = function(methodName, serializedArgs, opt_callback, opt_errorCallback) {
    goog.net.XhrIo.send(
        [mirosubs.Rpc.baseURL(), 'xhr/', methodName].join(''),
        function(event) {
            if (!event.target.isSuccess()) {
                var status = null;
                if (event.target.getLastErrorCode() != goog.net.ErrorCode.TIMEOUT)
                    status = event.target.getStatus();
                if (opt_errorCallback)
                    opt_errorCallback(status);
            }
            else {
                mirosubs.Rpc.logResponse_(
                    methodName, 
                    event.target.getResponseText());
                if (opt_callback)
                    opt_callback(event.target.getResponseJson());
            }
        },
        "POST", 
        mirosubs.Rpc.encodeKeyValuePairs_(serializedArgs),
        null, mirosubs.Rpc.TIMEOUT_);
};

mirosubs.Rpc.encodeKeyValuePairs_ = function(serializedArgs) {
    var queryData = new goog.Uri.QueryData();
    for (var param in serializedArgs)
        queryData.set(param, serializedArgs[param]);
    return queryData.toString();
};

mirosubs.Rpc.callWithJsonp_ = function(methodName, serializedArgs, opt_callback, opt_errorCallback) {
    var jsonp = new goog.net.Jsonp(
        [mirosubs.Rpc.baseURL(), 'jsonp/', methodName].join(''));
    jsonp.setRequestTimeout(mirosubs.Rpc.TIMEOUT_);
    jsonp.send(
        serializedArgs,
        function(result) {
            if (mirosubs.DEBUG)
                mirosubs.Rpc.logResponse_(
                    methodName, goog.json.serialize(result));
            if (opt_callback)
                opt_callback(result);
        },
        function(errorPayload) {
            if (opt_errorCallback)
                opt_errorCallback();
        });
};

mirosubs.Rpc.logCall_ = function(methodName, args, channel) {
    if (goog.DEBUG) {
        mirosubs.Rpc.logger_.info(
            ['calling ', methodName, ' with ', channel,
             ': ', goog.json.serialize(args)].join(''));
    }
};

mirosubs.Rpc.logResponse_ = function(methodName, response) {
    if (goog.DEBUG) {
        if (mirosubs.DEBUG)
            mirosubs.Rpc.logger_.info(
                [methodName, ' response: ', response].join(''));
    }
};

/**
 *
 * @param {function(?number)=} opt_errorCallback Gets called on error. 
 *     Will include http code if there was a server error and a 
 *     descriptive strategy is used
 * @param {boolean=} opt_forceDescriptive This forces a call strategy 
 *     that returns an http code to opt_errorCallback on server error.
 *     Right now, this means that cross-domain uses CrossDomainRpc instead
 *     of rpc.
 */
mirosubs.Rpc.call = 
    function(methodName, args, opt_callback, opt_errorCallback, opt_forceDescriptive) 
{
    var s = goog.json.serialize;
    var serializedArgs = {};
    var arg;
    var totalSize = 0;
    for (var param in args) {
        arg = s(args[param]);
        serializedArgs[param] = arg;
        totalSize += arg.length;
    }
    var callType = ''
    if (mirosubs.isEmbeddedInDifferentDomain()) {
        goog.asserts.assert(!opt_forceDescriptive);
        callType = 'jsonp';
        mirosubs.Rpc.callWithJsonp_(
            methodName, serializedArgs, 
            opt_callback, opt_errorCallback);
    } else {
        callType = 'xhr';
        mirosubs.Rpc.callXhr_(
            methodName, serializedArgs, 
            opt_callback, opt_errorCallback);
    }
    mirosubs.Rpc.logCall_(methodName, args, callType);
};

