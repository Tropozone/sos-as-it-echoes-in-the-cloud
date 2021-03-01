
#######'SONOR Interpreter
###To develop

#**********************************************************************PARAMETERS***************************************************************************

step_size=100 #decide the chunk size for the audio
confidence_level=0.8

#**********************************************************************INITIALISATION**************************************************************************

import crepe
from scipy.io import wavfile
from math import log2, pow

A4 = 440
C0 = A4 * pow(2, -4.75)
nameNote = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

#**********************************************************************PRELIMINARIES***************************************************************************

def pitch(freq):
    if freq==0:
        return "VOID"
    else:
        h = round(12*log2(freq/C0))
        octave = h // 12
        n = h % 12
        return nameNote[n] + str(octave)


#**********************************************************************PROCEDURES***************************************************************************


### Need mic to work ####
# to be triggered at the same time when chris is activated
import sounddevice as sd
from scipy.io.wavfile import write

fs = 44100  # Sample rate
seconds = 5  # Duration of recording


def soundToNotes(name_audio):
    sr, audio = wavfile.read(name_audio)
    time, frequency, confidence, activation = crepe.predict(audio, sr, step_size=step_size, viterbi=True)
    nChunks=len(confidence)
    print("Number Chunks", nChunks)
    print("List frequencies:", frequency)
    notes=[]
    for i in range(nChunks):
        note=pitch(frequency[i])
        if confidence[i]>confidence_level and (not (note=="VOID")):
            notes.append(note)
    print("List Notes :", notes)
    nStep=len(notes)
    print("number Step Melody:", nStep)
    return notes


def notesToWords(notes):
    #For now only test if contain a certain sequence of notes (because of chunk things).
    #Shall develop a sonor language in a non linear way maybe ?
    if set(['B5', 'C6', 'G#6']) <= set(notes):
        return("Am I watched atm?")
    else:
        return("How is my router going?")


def sonorInterpret(name_audio):
    notes=soundToNotes(name_audio)
    words=notesToWords(notes)
    print(words)
    return words

# #To test
#myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
#sd.wait()  # Wait until recording is finished
#write('./data/recorded.wav', fs, myrecording)  # Save as WAV file 
#sonorInterpret('./data/flute4.wav')
