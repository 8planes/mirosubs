(function() {
    function readCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i = 0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') 
                c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) 
                return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function makeBucketString(time, buckets) {
        for (var i = 0; i < buckets.length; i++) {
            if (time < buckets[i]) {
                if (i == 0)
                    return "0-" + (buckets[0] - 1);
                else
                    return [buckets[i-1], buckets[i] - 1].join('-');
            }
        }
        return buckets[buckets.length - 1] + '+';
    }

    function registerTime(prefix, time, buckets) {
        var bucketString = makeBucketString(time, buckets);
        window._gaq.push(
            ['_trackEvent', prefix, bucketString, 
             window.location.pathname, parseInt(time)]);
    }

    var SERVER_BUCKETS = [100, 2000, 5000, 10000];
    var LOAD_BUCKETS = [100, 1000, 2500, 5000];
    var TOTAL_BUCKETS = [200, 3000, 7500, 15000];

    $(window).load(function() {
        // page should be fully-loaded, including graphics.
        var serverTime = parseFloat(readCookie('response_time'));
        var loadTime = (new Date()).getTime() - window.usStartTime;
        registerTime('serverTime', serverTime, SERVER_BUCKETS);
        registerTime('loadTime', loadTime, LOAD_BUCKETS);
        registerTime('totalTime', serverTime + loadTime, TOTAL_BUCKETS);
    });
})();