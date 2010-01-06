var current_line = null;
var input_fields = null;
var MAXCHARS = 100;
var transcript_disabled = false;

function add_line(){
  if (current_line){
    current_line.style.background = "#ffd";
  }

  var line = document.createElement("div");
	line.innerHTML='<input type="text" class="inputline"></input><p>(silence)</p>';
  input_fields.appendChild(line);
  input_fields.appendChild(document.createElement("br"));
  line.firstChild.focus();
	line.setAttribute("silence", "false");

	//hack: when user clicks on (pause) the underlying input field should receive focus!
	line.childNodes[1].onclick = function(e){ e.target.parentNode.firstChild.focus(); }
  return line;
}

function hex(i){
  if (i>15) return 'F';
  if (i<0) return '0';
  return ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'][Math.floor(i)];
}

function color_scale(i){
  var first_chars = 40;
  if (i<first_chars) i=0
  else i-=first_chars;

  r=15;
  g = 16 - 16*i/(MAXCHARS-first_chars);
  b = 12 - 12*i/(MAXCHARS-first_chars);
  return "#" + hex(r) + hex(g) + hex(b);
}

function TranscriptWidgetKeyHandler(e){
  if (current_step !=1) return;
  current_line.firstChild.style.background=color_scale(current_line.firstChild.value.length);
  subtitles_p.innerHTML = check_and_prepare_for_double_line(current_line.firstChild.value);

  if (((current_line.firstChild.value.length > MAXCHARS) /* && e.type == "keypress" */ && e.keyCode == 32) ||
      (e.type == "keydown" && e.keyCode==13)){
    current_line = add_line();
  }

  var line = current_line;
  if (e.type == "keydown" && e.keyCode == 38){//up-arrow
    line = line.previousSibling;
    while (line && line.tagName != "DIV"){
      line = line.previousSibling;
    }

    if (line){
      current_line.style.background = "#ffd";
      current_line = line;
      current_line.firstChild.focus();
    }

  }

  if (e.type == "keydown" && e.keyCode == 40){//down-arrow
    line = line.nextSibling;
    while (line && line.tagName != "DIV"){
      line = line.nextSibling;
    }

    if (line){
      current_line.style.background = "#ffd";
      current_line = line;
      current_line.firstChild.focus();
    }
  }

  if (e.type == "keyup"){
		if (current_line.firstChild.value.length==0)
			current_line.setAttribute("silence", "true");
		else
			current_line.setAttribute("silence", "false");
	}
}

function init_transcript_widget(event){
  input_fields = document.getElementById("inputfields");
  current_line = add_line();

  input_fields.addEventListener("keydown", TranscriptWidgetKeyHandler, true);
  input_fields.addEventListener("keyup", TranscriptWidgetKeyHandler, true);
  input_fields.addEventListener("keypress", TranscriptWidgetKeyHandler, true);
}
