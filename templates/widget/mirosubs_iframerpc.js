{# meant to be included in mirosubs_widget.js #}
MiroSubs.IFrameRPC = function() {
    var next_id = function() {
        if (typeof(window.MiroSubsNextIFrameID) == 'undefined')
            window.MiroSubsNextIFrameID = 0;
        return window.MiroSubsNextIFrameID++;
    };
    var add_textarea = function(doc, form, name, value) {
        var textarea = doc.createElement("textarea");
        textarea.name = name;
        var text = doc.createTextNode(value);
        textarea.appendChild(text);
        form.appendChild(textarea);
    };
    var callbacks = {};
    return {
        post : function(url, postargs, callback) {
            var id = "msxdrq-" + next_id();

            callbacks[id] = callback;

            var iframe = document.createElement("iframe");
            iframe.id = id;
            iframe.style.position = "absolute";
            iframe.style.top = iframe.style.left = "-5000px";
            document.body.appendChild(iframe);

            var idoc = iframe.contentWindow.document;
            var form = idoc.createElement("form");
            form.action = url;
            form.method = "POST";
            add_textarea(idoc, form, "iframe_id", id);
            for (key in postargs)
                add_textarea(idoc, form, key, postargs[key]);
            iframe.contentWindow.document.body.appendChild(form);
            form.submit();
        },
        post_return : function(id, result) {
            alert("RETURNED!");
            //            document.body.removeChild(document.getElementById(id));
            callbacks[id](result);
            // delete callbacks[id];
        }
    };
}();