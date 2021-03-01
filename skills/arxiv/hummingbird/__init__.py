###Hummingbird Skill
from adapt.intent import IntentBuilder # adapt intent parser
from mycroft import MycroftSkill, intent_handler #padatious intent parser
from mycroft.skills.audioservice import AudioService

#To record audio. Unless have to pass by mycroft?
import sounddevice as sd
from scipy.io.wavfile import write

import sonor

fs = 44100  # Sample rate
recording_length # Duration of recording by default (if not specified by user)

class HummingbirdSkill(MycroftSkill):
    def __init__(self):
        """ The __init__ method is called when the Skill is first constructed.
        It is often used to declare variables or perform setup actions, however
        it cannot utilise MycroftSkill methods as the class does not yet exist.
        """
        super().__init__()
        #self.learning = True 

    def initialize(self):
        """ Perform any final setup needed for the skill here.
        This function is invoked after the skill is fully constructed and
        registered with the system. Intents will be registered and Skill
        settings will be available."""
        self.audio_service = AudioService(self.bus) #instantiate an AudioService object:
        my_setting = self.settings.get('my_setting')
        self.seconds=recording_length 


    #What happen when detect like Intent. PADATIOUS: use .intent file
    @intent_handler('humming.intent')
    def handle_humming_intent(self, message):
        #(0) Catch the parameter
        time = message.data.get('time')
        if not time==None and not time=="":
            self.seconds=int(time)
        if self.seconds>1000 or self.seconds<1 : #in case error understanding
            self.seconds=recording_length 

        #(1) Record what human say during n second: shall pass via Mycroft ??
        myrecording = sd.rec(int(self.seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        write('./data/recorded.wav', fs, myrecording)  # Save as WAV file

        #(2) Interpret the Melody
        words=sonor.sonorInterpret('./data/recorded.wav')
        self.speak(words)# Just to check works, can remove after

        #(3) React. For now, simple correspondance sentence to sound playing
        if words=="Am I watched atm?":
            self.audio_service.play('./data/jupyter_magnetosphere.wav')
        else:
            self.audio_service.play('./data/birds.wav')


    def stop(self):
        pass


def create_skill():
    return HummingbirdSkill()



    #     #Play a list of tracks
    #     #self.audio_service.play(['file:///path/to/my/track.mp3', 'http://tracks-online.com/my/track.mp3'])
