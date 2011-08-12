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

function testYTIFrameFormat() {
    var test_cases = [
        ['http://www.youtube.com/embed/V0youqZ2JwI?enablejsapi=1&wmode=opaque&origin=http://mirosubs.example.com:8000', 
         'V0youqZ2JwI']]
    for (i in test_cases) {
        var test_case = test_cases[i];
        var vs = mirosubs.video.YTIFrameVideoSource.forURL(test_case[0]);
        assertEquals(test_case[1], vs.getYoutubeVideoID());
    }
}

function testBlipFlv() {
    var vs = mirosubs.video.VideoSource.videoSourceForURL(
        'http://blip.tv/file/get/Coldguy-SpineBreakersLiveAWizardOfEarthsea210.FLV');
    assertTrue(vs instanceof mirosubs.video.FlvVideoSource);
}

function assertForHtml5Video_(startURL, endURL, videoType) {
    var vs = mirosubs.video.VideoSource.videoSourceForURL(startURL);
    assertTrue(vs instanceof mirosubs.video.Html5VideoSource);
    assertEquals(endURL, vs.getVideoURL());
    assertEquals(videoType, vs.getVideoType());
}

function testOgg() {
    assertForHtml5Video_(
        'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
        'http://videos.mozilla.org/firefox/3.5/switch/switch.ogv',
        mirosubs.video.Html5VideoType.OGG);
}

function testBlipOggFormat() {
    assertForHtml5Video_(
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv',
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv',
        mirosubs.video.Html5VideoType.OGG);
}

function testBlipOggWithQueryString() {
    assertForHtml5Video_(
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv?bri=1.4&brs=1317',
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.ogv',
        mirosubs.video.Html5VideoType.OGG);
}

function testMP4() {
    assertForHtml5Video_(
        'http://videos.mozilla.org/firefox/3.5/switch/switch.mp4',
        'http://videos.mozilla.org/firefox/3.5/switch/switch.mp4',
        mirosubs.video.Html5VideoType.H264);
    assertForHtml5Video_(
        'http://blip.tv/file/get/Judocan-GS_MOSCOW_2010_78KG_UILENHOED_Carola_NED_PUGLIA_Aline_BRA730.MP4',
        'http://blip.tv/file/get/Judocan-GS_MOSCOW_2010_78KG_UILENHOED_Carola_NED_PUGLIA_Aline_BRA730.MP4',
        mirosubs.video.Html5VideoType.H264);
}

function testBlipMP4WithFileGet() {
    assertForHtml5Video_(
        'http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles847.mp4',
        'http://blip.tv/file/get/Miropcf-AboutUniversalSubtitles847.mp4',
        mirosubs.video.Html5VideoType.H264);
}

function testBlipMP4WithQueryString() {
    assertForHtml5Video_(
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.mp4?bri=1.4&brs=1317',
        'http://a59.video2.blip.tv/8410006747301/Miropcf-AboutUniversalSubtitles847.mp4',
        mirosubs.video.Html5VideoType.H264);
}

function testBrightcoveVideoSource(){
        var test_cases = [
        [ 'http://link.brightcove.com/services/player/bcpid955357260001?bckey=AQ~~,AAAA3ijeRPk~,jc2SmUL6QMyqTwfTFhUbWr3dg6Oi980j&bctid=956115197001',
          '955357260001', 'AQ~~,AAAA3ijeRPk~,jc2SmUL6QMyqTwfTFhUbWr3dg6Oi980j&domain']];
    for (i in test_cases) {
        var test_case = test_cases[i];
        var vs = mirosubs.video.VideoSource.videoSourceForURL(test_case[0]);
        assertEquals(test_case[1], vs.getPlayerID());

    }
}
{% endblock %}
