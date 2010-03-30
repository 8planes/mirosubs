{ 
    uuid: '{{uuid}}', 
    video_id: '{{video_id}}', 
    youtube_videoid: '{{youtube_videoid}}',
    show_tab: {{show_tab}},
    username: '{{request.user.username|escapejs}}',
    base_url: 'http://{{site.domain}}',
    null_widget: {{null_widget}},
    debug_js: {{debug_js}},
    writelock_expiration: {{writelock_expiration}},
    translation_languages: {{translation_languages|safe}}
{% if autoplay_params %}
    , autoplay_params: {{autoplay_params|safe}}
{% endif %}
}