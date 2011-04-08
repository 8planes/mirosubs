function start() {
    var element = document.getElementsByTagName('embed')[0];
    goog.dom.classes.add(element, 'mirosubs-video-decorated');
    var count = 0;
    window.setInterval(
        function() {
            if (!element['playVideo']) {
                count++;
                console.log(element);
            }
        }, 250);
}

if (mirosubs.LoadingDom.getInstance().isDomLoaded()) {
    start();
}
else {
    goog.events.listenOnce(
        mirosubs.LoadingDom.getInstance(),
        mirosubs.LoadingDom.DOMLOAD,
        start);
}
