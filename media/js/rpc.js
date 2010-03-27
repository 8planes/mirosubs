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

mirosubs.Rpc.BASE_URL = "";

mirosubs.Rpc.logger_ =
    goog.debug.Logger.getLogger('mirosubs.Rpc');

mirosubs.Rpc.call = function(methodName, args, opt_callback) {
    var s = goog.json.serialize;
    var p = goog.json.parse;
    var serializedArgs = {};
    for (var param in args)
        serializedArgs[param] = s(args[param]);
    mirosubs.Rpc.logger_.info('calling ' + methodName + ': ' + s(args));
    if (mirosubs.Rpc.BASE_URL.substr(0, 1) != '/' && 
        !goog.Uri.haveSameDomain(mirosubs.Rpc.BASE_URL, window.location.href)) {
        goog.net.CrossDomainRpc.send([mirosubs.Rpc.BASE_URL, "xd/", methodName].join(''),
                                     function(event) {
                                         var responseText = event["target"]
                                             ["responseText"];
                                         mirosubs.Rpc.logger_.info(methodName + 
                                                                   ' response: ' +
                                                                   responseText);
                                         if (opt_callback)
                                             opt_callback(p(responseText))
                                     }, "POST",
                                     serializedArgs);
    } else {
        var postContent = "";
        var isFirst = true;
        for (var param in serializedArgs) {
            if (!isFirst)
                postContent += "&";
            isFirst = false;
            postContent += (param + "=" + encodeURIComponent(serializedArgs[param]));
        }
        goog.net.XhrIo.send([mirosubs.Rpc.BASE_URL, "xhr/", methodName].join(''),
                            function(event) {
                                if (opt_callback)
                                    opt_callback(event.target.getResponseJson());
                            }, "POST",
                            postContent);
    }
};
