var MiroSubs = function() {
    var jQueryLoadParams = {
        loaded : function() { return typeof(jQuery) != 'undefined'; },
        url : "http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js",
        name : "jquery"
    };
    var jQueryUILoadParams = {
        loaded : function() { return typeof(jQuery.ui) != 'undefined'; },
        url: "http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js",
        name : "jqueryui"
    };
    var afterJSLoad = function(loadParams, fun) {
        if (loadParams.loaded())
            fun();
        else {
            var windowKey = "MiroSubsJSLoaded_" + loadParams.name;
            if (typeof(window[windowKey]) == 'undefined') {
                window[windowKey] = 'loading';
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = loadParams.url;
                script.charset = 'UTF-8';
                document.getElementsByTagName('head')[0].appendChild(script);
            }
            var timer = {};
            timer.intervalID = setInterval(function() {
                    if (loadParams.loaded()) {
                        clearInterval(timer.intervalID);
                        fun();
                    }
                }, 250);
        }
    };
    var afterJQuery = function(fun) {
        afterJSLoad(jQueryLoadParams, 
                    function() { 
                        afterJSLoad(jQueryUILoadParams, fun); 
                    });
    };
    var login_impl = function() {
        var base_url = "http://localhost:8000/widget/login";
        var to_redirect = encodeURIComponent(window.location);
        base_url += ("?" + (new Date()).getTime() +
                     "&to_redirect=" + to_redirect);
        var html = ['<div><iframe ', 
                    'marginwidth="0" marginheight="0" hspace="0" ',
                    'vspace="0" frameborder="0" allowtransparency="true" ',
                    'src="', base_url,
                    '"</iframe></div>'].join('');
        var dialog = $(html).dialog({
                resizable : false,
                modal : true,
                dialogClass : 'MiroSubs-login',
                draggable : false
            });
        dialog.dialog('open');
    };
    return {
        init : function() {
            afterJQuery(function() {});
        },
        embed_player : function(identifier) {
            
        },
        login : function() {
            afterJQuery(login_impl);
        }
    };
}();
// start loading prerequisite libraries now.
MiroSubs.init();
for (var i = 0; i < window.MiroSubsToEmbed.length; i++)
    MiroSubs.embed_player(window.MiroSubsToEmbed[i]);