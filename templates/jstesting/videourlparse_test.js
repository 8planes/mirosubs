{% extends "jstesting/base_test.html" %}

{% block testscript %}

function testYoutubeFormats() {
    // note: this is duplicated in videos/tests.py in python.
    var test_cases = [
        ['http://www.youtube.com/watch#!v=UOtJUmiUZ08&feature=featured&videos=Qf8YDn9mbGs',
         'UOtJUmiUZ08'],
        ['http://www.youtube.com/v/6Z5msRdai-Q',
         '6Z5msRdai-Q'],
        ['http://www.youtube.com/watch?v=HOaRO-S6h64&playnext=1&videos=nPZyUUKpCEA&feature=featured',
         'HOaRO-S6h64'],
        ['http://www.youtube.com/watch?v=HOaRO-S6h64',
         'HOaRO-S6h64']
    ];
    for (i in test_cases) {
        var test_case = test_cases[i];
        var vs = mirosubs.video.VideoSource.videoSourceForURL(test_case[0]);
        assertEquals(test_case[1], vs.getYoutubeVideoID());
    }
}

{% endblock %}