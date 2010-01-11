goog.provide('mirosubs.RPC');

mirosubs.Rpc = {};

/**
 *
 * @param baseURL {string} base URL for RPC requests on server.
 */
mirosubs.Rpc.call = function(baseURL, methodName, args, opt_callback) {
    var s = new goog.json.Serializer();
    var p = new goog.json.Parser();
    var serializedArgs = {};
    for (var param in args)
        serializedArgs[param] = s.serialize(args[param]);
    if (!goog.Uri.haveSameDomain(baseURL, window.location.href))
        goog.net.CrossDomainRpc.send([baseURL, "xd/", methodName].join(''),
                                     function(event) {
                                         if (opt_callback)
                                             opt_callback(event["target"]["responseText"]);
                                     }, "POST",
                                     serializedArgs);
    else {
        var postContent = "";
        var isFirst = true;
        for (var param in serializedArgs) {
            if (!isFirst)
                postContent += "&";
            isFirst = false;
            postContent += (param + "=" + encodeURIComponent(serializedArgs[param]));
        }
        goog.net.XhrIo.send([baseURL, methodName].join(''),
                            function(data) {
                                console.log("XhrIo send completed: " + data);
                            }, "POST",
                            postContent);
    }
};
