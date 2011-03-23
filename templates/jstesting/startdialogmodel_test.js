{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_model = null;

function makeBaseJSON() {
    return {
        'my_languages': ['en', 'fr'],
        'original_language': 'en',
        'video_languages': [
            { 'language': 'en', 'dependent': false, 'is_complete': true },
            { 'language': 'fr', 'dependent': false, 'is_complete': false }
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
    assertEquals('fr', languages[0].language);
    assertEquals('en', languages[1].language);
    assertEquals('fr', model.getSelectedLanguage());
}

function testToLanguages1() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    var languages = model.toLanguages();
    assertTrue(languages.length > 2)
    assertEquals(1, goog.array.filter(
        languages, function(l) {
            return l.language == 'en'
        }).length);
    assertEquals(1, goog.array.filter(
        languages, function(l) {
            return l.language == 'fr'
        }).length);
    // assert the languages are sorted by language name.
    for (var i = 2; i < languages.length - 1; i++)
        assertTrue(goog.array.defaultCompare(
            languages[i].languageName, languages[i+1].languageName) <= 0);
}

function testToLanguages2() {
    var json = makeBaseJSON();
    json['original_language'] = '';
    json['video_languages'] = [];
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertTrue(languages[0].language == 'en' || languages[0].language == 'fr');
    assertTrue(languages[0].language != languages[1].language && 
               (languages[1].language == 'en' || languages[1].language == 'fr'));
    assertTrue(languages.length > 2);
}

function testToLanguagesWithUnsubtitledLanguage() {
    var json = makeBaseJSON();
    json['my_languages'].push('de');
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertEquals('de', languages[0].language);
    assertEquals('fr', languages[1].language);
    assertEquals('en', languages[2].language);
}

function testToLanguagesWithDependent0() {
    var json = makeBaseJSON();
    json['my_languages'] = ['it', 'fr'];
    json['video_languages'].push({
        'language': 'it', 'dependent': true, 'percent_done': 50, 'standard': 'fr'
    })
    var model = new mirosubs.startdialog.Model(json);
    var languages = model.toLanguages();
    assertEquals('it', languages[0].language);
    assertEquals('fr', languages[1].language);
}

function testFromLanguages0() {
    var model = new mirosubs.startdialog.Model(makeBaseJSON());
    var fromLanguages = model.fromLanguages();
    assertEquals(1, fromLanguages.length);
    assertEquals('en', fromLanguages[0].LANGUAGE);
    model.selectLanguage('en');
    fromLanguages = model.fromLanguages();
    // english is also the original video language.
    assertEquals(0, fromLanguages.length);
}

function testGeneral0() {
    var json = {
        "my_languages": ["en-us", "en", "en"],
        "original_language": "",
        "video_languages": [{
            "dependent": false,
            "is_complete": true,
            "language": ""
        }]
    }
    var model = new mirosubs.startdialog.Model(json, null);
    assertTrue(model.originalLanguageShown());
    assertEquals(0, model.fromLanguages().length);
    var toLanguages = model.toLanguages();
    assertEquals("en", toLanguages[0].language);
    assertEquals(mirosubs.languages.length, toLanguages.length);
    for (var i = 0; i < toLanguages.length; i++)
        assertTrue(!toLanguages[i].videoLanguage);
}

function testLanguageSummaryNullError() {
    var json = {
        'video_languages': [
            {'dependent': false, 'is_complete': false, 'language': 'en'},
            {'dependent': true, 'percent_done': 66, 'language': 'ru', 'standard': 'en'}
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
            {'dependent': false, 'is_complete': false, 'language': 'ru'}
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