var mirosubs = mirosubs || {};

mirosubs.login = function() {
    var base_url = ["http://localhost:8000/widget/login?", 
                    '' + (new Date()).getTime(),
                    "&to_redirect=", 
                    encodeURIComponent(window.location)].join('');
    var html = ['<div><iframe marginwidth="0" marginheight="0" hspace="0" ',
                'vspace="0" frameborder="0" allowtransparency="true" src="', 
                base_url,
                '"</iframe></div>'].join('');
    var dialog = new goog.ui.Dialog("mirosubs-modal-dialog", true);
    dialog.setContent(html);
    dialog.setTitle("Login or Sign Up");
    dialog.setVisible(true);
};

mirosubs.saveCaptionWork = function(video_id, updatedCaptions, 
                                    insertedCaptions, deletedCaptions) {
    var s = new goog.json.Serializer();
    goog.net.CrossDomainRpc.send("http://localhost:8000/widget/save_captions/",
                              function(event) { alert(event.target.responseText) },
                              "POST",
                              { video_id : video_id + '',
                                updated : s.serialize(updatedCaptions),
                                inserted : s.serialize(insertedCaptions),
                                deleted : s.serialize(deletedCaptions) });
}

mirosubs.embedPlayer = function(identifier) {
    // not clear what we need to do here yet
    
};

if (typeof(MiroSubsToEmbed) != 'undefined')
    for (var i = 0; i < MiroSubsToEmbed.length; i++)
        mirosubs.embedPlayer(MiroSubsToEmbed[i]);

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
window["mirosubs"] = mirosubs;
mirosubs["login"] = mirosubs.login;
mirosubs["saveCaptionWork"] = mirosubs.saveCaptionWork;
mirosubs["embedPlayer"] = mirosubs.embedPlayer;
window["xdSendResponse"] = goog.net.CrossDomainRpc.sendResponse;
window["xdRequestID"] = goog.net.CrossDomainRpc.PARAM_ECHO_REQUEST_ID;
window["xdDummyURI"] = goog.net.CrossDomainRpc.PARAM_ECHO_DUMMY_URI;