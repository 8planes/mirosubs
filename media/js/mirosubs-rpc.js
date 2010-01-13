goog.provide('mirosubs.Rpc');

mirosubs.Rpc.BASE_URL = "";

mirosubs.Rpc.call = function(methodName, args, opt_callback) {
    var s = goog.json.serialize;
    var p = goog.json.parse;
    var serializedArgs = {};
    for (var param in args)
        serializedArgs[param] = s(args[param]);
    if (!goog.Uri.haveSameDomain(mirosubs.Rpc.BASE_URL, window.location.href))
        goog.net.CrossDomainRpc.send([mirosubs.Rpc.BASE_URL, "xd/", methodName].join(''),
                                     function(event) {
                                         if (opt_callback)
                                             opt_callback(p(event["target"]
                                                            ["responseText"]))
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
        goog.net.XhrIo.send([mirosubs.Rpc.BASE_URL, "xhr/", methodName].join(''),
                            function(data) {
                                console.log("XhrIo send completed: " + data);
                            }, "POST",
                            postContent);
    }
};
