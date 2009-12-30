{% load escapejs %}
(function() {
    document.write('{% escapejs %}{% include "widget/widget.html" %}{% endescapejs %}');

    var scripts = [
    {% for dep in js_dependencies %}
      '{{dep|safe}}'{% if not forloop.last %},{% endif %}
    {% endfor %}];

    var identifier = 
        { 
            uuid: '{{uuid}}', 
            video_id: '{{video_id}}', 
            username: '{{username|escapejs}}',
            save_captions_url: 'http://{{site.domain}}/widget/save_captions/'
        };

    if (typeof(mirosubs) != 'undefined' && typeof(mirosubs.CaptionWidget) != 'undefined')
        mirosubs.CaptionWidget.wrap(identifier);
    else {
        if (!window.MiroSubsLoading) {
            window.MiroSubsLoading = true;
            for (var i = 0; i < scripts.length; i++) {
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = scripts[i];
                script.charset = 'UTF-8';
                document.getElementsByTagName('head')[0].appendChild(script);
            }
        }
        if (typeof(MiroSubsToEmbed) == 'undefined')
            window.MiroSubsToEmbed = [];
        window.MiroSubsToEmbed.push(identifier);
    }
})();