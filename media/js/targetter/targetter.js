PcfTargetter = (function(){
    var ua = navigator.userAgent.toLowerCase(),
        check = function(r){
            return r.test(ua);
        },
        isOpera = check(/opera/),
        isChrome = check(/\bchrome\b/),
        isWebKit = check(/webkit/),
        isSafari = !isChrome && check(/safari/),
        isSafari2 = isSafari && check(/applewebkit\/4/), // unique to Safari 2
        isSafari3 = isSafari && check(/version\/3/),
        isSafari4 = isSafari && check(/version\/4/),
        isIE = !isOpera && check(/msie/),
        isIE7 = isIE && (check(/msie 7/) || docMode == 7),
        isIE8 = isIE && (check(/msie 8/) && docMode != 7),
        isIE6 = isIE && !isIE7 && !isIE8,
        isGecko = !isWebKit && check(/gecko/),
        isGecko2 = isGecko && check(/rv:1\.8/),
        isGecko3 = isGecko && check(/rv:1\.9/),
        isWindows = check(/windows|win32/),
        
        isOsMac = check(/macintosh|mac os x/),
        isOsAir = check(/adobeair/),
        isOsLinux = check(/linux/),
        
        isSecure = /^https/i.test(window.location.protocol);
    
    return {
        isOpera: isOpera,
        isChrome: isChrome,
        isWebKit: isWebKit,
        isSafari: isSafari,
        isSafari2: isSafari2, // unique to Safari 2
        isSafari3: isSafari3,
        isSafari4: isSafari4,
        isIE: isIE,
        isIE7: isIE7,
        isIE8: isIE8,
        isIE6: isIE6,
        isGecko: isGecko,
        isGecko2: isGecko2,
        isGecko3: isGecko3,
        
        isOsWindows: isWindows,
        isOsMac: isOsMac,
        isOsAir: isOsAir,
        isOsLinux: isOsLinux,
        
        isSecure: isSecure,
                
        defaults: {
            userAgents: [],
            os: [],
            refferers: [],
            text: '',
            elementID: 'pcf-targetter-message',
            callback: function(){
                if (this.elementID){
                    var el = document.getElementById(this.elementID);
                    el && (el.innerHTML = this.text);
                }
            }
        },
        
        init: function(options){
            options = this.apply({}, options, this.defaults);
            if (this.checkUserAgent(options) && this.checkOs(options) && this.checkRefferer(options)){
                options.callback.call(options)
            }
        },
        checkRefferer: function(options){
            var pattern = /https?:\/\/([^\/]+)\//g;
            var result = pattern.exec(document.referrer)[1];
            var referrers = options.refferers;
            for (var i=0,l=referrers.length; i<l; i++){
                if (referrers[i] === result){
                    return true;
                }
            }
            return !referrers.length;
        },
        checkUserAgent: function(options){
            var userAgents = options.userAgents;
            for (var i=0,l=userAgents.length; i<l; i++){
                var f = this['is'+userAgents[i]];
                this.isFunction(f) && (f = f.call(this, options));
                if (f){
                    return true
                }
            }
            return !userAgents.length //if it is empty, return true
        },
        checkOs: function(options){
            var os = options.os;
            for (var i=0,l=os.length; i<l; i++){
                var f = this['isOs'+os[i]];
                this.isFunction(f) && (f = f.call(this, options));
                if (f){
                    return true
                }                
            }
            return !os.length //if it is empty, return true
        },
        
        apply: function(o, c, defaults){
            //from ExtJs Core
            if(defaults){
                this.apply(o, defaults);
            }
            if(o && c && typeof c == 'object'){
                for(var p in c){
                    o[p] = c[p];
                }
            }
            return o;
        },
        isFunction : function(v){
            return Object.prototype.toString.apply(v) === '[object Function]';
        }
    }
})();
