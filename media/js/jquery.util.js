jQuery.isObject = function(v){
    return !!v && Object.prototype.toString.call(v) === '[object Object]';
};

jQuery.isNumber = function(v){
    return typeof v === 'number' && isFinite(v);
};


jQuery.isEmpty = function(v, allowBlank){
    return v === null || v === undefined || ((jQuery.isArray(v) && !v.length)) || (!allowBlank ? v === '' : false);
};

jQuery.isDefined = function(v){
    return typeof v !== 'undefined';
};

jQuery.namespace = function(){
    var o, d;
    jQuery.each(arguments, function(i, v){
        d = v.split(".");
        o = window[d[0]] = window[d[0]] || {};
        jQuery.each(d.slice(1), function(i, v2){
            o = o[v2] = o[v2] || {};
        });
    });
    return o;
};

jQuery.ns = jQuery.namespace;

jQuery.JSON = {
    useHasOwn: ({}.hasOwnProperty ? true : false),
    pad: function(n){
        return n < 10 ? "0" + n : n;
    },
    m: {
        "\b": '\\b',
        "\t": '\\t',
        "\n": '\\n',
        "\f": '\\f',
        "\r": '\\r',
        '"': '\\"',
        "\\": '\\\\'
    },
    encodeString: function(s){
        if (/["\\\x00-\x1f]/.test(s)) {
            return '"' +
            s.replace(/([\x00-\x1f\\"])/g, function(a, b){
                var c = m[b];
                if (c) {
                    return c;
                }
                c = b.charCodeAt();
                return "\\u00" +
                Math.floor(c / 16).toString(16) +
                (c % 16).toString(16);
            }) +
            '"';
        }
        return '"' + s + '"';
    },
    encodeArray: function(o){
        var a = ["["], b, i, l = o.length, v;
        for (i = 0; i < l; i += 1) {
            v = o[i];
            switch (typeof v) {
                case "undefined":
                case "function":
                case "unknown":
                    break;
                default:
                    if (b) {
                        a.push(',');
                    }
                    a.push(v === null ? "null" : this.encode(v));
                    b = true;
            }
        }
        a.push("]");
        return a.join("");
    },
    encodeDate: function(o){
        return '"' + o.getFullYear() + "-" +
        pad(o.getMonth() + 1) +
        "-" +
        pad(o.getDate()) +
        "T" +
        pad(o.getHours()) +
        ":" +
        pad(o.getMinutes()) +
        ":" +
        pad(o.getSeconds()) +
        '"';
    },
    encode: function(o){
        if (typeof o == "undefined" || o === null) {
            return "null";
        }
        else 
            if (o instanceof Array) {
                return this.encodeArray(o);
            }
            else 
                if (o instanceof Date) {
                    return this.encodeDate(o);
                }
                else 
                    if (typeof o == "string") {
                        return this.encodeString(o);
                    }
                    else 
                        if (typeof o == "number") {
                            return isFinite(o) ? String(o) : "null";
                        }
                        else 
                            if (typeof o == "boolean") {
                                return String(o);
                            }
                            else {
                                var self = this;
                                var a = ["{"], b, i, v;
                                for (i in o) {
                                    if (!this.useHasOwn || o.hasOwnProperty(i)) {
                                        v = o[i];
                                        switch (typeof v) {
                                            case "undefined":
                                            case "function":
                                            case "unknown":
                                                break;
                                            default:
                                                if (b) {
                                                    a.push(',');
                                                }
                                                a.push(self.encode(i), ":", v === null ? "null" : self.encode(v));
                                                b = true;
                                        }
                                    }
                                }
                                a.push("}");
                                return a.join("");
                            }
    },
    decode: function(json){
        return eval("(" + json + ')');
    }
};

jQuery.override = function(origclass, overrides){
    if(overrides){
        var p = origclass.prototype;
        jQuery.extend(p, overrides);
        if(jQuery.browser.msie && overrides.hasOwnProperty('toString')){
            p.toString = overrides.toString;
        }
    }
};

Function.prototype.createDelegate = function(obj, args, appendArgs){
    var method = this;
    return function() {
        var callArgs = args || arguments;
        if (appendArgs === true){
            callArgs = Array.prototype.slice.call(arguments, 0);
            callArgs = callArgs.concat(args);
        }else if ($.isNumber(appendArgs)){
            callArgs = Array.prototype.slice.call(arguments, 0); // copy arguments first
            var applyArgs = [appendArgs, 0].concat(args); // create method call params
            Array.prototype.splice.apply(callArgs, applyArgs); // splice them in
        }
        return method.apply(obj || window, callArgs);
    };
};

jQuery.inherit = function(){
    // Copy of Ext.extend from Ext-Core
    var io = function(o){
        for (var m in o) {
            this[m] = o[m];
        }
    };
    var oc = Object.prototype.constructor;
    
    return function(sb, sp, overrides){
        if (jQuery.isObject(sp)) {
            overrides = sp;
            sp = sb;
            sb = overrides.constructor != oc ? overrides.constructor : function(){
                sp.apply(this, arguments);
            };
        }
        var F = function(){
        }, sbp, spp = sp.prototype;
        
        F.prototype = spp;
        sbp = sb.prototype = new F();
        sbp.constructor = sb;
        sb.superclass = spp;
        if (spp.constructor == oc) {
            spp.constructor = sp;
        }
        sb.override = function(o){
            jQuery.override(sb, o);
        };
        sbp.superclass = sbp.supr = (function(){
            return spp;
        });
        sbp.override = io;
        jQuery.override(sb, overrides);

        sb.inherit = function(o){
            return jQuery.inherit(sb, o);
        };
        return sb;
    };
}();

jQuery.util = jQuery.util || {};

jQuery.util.Event = function(obj, name){
    this.name = name;
    this.obj = obj;
    this.listeners = [];
};

jQuery.util.Event.prototype = {
    addListener: function(fn, scope, options){
        var me = this, l;
        scope = scope || me.obj;
        if (!me.isListening(fn, scope)) {
            l = me.createListener(fn, scope, options);
            if (me.firing) { // if we are currently firing this event, don't disturb the listener loop
                me.listeners = me.listeners.slice(0);
            }
            me.listeners.push(l);
        }
    },
    
    createListener: function(fn, scope, o){
        o = o || {}, scope = scope || this.obj;
        var l = {
            fn: fn,
            scope: scope,
            options: o
        }, h = fn;
        l.fireFn = h;
        return l;
    },
    
    isListening: function(fn, scope){
        return this.findListener(fn, scope) != -1;
    },
    
    findListener: function(fn, scope){
        var list = this.listeners, i = list.length, l;
        
        scope = scope || this.obj;
        while (i--) {
            l = list[i];
            if (l) {
                if (l.fn == fn && l.scope == scope) {
                    return i;
                }
            }
        }
        return -1;
    },
    
    removeListener: function(fn, scope){
        var index, l, k, me = this, ret = false;
        if ((index = me.findListener(fn, scope)) != -1) {
            if (me.firing) {
                me.listeners = me.listeners.slice(0);
            }
            l = me.listeners[index];
            if (l.task) {
                l.task.cancel();
                delete l.task;
            }
            k = l.tasks && l.tasks.length;
            if (k) {
                while (k--) {
                    l.tasks[k].cancel();
                }
                delete l.tasks;
            }
            me.listeners.splice(index, 1);
            ret = true;
        }
        return ret;
    },
    
    // Iterate to stop any buffered/delayed events
    clearListeners: function(){
        var me = this, l = me.listeners, i = l.length;
        while (i--) {
            me.removeListener(l[i].fn, l[i].scope);
        }
    },
    
    fire: function(){
        var me = this, args = jQuery.makeArray(arguments), listeners = me.listeners, len = listeners.length, i = 0, l;
        
        if (len > 0) {
            me.firing = true;
            for (; i < len; i++) {
                l = listeners[i];
                if (l && l.fireFn.apply(l.scope || me.obj || window, args) === false) {
                    return (me.firing = false);
                }
            }
        }
        me.firing = false;
        return true;
    }
};

jQuery.util.Observable = function(){

    var me = this, e = me.events;
    if (me.listeners) {
        me.on(me.listeners);
        delete me.listeners;
    }
    me.events = e || {};
};

jQuery.util.Observable.prototype = {
    // private
    filterOptRe: /^(?:scope|delay|buffer|single)$/,
    
    fireEvent: function(){
        var a = jQuery.makeArray(arguments), ename = a[0].toLowerCase(), me = this, ret = true, ce = me.events[ename], q, c;
        if (me.eventsSuspended === true) {
            if (q = me.eventQueue) {
                q.push(a);
            }
        }
        else 
            if (jQuery.isObject(ce) && ce.bubble) {
                if (ce.fire.apply(ce, a.slice(1)) === false) {
                    return false;
                }
                c = me.getBubbleTarget && me.getBubbleTarget();
                if (c && c.enableBubble) {
                    if (!c.events[ename] || !jQuery.isObject(c.events[ename]) || !c.events[ename].bubble) {
                        c.enableBubble(ename);
                    }
                    return c.fireEvent.apply(c, a);
                }
            }
            else {
                if (jQuery.isObject(ce)) {
                    a.shift();
                    ret = ce.fire.apply(ce, a);
                }
            }
        return ret;
    },
    
    addListener: function(eventName, fn, scope, o){
        var me = this, e, oe, isF, ce;
        if (jQuery.isObject(eventName)) {
            o = eventName;
            for (e in o) {
                oe = o[e];
                if (!me.filterOptRe.test(e)) {
                    me.addListener(e, oe.fn || oe, oe.scope || o.scope, oe.fn ? oe : o);
                }
            }
        }
        else {
            eventName = eventName.toLowerCase();
            ce = me.events[eventName] || true;
            if (typeof ce === 'boolean') {
                me.events[eventName] = ce = new jQuery.util.Event(me, eventName);
            }
            ce.addListener(fn, scope, jQuery.isObject(o) ? o : {});
        }
    },
    
    removeListener: function(eventName, fn, scope){
        var ce = this.events[eventName.toLowerCase()];
        if (jQuery.isObject(ce)) {
            ce.removeListener(fn, scope);
        }
    },
    
    purgeListeners: function(){
        var events = this.events, evt, key;
        for (key in events) {
            evt = events[key];
            if (jQuery.isObject(evt)) {
                evt.clearListeners();
            }
        }
    },
    
    addEvents: function(o){
        var me = this;
        me.events = me.events || {};
        if (typeof o === 'string') {
            var a = arguments, i = a.length;
            while (i--) {
                me.events[a[i]] = me.events[a[i]] || true;
            }
        }
        else {
            Ext.applyIf(me.events, o);
        }
    },
    
    hasListener: function(eventName){
        var e = this.events[eventName.toLowerCase()];
        return jQuery.isObject(e) && e.listeners.length > 0;
    }
};

jQuery.util.Observable.prototype.on = jQuery.util.Observable.prototype.addListener;
jQuery.util.Observable.prototype.un = jQuery.util.Observable.prototype.removeListener;

//jQuery.util.DelayedTask
jQuery.util.DelayedTask = function(fn, scope, args){
    var me = this,
        id,     
        call = function(){
            clearInterval(id);
            id = null;
            fn.apply(scope, args || []);
        };
        
    me.delay = function(delay, newFn, newScope, newArgs){
        me.cancel();
        fn = newFn || fn;
        scope = newScope || scope;
        args = newArgs || args;
        id = setInterval(call, delay);
    };

    me.cancel = function(){
        if(id){
            clearInterval(id);
            id = null;
        }
    };
};