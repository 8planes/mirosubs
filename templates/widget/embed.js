{% load escapejs %}
(function() {
    document.write('{% escapejs %}{% include "widget/widget.html" %}{% endescapejs %}');

    var identifier = { uuid: '{{uuid}}', 
                       video_id: '{{video_id}}', 
                       username: '{{username|escapejs}}' };

    if (typeof(MiroSubs) != 'undefined')
        MiroSubs.embed_player(identifier);
    else {
        if (!window.MiroSubsLoading) {
            window.MiroSubsLoading = true;
            var mirosubs_script = document.createElement('script');
            mirosubs_script.type = 'text/javascript';
            mirosubs_script.src = 'http://localhost:8000/mirosubs_widget.js';
            mirosubs_script.charset = 'UTF-8';
            document.getElementsByTagName('head')[0].appendChild(mirosubs_script);
        }
        if (typeof(MiroSubsToEmbed) == 'undefined')
            window.MiroSubsToEmbed = [];
        window.MiroSubsToEmbed.push(identifier);
    }
})();