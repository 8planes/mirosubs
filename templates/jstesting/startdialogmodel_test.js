{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_model = null;

function makeBaseJSON() {
    return {
        'my_languages': ['en', 'fr'],
        'original_language': 'en',
        'video_languages': [
            { 'pk': 1, 'language': 'en', 'dependent': false, 'is_complete': true, 'subtitle_count': 4 },
            { 'pk': 2, 'language': 'fr', 'dependent': false, 'is_complete': false, 'subtitle_count': 5 }
        ]
    };
}

function setUp() {
    mirosubs.languages = {{languages|safe}};
    mirosubs.metadataLanguages = [];
}

function testOriginalLanguageDisplay() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    assertFalse(model.originalLanguageShown());

    var json = makeBaseJSON();
    json['original_language'] = '';
    json['video_languages'] = [];
    var model = new mirosubs.startdialog.Model(json);
    assertTrue(model.originalLanguageShown());
}

function testToLanguages0() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    var languages = model.toLanguages();

    assertEquals('fr', languages[0].LANGUAGE);
    assertEquals('fr', languages[0].VIDEO_LANGUAGE.LANGUAGE);
    assertEquals('en', languages[1].LANGUAGE);
    assertEquals('en', languages[1].VIDEO_LANGUAGE.LANGUAGE);
    assertEquals('fr', model.getSelectedLanguage().LANGUAGE);
}

function testToLanguagesWithUnspoken() {
    var json = makeBaseJSON();
    json['video_languages'].push({
        'language': 'it', 'dependent': false, 'is_complete': true, 
        'subtitle_count': 8
    });
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    var italians = goog.array.filter(
        languages, 
        function(l) { return l.LANGUAGE == 'it'; });
    assertEquals(1, italians.length);
    assertEquals('it', italians[0].VIDEO_LANGUAGE.LANGUAGE);
}

function testToLanguages1() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    var languages = model.toLanguages();
    assertTrue(languages.length > 2)
    assertEquals(1, goog.array.filter(
        languages, function(l) {
            return l.LANGUAGE == 'en'
        }).length);
    assertEquals(1, goog.array.filter(
        languages, function(l) {
            return l.LANGUAGE == 'fr'
        }).length);
    // assert the languages are sorted by language name.
    for (var i = 2; i < languages.length - 1; i++)
        assertTrue(goog.array.defaultCompare(
            languages[i].LANGUAGE_NAME, 
            languages[i+1].LANGUAGE_NAME) <= 0);
}

function testToLanguages2() {
    var json = makeBaseJSON();
    json['original_language'] = '';
    json['video_languages'] = [];
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertTrue(languages[0].LANGUAGE == 'en' || languages[0].LANGUAGE == 'fr');
    assertTrue(languages[0].LANGUAGE != languages[1].LANGUAGE && 
               (languages[1].LANGUAGE == 'en' || languages[1].LANGUAGE == 'fr'));
    assertTrue(languages.length > 2);
}

function testToLanguagesWithUnsubtitledLanguage() {
    var json = makeBaseJSON();
    json['my_languages'].push('de');
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertEquals('de', languages[0].LANGUAGE);
    assertEquals('fr', languages[1].LANGUAGE);
    assertEquals('en', languages[2].LANGUAGE);
}

function testToLanguagesWithDependent0() {
    var json = makeBaseJSON();
    json['my_languages'] = ['it', 'fr'];
    json['video_languages'].push({
        'pk': 3, 'language': 'it', 'dependent': true, 'percent_done': 50, 'standard_pk': 2, 'subtitle_count': 9
    })
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertEquals('it', languages[0].LANGUAGE);
    assertEquals('fr', languages[1].LANGUAGE);
}

function testFromLangugesWithBlank() {
    var json = makeBaseJSON();
    var fr = json['video_languages'][1];
    fr['language'] = '';
    fr['subtitle_count'] = 0;
    var model = new mirosubs.startdialog.Model(json);
    var fromLanguages = model.fromLanguages();

    var containsOriginal = function(tolang) {
        return goog.string.startsWith(tolang.toString(), 'Original');
    };

    assertFalse(goog.array.some(fromLanguages, containsOriginal));

    json = makeBaseJSON();
    fr = json['video_languages'][1];
    fr['language'] = '';
    fr['subtitle_count'] = 8;
    model = new mirosubs.startdialog.Model(json);
    fromLanguages = model.fromLanguages();

    assertTrue(goog.array.some(fromLanguages, containsOriginal));
}

function testFromLanguages0() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    var toLanguages = model.toLanguages();
    var fromLanguages = model.fromLanguages();
    assertEquals(1, fromLanguages.length);
    assertEquals('en', fromLanguages[0].LANGUAGE);
    model.selectLanguage(goog.array.find(
        toLanguages, function(tl) { return tl.LANGUAGE == 'en'; }).KEY);
    fromLanguages = model.fromLanguages();
    // english is also the original video language.
    assertEquals(0, fromLanguages.length);
}

function testFromLanguagesWithZeroPercent() {
    var json = makeBaseJSON();
    json['video_languages'].push(
        {'pk': 3, 'dependent': true, 'percent_done': 90, 
         'language': 'ru', 'standard_pk': 1, 'subtitle_count': 4 });
    var model = new mirosubs.startdialog.Model(json);
    var fromLanguages = model.fromLanguages();
    assertEquals(2, fromLanguages.length);


    json = makeBaseJSON();
    json['video_languages'].push(
        {'pk': 3, 'dependent': true, 'percent_done': 0, 
         'language': 'ru', 'standard_pk': 1, 'subtitle_count': 0 });
    model = new mirosubs.startdialog.Model(json);
    fromLanguages = model.fromLanguages();
    assertEquals(1, fromLanguages.length);
}

function testFromLanguageWithZeroCount() {
    var json = makeBaseJSON();
    json['video_languages'].push(
        {'pk': 3, 'dependent': false, 'is_complete': false, 
         'language': 'ru', 'subtitle_count': 4 });
    var model = new mirosubs.startdialog.Model(json);
    var fromLanguages = model.fromLanguages();
    assertEquals(2, fromLanguages.length);


    json = makeBaseJSON();
    json['video_languages'].push(
        {'pk': 3, 'dependent': false, 'is_complete': false, 
         'language': 'ru', 'subtitle_count': 0 });
    model = new mirosubs.startdialog.Model(json);
    fromLanguages = model.fromLanguages();
    assertEquals(1, fromLanguages.length);
}


function testGeneral0() {
    var json = {
        "my_languages": ["en-us", "en", "en"],
        "original_language": "",
        "video_languages": [{
            'pk': 3, 
            "dependent": false,
            "is_complete": true,
            "language": "",
            'subtitle_count': 0
        }]
    }
    var model = new mirosubs.startdialog.Model(json, null);
    assertTrue(model.originalLanguageShown());
    assertEquals(0, model.fromLanguages().length);
    var toLanguages = model.toLanguages();
    assertEquals("en", toLanguages[0].LANGUAGE);
    console.log(toLanguages);
    assertEquals(mirosubs.languages.length, toLanguages.length);
    for (var i = 0; i < toLanguages.length; i++)
        assertTrue(!toLanguages[i].VIDEO_LANGUAGE);
}

function testLanguageSummaryNullError() {
    var json = {
        'video_languages': [
            {'pk': 3, 'dependent': false, 'is_complete': false, 'language': 'en', 'subtitle_count': 3},
            {'pk': 4, 'dependent': true, 'percent_done': 66, 'language': 'ru', 'standard_pk': 3, 'subtitle_count': 2}
        ],
        'my_languages': ['ru', 'be'],
        'original_language': 'en'
    }
    var model = new mirosubs.startdialog.Model(json, null);
    // the tests passes if the following call does not throw an exception.
    var langs = model.fromLanguages();
}

function testSetOriginalLanguage() {
    var json = {
        'video_languages': [
            {'pk': 5, 'dependent': false, 'is_complete': false, 'language': 'ru', 'subtitle_count': 3}
        ],
        'my_languages': ['ru', 'en'],
        'original_language': ''
    }
    var model = new mirosubs.startdialog.Model(json, null);
    model.selectOriginalLanguage('ru');
    model.selectLanguage('en');
    assertTrue(model.fromLanguages().length > 0);
    model.selectOriginalLanguage('en');
    assertEquals(0, model.fromLanguages().length);
}


{% endblock %}