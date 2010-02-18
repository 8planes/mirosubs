goog.provide('mirosubs.subtitle.Util');

mirosubs.subtitle.Util.createHelpLi = function($d, helpLines, showSpaceBar, firstKeyText) {
    return $d('li', {'className': 'mirosubs-transcribeHelp'},
              $d('div', {'className':'mirosubs-helpInner'}, 
                 $d('p', {'className':'mirosubs-topP'}, helpLines[0]),
                 $d('p', null, helpLines[1]),
                 $d('div', {'className':'mirosubs-keys'}, 
                    $d('span', 
                       showSpaceBar ? {'className':'mirosubs-space_bar'} : null, 
                       firstKeyText),
                    $d('span', {'className':'mirosubs-tab'}, 'Play/Pause'),
                    $d('span', {'className':'mirosubs-back'}, 'Skip Back')
                    )
                 )
              );
};