//Globar vars:
var SUBTITLES_SERVER = "http://wstr.org/subs/";
var mode = "playback";
var current_subtitle = null;
var current_title_sync;
var subtitles_textbox = [];
var subtitles_time_in = [];
var subtitles_time_out = [];
var autoskipback;
var autoskipback_ammount;
var autoskip_timeout;
var video;
var holding_key=false;
var hold_start;
var subtitles_p;
var current_step=1;
var options = {};

//---------------
function sendGETRequest(url, callback) {
 	var xhr = new XMLHttpRequest();
  var ajaxDataReader = function () {
    if (xhr.readyState == 4) {
      callback(xhr.responseText);
    }
  }

  xhr.open("GET", url, true);

  //https://developer.mozilla.org/En/Using_XMLHttpRequest#Bypassing_the_cache
  xhr.channel.loadFlags |= Components.interfaces.nsIRequest.LOAD_BYPASS_CACHE;

  xhr.onreadystatechange = ajaxDataReader;
  try {
      xhr.send(null);
    }
  catch(e){
//    alert("bad request");
  }
}

function sendPOSTRequest(url, params, callback) {
//alert("url: "+url);
//alert("params: "+params);
 	var xhr = new XMLHttpRequest();
  var ajaxDataReader = function () {
    if (xhr.readyState == 4) {
//alert("xhr.responseText: "+xhr.responseText);
      callback(xhr.responseText);
    }
  }

  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhr.setRequestHeader("Content-length", params.length);
  xhr.setRequestHeader("Connection", 'close');

  xhr.onreadystatechange = ajaxDataReader;
  try {
      xhr.send(params);
    }
  catch(e){
//    alert("bad request");
  }
}

function save_article(articlename, content){
  var token = "+\\"; //this token is used for anonymous edits

//  alert("article: "+articlename+"\n\ncontent:\n\n\""+content+"\"");

  var display_result = function(data){
      //for debugging purpose only:
          //alert("result:\n\n"+data);
  }

  var params = "action=edit&title=" + encodeURIComponent(articlename) + "&section=0&text="+encodeURIComponent(content) + "&token=" + encodeURIComponent(token);

  sendPOSTRequest("../subs/api.php", params, display_result);
}

function load_article(pagename, callback){
  var parse_response = function(text){
    callback(text);
  }
    
  sendGETRequest("../subs/index.php?action=raw&title=" + pagename, parse_response);
}

//---------------


/* SRT (subtitles file format) parsing and encoding routines: */

function toMilliSeconds(s){
  var timeparts = s.split(',');
  msecs = Number(timeparts[1]);
  var timeparts = timeparts[0].split(':');
  var hours = Number(timeparts[0]);
  var mins = Number(timeparts[1]);
  var secs = Number(timeparts[2]);

  return (((hours*60 + mins) * 60) + secs)*1000 + msecs;
}

function MilliSecondsToString(time){
  var hours = Math.floor(time / 3600000);
  var mins  = Math.floor(time % 3600000 / 60000);
  var secs  = Math.floor(time % 60000 / 1000);

  if (secs < 10) secs = "0" + secs;
  if (mins < 10) mins = "0" + mins;
  if (hours < 10) hours = "0" + hours;

  var msecs = time%1000;
  if (msecs < 10) msecs = "0" + msecs;
  if (msecs < 100) msecs = "0" + msecs;
  return hours + ":" + mins + ":" + secs + "," + msecs;
}

function MilliSecondsToString_for_output(time){
  var timeString = "";
  var hours = Math.floor(time / 3600000);
  var mins  = Math.floor(time % 3600000 / 60000);
  var secs  = Math.floor(time % 60000 / 1000);

  if (secs < 10) secs = "0" + secs;
  if (hours>0){
    if(mins < 10) mins = "0" + mins;
    timeString = hours + ":";
  }
  return timeString + mins + ":" + secs;
}

function encode_srt(sub){
  text = ""
  for (i in sub){
      text+=(Number(i)+1)+"\n"
      text+=this.MilliSecondsToString(sub[i]["start"])
      text+=" --> "
      text+=this.MilliSecondsToString(sub[i]["end"])+"\n";
      text+=sub[i]["text"]+"\n\n";
  }
  return text;
}

function load_article(){
//TODO: implement-me!
	return;
}

function step1(){
  current_step=1;

  document.getElementById("step1css").disabled = false;
  document.getElementById("step2css").disabled = true;
  document.getElementById("step3css").disabled = true;

  document.getElementById("step1tab").setAttribute("class", "tab selected");
  document.getElementById("step2tab").setAttribute("class", "tab");
  document.getElementById("step3tab").setAttribute("class", "tab");
}

function step2(){
  var input_fields = document.getElementById("inputfields");
  var transcript = "";
  var node;

  for (var i in input_fields.childNodes){
    node = input_fields.childNodes[i];
		if (node.tagName == "DIV"){
		  if (node.getAttribute("silence") == "true"){
		    transcript += "\n";
		  } else {
		    transcript += node.firstChild.value + "\n"; 
		  }
		}
  }

  if (current_step==1){
    var src = video.currentSrc;
//    if (!src) src = video.getElementsByTagName("source")[0].src;
    save_article("Transcript/URL/"+src, transcript);
  }
  current_step=2;
  document.getElementById("step1css").disabled = true;
  document.getElementById("step2css").disabled = false;
  document.getElementById("step3css").disabled = true;

  document.getElementById("step1tab").setAttribute("class", "tab");
  document.getElementById("step2tab").setAttribute("class", "tab selected");
  document.getElementById("step3tab").setAttribute("class", "tab");

  var titles = transcript.split('\n');
  var subs = [];
  for (i in titles){
    subs.push({"text": titles[i], "start":-1,"end":-1});
  }
  current_subtitle = {"content":subs};
  current_title_sync = 0;

//alert('current_subtitle["content"].length: '+current_subtitle["content"].length);
  //restart playback:
  video.currentTime = 0;
	//displaySubtitles_sync(0);

  video.addEventListener('timeupdate', function(e){
    displaySubtitles_sync(e.target.currentTime*1000);
  }, false);

}

function fake_transcript_mode(){

  current_step=2;
  document.getElementById("step1css").disabled = true;
  document.getElementById("step2css").disabled = false;
  document.getElementById("step3css").disabled = true;

  document.getElementById("step1tab").setAttribute("class", "tab");
  document.getElementById("step2tab").setAttribute("class", "tab selected");
  document.getElementById("step3tab").setAttribute("class", "tab");

	var transcript= "\
hi, I'm Asa Dotzler from Mozilla and I'm here to show you\n\
how simple it is to switch to Firefox\n\
just go to getfirefox.com with your current web browser\n\
and click the green download button on the website\n\
to save the Firefox setup file to your desktop\n\
close the browser window and double-click the Firefox setup icon to start the install \n\
\n\
then follow the simple steps on the screen and Firefox will be installed on your computer\n\
\n\
Firefox can even import your personalized settings from your current webbrowser,\n\
for example your favorites and stored passwords\n\
\n\
finish the installation and you're now searching the web using firefox,\n\
the fast, secure, and customizable web browser from Mozilla.";

  var titles = transcript.split('\n');
  var subs = [];
  for (var i in titles){
    subs.push({"text": titles[i], "start":-1,"end":-1});
  }
  current_subtitle = {"content":subs};
  current_title_sync = 0;

  //restart playback:
//  video.currentTime = 0;
	//displaySubtitles_sync(0);

  video.addEventListener('timeupdate', function(e){
    displaySubtitles_sync(e.target.currentTime*1000);
  }, false);
}

function step3(){
  if (current_step==2){
    var src = video.currentSrc;
//    if (!src) src = video.getElementsByTagName("source")[0].src;
    save_article("Subtitles/URL/"+src, encode_srt(current_subtitle["content"]));
  }
  current_step=3;
  document.getElementById("step1css").disabled = true;
  document.getElementById("step2css").disabled = true;
  document.getElementById("step3css").disabled = false;

  document.getElementById("step1tab").setAttribute("class", "tab");
  document.getElementById("step2tab").setAttribute("class", "tab");
  document.getElementById("step3tab").setAttribute("class", "tab selected");
}

function next_step(){
  switch(current_step){
    case 1:
      step2();
      break;
    case 2:
      step3();
      break;
  }
}

function check_and_prepare_for_double_line(text){
  var parts = text.split(' ');
  var counter = 0;
  var result="";
  var lines=1;
  for (var i in parts){
    if (counter + parts[i].length > 50){
      counter = 0;
      if (lines==3){ result += " [...]"; break; }
      result += "<br/>";
      lines++;
    }
    counter += parts[i].length + 1;
    if (i>0) result += " ";
    result += parts[i];
  }
  return "<p class='subtitles subtitleslines"+lines+"'>"+result+"</p>";
}

function highlight_current_title(i){
	var nodes = document.getElementById("inputfields").childNodes;
	for (var n in nodes){
		if (n%2==0){//div nodes
			$(nodes[n]).removeClass("current_title");
		}
	}

	$(nodes[2*i]).addClass("current_title");
}

//TODO: use the value passed to this function!
function displaySubtitles_sync(current_time){
  if (current_subtitle == null){
    subtitles_textbox[0].innerHTML = "&nbsp;";
    subtitles_textbox[1].innerHTML = "&nbsp;";
    subtitles_textbox[2].innerHTML = "&nbsp;";
    subtitles_textbox[3].innerHTML = "&nbsp;";
    subtitles_textbox[4].innerHTML = "&nbsp;";
    subtitles.innerHTML = "";
    return;
  }

  var subs = current_subtitle["content"];
  var currentTime = Math.round(video.currentTime * 1000);

  if (holding_key) currentTime = hold_start;
  if (subs[0].start>=0 && currentTime < subs[0].start) current_title_sync = 0;

  for (var i=0; i < subs.length; i++){
    if ((subs[i].start != -1) && (currentTime >= subs[i].start) && ((currentTime < subs[i].end) || (subs[i].end==-1))){
      current_title_sync = i+1;
      break;
    }
  }

  function get_title(i){
    if (i>=0 && i<subs.length){
      return subs[i]["text"];
    } else {
      if (i==-3) return "--- Opening Silence ---"
      if (i==-2) return "--- Skip down when people start talking ---";
      if (i==subs.length) return "--- end of transcript ---";
    }
    return "&nbsp;";
  }

  function get_title_or_silence(i){
    var title = get_title(i);
    return (title == "") ? "[silence]" : title;
  }

  function get_time_in(i){
    if (i>=0 && i<subs.length && subs[i].start>0){
      return MilliSecondsToString_for_output(subs[i].start);
    } else {
      return "";
    }
  }

  function get_time_out(i){
    if (i>=0 && i<subs.length && subs[i].end>0){
      return MilliSecondsToString_for_output(subs[i].end);
    } else {
      return "";
    }
  }

  var i = current_title_sync - 1;
  for (index in subtitles_textbox){
    subtitles_textbox[index].innerHTML = get_title_or_silence(index-2 + i);
    subtitles_time_in[index].innerHTML = get_time_in(index-2 + i);
    subtitles_time_out[index].innerHTML = get_time_out(index-2 + i);
  }
  subtitles_p.innerHTML = check_and_prepare_for_double_line(get_title(i));

	try{
		highlight_current_title(i);

		var node = document.getElementById("inputfields").childNodes[2*i].firstChild;
		$("#inputfields").scrollTo($(node), 0, {offset:-100});
	} catch(e){}

}

function setup_autoskip(){
  if (autoskip_timeout)
    clearTimeout(autoskip_timeout);

  autoskip_timeout = setTimeout( auto_skip, autoskipback_interval.value*1000);
}

function auto_skip(){                      
  if (autoskipback.checked && current_step==1){
    var newval = video.currentTime - autoskipback_ammount.value;
    video.currentTime = (newval >= 0 ? newval : 0);
    setup_autoskip();
  } else {
    if (autoskip_timeout)
      clearTimeout(autoskip_timeout);  
  }
}

function autoskip_clicked(event){
  if (autoskipback.checked) setup_autoskip();
}

function reset_titles(start, end){
  if (!current_subtitle) return;

  var subs = current_subtitle["content"];

  for (i=0; i < subs.length; i++){
    if ((subs[i].start > start) && (subs[i].start < end)){
      subs[i].start = -1;
    }

    if ((subs[i].end > start) && (subs[i].end < end)){
      subs[i].end = -1;
    }
  }

  var now = Math.round(video.currentTime * 1000);
  for (i=0; i < subs.length; i++){
    if ((subs[i].start != -1) && (now >= subs[i].start) && ((now < subs[i].end) || (subs[i].end==-1))){
      current_title_sync = i+1;
      break;
    }
  }
}

function HOLD_handle_keydown(event){
  if (!holding_key) hold_start = Math.round(video.currentTime * 1000);

  holding_key=true;
}

function HOLD_handle_keyup(event){
  holding_key=false;
  reset_titles(hold_start, Math.round(video.currentTime * 1000));
}

function load(event){
  video = document.getElementById("video");
  subtitles_p = document.getElementById("subtitles");

  var url_fragments = String(document.location).split("?");

//This is more than what we need, but is good because we
// can eventually pass other useful attributes in the url

  if (url_fragments.length>1){
    var params = url_fragments[1].split("&");
    if (params.length==1){
      var pair = String(params).split("=");
      options[pair[0]] = pair[1];
    } else {
      for (var i in params){ 
        var pair = params[i].split("=");
        options[pair[0]] = pair[1];
      }
    }
  }

  if (!options["videourl"]){
    options["videourl"] = "http://videos.mozilla.org/firefox3/switch/switch.ogg";
  }

  video.src = options["videourl"];
  document.getElementById("transcript_wiki").setAttribute("href", SUBTITLES_SERVER + "/index.php?title=Transcript/URL/"+options["videourl"]);
  document.getElementById("SRT_wiki").setAttribute("href", SUBTITLES_SERVER + "/index.php?title=Subtitles/URL/"+options["videourl"]);

  subtitles_textbox.push(document.getElementById("title_1"));
  subtitles_textbox.push(document.getElementById("title_2"));
  subtitles_textbox.push(document.getElementById("title_3"));
  subtitles_textbox.push(document.getElementById("title_4"));
  subtitles_textbox.push(document.getElementById("title_5"));

  subtitles_time_in.push(document.getElementById("time_in_1"));
  subtitles_time_in.push(document.getElementById("time_in_2"));
  subtitles_time_in.push(document.getElementById("time_in_3"));
  subtitles_time_in.push(document.getElementById("time_in_4"));
  subtitles_time_in.push(document.getElementById("time_in_5"));

  subtitles_time_out.push(document.getElementById("time_out_1"));
  subtitles_time_out.push(document.getElementById("time_out_2"));
  subtitles_time_out.push(document.getElementById("time_out_3"));
  subtitles_time_out.push(document.getElementById("time_out_4"));
  subtitles_time_out.push(document.getElementById("time_out_5"));

  autoskipback = document.getElementById("autoskipback");
  autoskipback_ammount = document.getElementById("autoskipback-ammount");
  autoskipback_interval = document.getElementById("autoskipback-interval");

  autoskipback.addEventListener("click", autoskip_clicked, false);


  var select_key = function(value){
    switch (value){
      case "TAB": return 9;
      case "CTRL": return 17;
      case "[": return 219;
      case "]": return 221;
      case "SPACEBAR": return 32;
      case "|": return 220;
    }
  };

  function KeyUpHandler(event){
    HOLD_handle_keyup(event);

    var tap_key = select_key(document.getElementById("taphotkey").value);

    if (event.which == tap_key){
      event.preventDefault();
      event.stopPropagation();
      if(current_title_sync == null) return;
      var subs = current_subtitle["content"];
      var now = Math.round(video.currentTime * 1000);
      if (current_title_sync>0) subs[current_title_sync-1].end = now;
      if (current_title_sync<subs.length){
        subs[current_title_sync].start = now;
        current_title_sync++;
      }
    }
  }

  function KeyDownHandler(event){
    HOLD_handle_keydown(event);

    var rewind_key = select_key(document.getElementById("rewindhotkey").value);
    var playpause_key = select_key(document.getElementById("playpausehotkey").value);

    if (event.which == rewind_key){
      var newval = video.currentTime - document.getElementById("rewindsecs").value;
      video.currentTime = (newval >= 0 ? newval : 0);
      event.preventDefault();
      event.stopPropagation();
    }

    if (event.which == playpause_key){
      if (video.paused || video.ended){
          self.video.play();
          document.getElementById("playbtn").setAttribute("paused", "false");
      } else {
          video.pause();
          document.getElementById("playbtn").setAttribute("paused", "true");
      }
      event.preventDefault();
      event.stopPropagation();
    }
  }

  window.addEventListener("keydown", KeyDownHandler, true);
  window.addEventListener("keyup", KeyUpHandler, true);

  init_transcript_widget(event);  

	var src = video.currentSrc;
	var article = load_article("Transcript/URL/"+src)
	if (article){
		article = article.split("\n");
		for (i in article){
			current_line.value = article[i];
			current_line = add_line();
		}
	}

	if (options["faketranscript"]=="true"){
		fake_transcript_mode();
	} else {
	  step1();
	}

}
