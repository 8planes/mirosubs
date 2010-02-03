goog.provide('mirosubs.subtitle.Util');

mirosubs.subtitle.Util.createHelpLi = function(domHelper, helpLines) {
    var $d = goog.bind(domHelper.createDom, domHelper);
    var helpLines = goog.array.map(helpLines,
                                   function(line) {
                                       return $d('li', null, line);
                                   });
    return $d('li', {'class':'mirosubs-help'},
              $d('ol', null, helpLines));
};