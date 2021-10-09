var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
var SpeechGrammarList = SpeechGrammarList || webkitSpeechGrammarList;
var SpeechRecognitionEvent = SpeechRecognitionEvent || webkitSpeechRecognitionEvent;

var colors = [ 'aqua' , 'azure' , 'beige', 'bisque', 'black', 'blue', 'brown', 'chocolate', 'coral', 'crimson', 'cyan', 'fuchsia', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'indigo', 'ivory', 'khaki', 'lavender', 'lime', 'linen', 'magenta', 'maroon', 'moccasin', 'navy', 'olive', 'orange', 'orchid', 'peru', 'pink', 'plum', 'purple', 'red', 'salmon', 'sienna', 'silver', 'snow', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'white', 'yellow'];
var grammar = '#JSGF V1.0; grammar colors; public <color> = ' + colors.join(' | ') + ' ;'


var recognition = new SpeechRecognition();
var speechRecognitionList = new SpeechGrammarList();
speechRecognitionList.addFromString(grammar, 1);
recognition.grammars = speechRecognitionList;
recognition.continuous = false;
recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 1;


var diagnostic= document.querySelector('.output');

hints.innerHTML = 'Tap/click then say a color to change the background color of the app. Try ' + colorHTML + '.';

document.body.onclick = function() {
  recognition.start();
  console.log('Listen.');
}

recognition.onresult = function(event) {
  // The SpeechRecognitionEvent results property returns a SpeechRecognitionResultList object
  // The SpeechRecognitionResultList object contains SpeechRecognitionResult objects.
  // It has a getter so it can be accessed like an array
  // The first [0] returns the SpeechRecognitionResult at the last position.
  // Each SpeechRecognitionResult object contains SpeechRecognitionAlternative objects that contain individual results.
  // These also have getters so they can be accessed like arrays.
  // The second [0] returns the SpeechRecognitionAlternative at position 0.
  // We then return the transcript property of the SpeechRecognitionAlternative object
  var heard = event.results[0][0].transcript;
  var confidence = event.results[0][0].confidence;
  diagnostic.textContent = "Heard: " + heard + "with a confidence" +  confidence
  //diagnostic.innerHTML="Heard: " + output + "with a confidence"

  console.log('Confidence: ' +  confidence;
  console.log('Heard: ' + heard);
}

recognition.onspeechend = function() {
  recognition.stop();
}

recognition.onnomatch = function(event) {
  diagnostic.textContent = "I didn't recognise that.";
}

recognition.onerror = function(event) {
  diagnostic.textContent = 'Error occurred in recognition: ' + event.error;
}


recognition.onaudiostart = function(event) {
  //Fired when the user agent has started to capture audio.
  console.log('SpeechRecognition.onaudiostart');
}

recognition.onaudioend = function(event) {
  //Fired when the user agent has finished capturing audio.
  console.log('SpeechRecognition.onaudioend');
}

recognition.onend = function(event) {
  //Fired when the speech recognition service has disconnected.
  console.log('SpeechRecognition.onend');
}

recognition.onsoundstart = function(event) {
  //Fired when any sound — recognisable speech or not — has been detected.
  console.log('SpeechRecognition.onsoundstart');
}

recognition.onsoundend = function(event) {
  //Fired when any sound — recognisable speech or not — has stopped being detected.
  console.log('SpeechRecognition.onsoundend');
}

recognition.onspeechstart = function (event) {
  //Fired when sound that is recognised by the speech recognition service as speech has been detected.
  console.log('SpeechRecognition.onspeechstart');
}
recognition.onstart = function(event) {
  //Fired when the speech recognition service has begun listening to incoming audio with intent to recognize grammars associated with the current SpeechRecognition.
  console.log('SpeechRecognition.onstart');
}
}







//testBtn.addEventListener('click', testSpeech);
