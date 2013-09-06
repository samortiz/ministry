// Setup the popup window for new input
var popup = new PopupWindow("popup_div");
popup.offsetY = 20;
var pop_hymn_line_id = ""
var pop_chpos = ""
var popped = 0 // Set to 1 when the popup is visible
var quickChord = "X"; // The quickChord that is currently selected


function showPopup(hymn_line_id, chpos) {
  if (popped) {
    // This means the popup window is already showing! 
    // This happens if you click on another position before the submit happens
    if (popped == 1) {
      // Wait a bit and try to show the popup again
      setTimeout("showPopup('"+hnum+"', '"+hymn_line_id+"', '"+chpos+"')",100);
      return;
    }
  }
  // Store the state variables
  pop_hymn_line_id = hymn_line_id;
  pop_chpos = chpos;
  
  // Check for a keypress chord (holding a key down while clicking)
  key_chord = "";
  key_modifier = "";
  for (var k in keyArr) {
    key = k.toUpperCase();
    if ((key == "A") || (key == "B") || (key == "C") || (key == "D") || (key == "E") || (key == "F") || (key == "G")) {
      key_chord = key;
    } else {
      if ((key == "7") || (key == "M")) {
        key_modifier = key;
      }
    }
  } // for
  if (key_chord != "") {
    newChord = key_chord + key_modifier.toLowerCase();
    document.getElementById('chord').value = newChord;
    submitPopup();
    keyArr = new Array();  // Clear all the keys after a key is pressed.
    return; // Do not show the popup - it's quick! 
  }
  
  // Do a quickChord 
  if (quickChord != "X") {
    document.getElementById('chord').value = quickChord;
    submitPopup();
    return; // Do not show the popup - it's quick! 
  }
  
  // show the popup
  popup.showPopup("a_hymn_line_id"+hymn_line_id+"_chpos"+chpos);
  popped = 1;
  // focus on the reference field in the popup
  chord = document.getElementById('chord');  
  if (chord) {
    chord.focus();
    chord.value = "";
  }  
}

// Just a little nothing, the onblur will do the form submit
function doNothing() {
}

// Delete a chord
function delChord(hymn_line_id, chpos)  {
  // Confirm the delete
  /*
  if (!confirm("Are you sure you want to delete this chord?")) {
    return;
  }
  */
  
  url = "edit_chords_ajax.py?hnum="+hnum+"&hymn_line_id="+hymn_line_id+"&chpos="+chpos+"&chord=&mode=del";

  // Do the Ajax submit 
  jx.load(url,function(data){
    if (data.foundError == null) {
      alert("System error updating data, please check the logs, the chord may not have been deleted.");
    } else if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      chordObj = document.getElementById("chord_hymn_line_id"+hymn_line_id+"_chpos"+chpos);
      if (chordObj != null) {
        chordObj.innerHTML = ""; // actually remove the data
      }
    }
  },'json','post');
  
}


function submitPopup() {
  // Get the data from the popup form
  chord = document.getElementById('chord').value;
  url = "edit_chords_ajax.py?hnum="+hnum+"&hymn_line_id="+pop_hymn_line_id+"&chpos="+pop_chpos+"&chord="+chord;
  
  // Do the Ajax submit
  jx.load(url,function(data){
    if (data.foundError == null) {
      alert("System error updating data, please check the logs, your data may not have been saved.");
    } else if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      chordObj = document.getElementById("chord_hymn_line_id"+pop_hymn_line_id+"_chpos"+pop_chpos);
      if (chordObj != null) {
        chordObj.innerHTML = data.chord; 
      } else {
        alert("Error! Could not find object with id=chord_hymn_line_id"+pop_hymn_line_id+"_chpos"+pop_chpos);
      }
      
      // TODO Update the display
      popup.hidePopup();
      popped = 0; // not visible any more
    }
  },'json','post');
  
} // function submitPopup



function setChord(chord) {
  obj = document.getElementById("quickchord_"+chord);
  if (obj != null) {
    // Clear the highlighting from the old object
    oldObj = document.getElementById("quickchord_"+quickChord);
    if (oldObj != null) {
      oldObj.style.background = "white";
      oldObj.style.fontWeight = "normal";
    } //else {alert("no old obj named "+quickChord): }
    
    // Highlight the new object 
    obj.style.background = "#CCCCCC";
    obj.style.fontWeight = "bold";
    
    // Store the current chord
    quickChord = chord;
  } else {
    alert("No quickcord exists by the name : "+chord);
  }
}


// Keypress events 
document.onkeydown = keydown;
document.onkeyup = keyup;
var keyArr = new Array();

function getKey(e) {
  var keynum;
  var keychar;
  if (window.event) { // IE
    keynum = e.keyCode;
  } else if (e.which) { // Netscape/Firefox/Opera
    keynum = e.which;
  }
  return String.fromCharCode(keynum);  
}

// A key is depressed
function keydown(e) {
  key = getKey(e);
  keyArr[key] = 1;
}

// A key is released
function keyup(e) {
  delete keyArr[key];
}


// -------------------  Key and Time popup ------------
var key_popup = new PopupWindow("key_popup_div");
key_popup.offsetY = 20;

function showPopupKey() {
  // show the popup
  key_popup.showPopup("key_anchor");
  // focus on the field in the popup
  key = document.getElementById('key');  
  if (key) {
    key.focus();
  }
}

function submitKey() {
  // Get the data from the popup form
  key = document.getElementById('key').value; 
  url = "edit_keytime_ajax.py?hnum="+hnum+"&key="+key+"&mode=key";
  
  // Do the Ajax submit
  jx.load(url,function(data){
    if (data.foundError == null) {
      alert("System error updating data, please check the logs, your data may not have been saved.");
    } else if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      document.getElementById("key").innerHTML = data.key;
      document.getElementById("key_anchor").innerHTML = data.key;
      key_popup.hidePopup();
    }
    
  },'json','post');
} // function submitKey


var time_popup = new PopupWindow("time_popup_div");
time_popup.offsetY = 20;

function showPopupTime() {
  // show the popup
  time_popup.showPopup("time_anchor");
  // focus on the field in the popup
  time = document.getElementById('time');  
  if (time) {
    time.focus();
  }
}

function submitTime() {
  // Get the data from the popup form
  time = document.getElementById('time').value; 
  url = "edit_keytime_ajax.py?hnum="+hnum+"&time="+escape(time)+"&mode=time";
  
  // Do the Ajax submit
  jx.load(url,function(data){
    if (data.foundError == null) {
      alert("System error updating data, please check the logs, your data may not have been saved.");
    } else if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      document.getElementById("time").innerHTML = data.time;
      document.getElementById("time_anchor").innerHTML = data.time;
      time_popup.hidePopup();
    }
    
  },'json','post');
} // function submitTime
