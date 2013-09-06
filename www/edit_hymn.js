// Setup the popup window for new input
var popup = new PopupWindow("popup_div");
popup.offsetY = 20;
var pop_hnum = ""
var pop_stanza = ""
var pop_line = ""


// Find the index of the entry to insert before in the data strorage object.
// Given a new node at the specified stanza and line, where should it be inserted?
function findInsertBeforeIndex(stanza, line, id) {
  sortOrder = getSortOrder(stanza, line, id);
  for (var i=0; i<data.length; i++) {
    thisSortOrder = getSortOrder( data[i][2], data[i][3], data[i][0]);
    if (thisSortOrder > sortOrder) {
      return i;
    }
  } // for
  return "-1";
}

function delVerse(hymn_verse_id) {
  // Delete the verse text
  verseNode = document.getElementById("hymn_verse_"+hymn_verse_id);
  verseNode.parentNode.removeChild(verseNode);
  
  // Delete the reference 
  hymnRefNode = document.getElementById("hymn_ref_"+hymn_verse_id);
  hymnRefNode.parentNode.removeChild(hymnRefNode);
  
  // Delete the entry from the data structure
  var newData = new Array();
  for (var i=0; i<data.length; i++) {
    if (data[i][0] != hymn_verse_id) {
      newData.push(data[i]);
    }
  } // for
  data = newData;
}

function delHymnVerse(hymn_verse_id, ref) {
  url = "del_hymn_ajax.py?hymn_verse_id="+hymn_verse_id;
  jx.load(url,function(data){
    if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      delVerse(hymn_verse_id);
    }
  },'json','post');
}

// Updates the display for a verse 
function editVerse(hymn_verse_id, refHtml, verseHtml) {
  verseNode = document.getElementById("hymn_verse_"+hymn_verse_id);
  verseNode.innerHTML = "<a href='javascript:editHymnVerse(\""+hymn_verse_id+"\")' id='edit_"+hymn_verse_id+"' name='edit_"+hymn_verse_id+"'><b>Edit</b></a> " + verseHtml;
  verseNode.innerHTML += "<div style='height:5px'></div>";
  
  hymnRefNode = document.getElementById("hymn_ref_"+hymn_verse_id);
  hymnRefNode.innerHTML = " "+refHtml;
}


function addVerse(hymn_verse_id, hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, comment, refHtml, verseHtml) {
  // Check for valid values 
  if ((hymn_verse_id==null) || (hnum==null) || (stanza==null) || (line==null) || (ref==null) || (refHtml==null) || (verseHtml== null)) {
    return;
  }
   
  // Find where the new node should be inserted
  insertIndex = findInsertBeforeIndex(stanza, line, hymn_verse_id);
  insertBeforeHymnVerseId = "";
  if (insertIndex != "-1") {
    insertBeforeHymnVerseId = data[insertIndex][0];
  } 

  // Create the new node
  newDiv = document.createElement("div");
  newDiv.id = "hymn_verse_"+hymn_verse_id;
  newDiv.innerHTML = "<a href='javascript:editHymnVerse(\""+hymn_verse_id+"\")' id='edit_"+hymn_verse_id+"' name='edit_"+hymn_verse_id+"'><b>Edit</b></a> ";
  newDiv.innerHTML += verseHtml;
  newDiv.innerHTML += "<div style='height:5px'></div>";
  
  // No Node found to insert before (probably an empty verse list), add it to the end
  if (insertBeforeHymnVerseId == "") {
    var verseList = document.getElementById("verselist");
    verseList.appendChild(newDiv);
  } else {
     // Insert the node at the proper position in the verse list
     var insertBeforeNode = document.getElementById("hymn_verse_"+insertBeforeHymnVerseId);
     if (insertBeforeNode == null) alert("node hymn_verse_"+insertBeforeHymnVerseId+" not found!")
     insertBeforeNode.parentNode.insertBefore(newDiv, insertBeforeNode);
  }
  
  var stanzaRefs = document.getElementById("stanza_"+stanza+"_"+line);
  if (stanzaRefs == null) { alert("Could not find element named stanza_"+stanza+"_"+line); }
  var newRef = document.createElement("span");
  newRef.id = "hymn_ref_"+hymn_verse_id;
  var spanStyle = "font-weight:bold; font-size:80%; white-space:nowrap";
  newRef.setAttribute("style", spanStyle );
  newRef.style.cssText = spanStyle;
  newRef.innerHTML = " "+ref;
  stanzaRefs.appendChild(newRef);
  
  // Update the data object and add the new hymn_verse entry
  hymnVerse = [hymn_verse_id, hnum, stanza, line, ref, fn, par, key, min_ref, min_quote, comment];
  data.push(hymnVerse);
  data.sort(dataComparator);
  
}

// Returns a row with all the hymnVerse data in it (from the data storage object)
function getData(hymn_verse_id) {
  if ((hymn_verse_id == "") || (hymn_verse_id == null)) return null;
  // Go through the data looking for a match
  for (var i=0; i<data.length; i++) {
    if (data[i][0] == hymn_verse_id) {
      return data[i];
    }
  }
  return null;
}

function setData(hymn_verse_id, dataRow) {
  if ((hymn_verse_id == "") || (hymn_verse_id == null) || (dataRow == null)) return null;
  // Go through the data looking for a match
  for (var i=0; i<data.length; i++) {
    if (data[i][0] == hymn_verse_id) {
      data[i] = dataRow;
      return null; // short-circuit
    }
  }
}


// Sets all the inputs in the pop-up form according to the hymn_verse id specified
// If hymn_verse_id is "" or null, it will clear all the fields
function setFormData(hymn_verse_id) {
  // Get the popup form fields
  ref = document.getElementById('ref');  
  fn =  document.getElementById('fn'); 
  par =  document.getElementById('par'); 
  key =  document.getElementById('key'); 
  min_ref =  document.getElementById('min_ref'); 
  min_quote =  document.getElementById('min_quote'); 
  comment =  document.getElementById('comment'); 
  
  if ((hymn_verse_id == null) || (hymn_verse_id == "")) {
    // Clear the fields 
    ref.value = "";
    fn.value = "";
    par.value = "";
    key.value = "";
    min_ref.value = "";
    min_quote.value = "";
    comment.value = "";
  } else {
    hymnVerseData = getData(hymn_verse_id);
    if (hymnVerseData != null) {
      pop_hymn_verse_id = hymnVerseData[0];
      pop_hnum = hymnVerseData[1];
      pop_stanza = hymnVerseData[2];
      pop_line = hymnVerseData[3];
      ref.value = hymnVerseData[4];
      fn.value = hymnVerseData[5];
      par.value = hymnVerseData[6];
      key.value = hymnVerseData[7];
      min_ref.value = hymnVerseData[8];
      min_quote.value = hymnVerseData[9];
      comment.value = hymnVerseData[10];
    } else {
      alert("Error!  Could not find an entry for hymn_verse_id = "+hymn_verse_id);
    }
  }
}

function showButton(mode) {
  addButton = document.getElementById("add_button");
  editButton = document.getElementById("edit_button");
  if (mode == "add") {
    addButton.style.display = "inline";
    editButton.style.display = "none";
  } else if (mode == "edit") {
    addButton.style.display = "none";
    editButton.style.display = "inline";
  }
}

function editHymnVerse(hymn_verse_id) {
  setFormData(hymn_verse_id);
  showButton('edit');
  anchor_id = "edit_"+hymn_verse_id;
  showPopup(anchor_id);
}

function addHymnVerse(hnum, stanza, line) {
  setFormData('');
  showButton('add');
  
  // Set the data needed to determine where the click was
  pop_hymn_verse_id = ""; // Blank will add a new one
  pop_hnum = hnum;
  pop_stanza = stanza;
  pop_line = line;
  
  // Show the popup
  anchor_id = "add_"+hnum+"_"+stanza+"_"+line;
  showPopup(anchor_id);
}


function showPopup(anchor_id) {
  // show the popup
  popup.showPopup(anchor_id);
  // focus on the reference field in the popup
  ref = document.getElementById('ref');  
  if (ref) ref.focus();
}

// This will determine if we should do an "edit" or an "add" mode display
function submitPopupGeneric() {
  if (pop_hymn_verse_id != "") {
    mode = "edit";
  } else {
    mode = "add";
  }
  submitPopup(mode);
}

function submitPopup(mode) {
  if (mode == 'cancel') {
    popup.hidePopup();
    return;
  }
  
  if (mode == 'delete') {
    if (!confirm("Are you sure you want to delete this verse?")) return;
    delHymnVerse(pop_hymn_verse_id);
    popup.hidePopup();
    return;
  }
  
  // The mode is "edit" or "add" do the submit
  
  // Get the data from the popup form
  ref = document.getElementById('ref').value;
  fn =  document.getElementById('fn').value; 
  par =  document.getElementById('par').value; 
  key =  document.getElementById('key').value; 
  min_ref =  document.getElementById('min_ref').value; 
  min_quote =  document.getElementById('min_quote').value; 
  comment =  document.getElementById('comment').value; 
  url = "edit_hymn_ajax.py?hymn_verse_id="+pop_hymn_verse_id+"&hnum="+pop_hnum+"&stanza="+pop_stanza+"&line="+pop_line+
    "&ref="+escape(ref)+"&fn="+escape(fn)+"&par="+escape(par)+"&key="+escape(key)+
    "&min_ref="+escape(min_ref)+"&min_quote="+escape(min_quote)+"&comment="+escape(comment);
  
  // Do the Ajax submit
  jx.load(url,function(data){
    if (data.foundError == null) {
      alert("System error updating data, please check the logs, your data may not have been saved.");
    } else if (data.foundError) {
      alert("Error! "+data.errMsg);
    } else {
      if (mode == 'add') {
        addVerse(data.hymn_verse_id, data.hnum, data.stanza, data.line, data.ref, data.fn, data.par, data.key, data.min_ref, data.min_quote, comment, data.refHtml, data.verseHtml);
      } else if (mode == 'edit') {
        // update the page, set the new verse information
        editVerse(data.hymn_verse_id, data.refHtml, data.verseHtml);
        // Set the data storage values to the values (so they load properly next time)
        setData(data.hymn_verse_id, [data.hymn_verse_id, data.hnum, data.stanza, data.line, data.ref, data.fn, data.par, data.key, data.min_ref, data.min_quote, data.comment] );
      }
      popup.hidePopup();
    }
  },'json','post');
  
} // function submitPopup

// Calculates a number that can be used as a sort order
function getSortOrder(stanza, line, id) {  
  stanzaOrder = 0;
  lineOrder = 0;
  idOrder = 0;
  
  if (stanza == "") stanzaOrder = 0;
  else if (stanza == "1") stanzaOrder = 1;
  else if (stanza == "s") stanzaOrder = 1;
  else if (stanza == "c") stanzaOrder = 2;
  else  stanzaOrder = (parseInt(stanza)+1);
  
  if (line == "") lineOrder = 0;
  else lineOrder = parseInt(line);
  
  if (id != "") idOrder = parseInt(id);
  
  // Seperate the order by orders of magnitude, this assumes there won't be more than 100 lines/stanza  and that id won't go over 99999
  return (stanzaOrder * 10000000) + (lineOrder * 100000) + idOrder;
}

// Compares entries in the data object (used for sorting)
function dataComparator(a, b) {
  return (getSortOrder(a[2],a[3],a[0]) - getSortOrder(b[2],b[3],b[0]));
}
