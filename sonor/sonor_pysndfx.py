



import random
import pathlib
# sound_path=str(pathlib.Path(__file__).parent.parent.absolute())+"/collective_memory/text/"

from pysndfx import AudioEffectsChain


from pydub import AudioSegment #JUST FOR OVERLAY...



sound_path1=str(pathlib.Path(__file__).parent.absolute())+"/voice.wav"
sound_path2=str(pathlib.Path(__file__).parent.absolute())+"/taiyuan.wav"
outfile=str(pathlib.Path(__file__).parent.absolute())+"/temp.wav"

#cf https://github.com/carlthome/python-audio-effects

#TODO: Add more effects such as:
# equalizer(frequency, q=1.0, db=-3.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandpass(frequency, q=1.0)  #"frequency in Hz, q or band-width (default=1.0)"
# bandreject(frequency, q=1.0) #"frequency in Hz, q or band-width (default=1.0)"
# compand(self, attack=0.2, decay=1, soft_knee=2.0, threshold=-20, db_from=-20.0, db_to=-20.0) #"""compand takes 6 parameters: attack (seconds), decay (seconds), soft_knee (ex. 6 results  in 6:1 compression ratio), threshold (a negative value  in dB), the level below which the signal will NOT be companded  (a negative value in dB), the level above which the signal will    NOT be companded (a negative value in dB). This effect   manipulates dynamic range of the input file.
# #delay(self, gain_in=0.8, gain_out=0.5, delays=None,decays=None, parallel=False)         #"delay takes 4 parameters: input gain (max 1), output gain and then two lists, delays and decays . Each list is a pair of comma seperated values within parenthesis.
# speed(self, factor, use_semitones=False)# s"speed takes 2 parameters: factor and use-semitones (True or False).When use-semitones = False, a factor of 2 doubles the speed and raises the pitch an octave. The same result is achieved with factor = 1200 and use semitones = True.


#TODO: may overlay with original at the end , and volume...other could be very small
#TODO: Normalise sound ?  normalize(self) "normalize has no parameters, boosts level so that the loudest part of your file reaches maximum, without clipping.
#TODO proba origian pure sound?

def random_distortion(infile, infile2=None):
    """

    """

    #Effects: low pass filter, reverse, pan. Overlay with itself?
    EFFECTS={
        "lowpass": 0.3,
        "highpass": 0.3,
        "reverb": 0.4,
        "phaser": 0.2,
        "chorus": 0.3,
        "overdrive": 0.2,
        "pitch": 0.2,
        "tempo": 0.3,
        "tremolo": 0.3,
        "reverse": 0.4,
        "overlay": 0.8

    }

    fx = AudioEffectsChain()



    if random.random()<EFFECTS["lowpass"]:
        # lowshelf(gain=-20.0, frequency=100, slope=0.5) # "lowshelf takes 3 parameters: a signed number for gain or attenuation in dB, filter frequency in Hz and slope (default=0.5, maximum=1.0)."
        freq=random.randint(100, 500)
        print("Lowpass at {}".format(freq))
        fx=fx.lowshelf(frequency=freq)
       
    if random.random()<EFFECTS["highpass"]:
        #    highshelf(self, gain=-20.0, frequency=3000, slope=0.5) 
        freq=random.randint(1000, 4000)
        print("Highpass at {}".format(freq))
        fx=fx.highshelf(frequency=freq)
    
    if random.random()<EFFECTS["reverb"]:
        #    reverb(self, reverberance=50, hf_damping=50, room_scale=100, stereo_depth=100, pre_delay=20, wet_gain=0, wet_only=False) #reverb takes 7 parameters: reverberance, high-freqnency damping, room scale, stereo depth, pre-delay, wet gain and wet only (True orFalse)"""
        room_scale=random.randint(20, 100)
        reverberance=random.randint(20, 50)
        print("Reverb")
        fx=fx.reverb(reverberance=reverberance, room_scale=room_scale)

    if random.random()<EFFECTS["phaser"]:
        speed=random.randrange(0, 2)
        print("Phaser")
        #    phaser(self, gain_in=0.9, gain_out=0.8, delay=1, decay=0.25, speed=2, triangular=False)# phaser takes 6 parameters: input gain (max 1.0), output gain (max 1.0), delay, decay, speed and LFO shape=trianglar (which must be set to True or False)"""
        fx=fx.phaser(speed=speed)

#TODO issue with decays form
    # if random.random()<EFFECTS["chorus"]:
    #     print("Chorus")
    #     #    chorus(self, gain_in, gain_out, decays)
    #     fx=fx.chorus(gain_in=0.2, gain_out=0.2, decays=[[2], [10], [6]])

#TODO: More fade in and out..cut ?
#TODO: CUt to a maximum length

    if random.random()<EFFECTS["overdrive"]:
        print("Overdrive")
        #    overdrive(self, gain=20, colour=20)  # overdrive takes 2 parameters: gain in dB and colour which effects the character of the distortion effet. Both have a default value of 20. TODO - changing color does not seem to have an audible effect
        fx=fx.overdrive()

    # if random.random()<EFFECTS["pitch"]:
    #     print("Pitch")
    #     #    pitch(self, shift, use_tree=False, segment=82, search=14.68, overlap=12) #pitch takes 4 parameters: user_tree (True or False), segment, search and overlap."""
    #     fx=fx.pitch()


    if random.random()<EFFECTS["tempo"]:
        factor=random.randrange(0, 2)
        factor=max(factor, 0.1)
        print("Tempo")
        #tempo(self, factor, use_tree=False, opt_flag=None, segment=82, search=14.68, overlap=12)#tempo takes 6 parameters: factor, use tree (True or False), option flag, segment, search and overlap). This effect changes the duration of the sound without modifying pitch.
        fx=fx.tempo(factor=factor)

    if random.random()<EFFECTS["tremolo"]:
        freq=random.randint(500,2500)
        depth=random.randint(0,60)
        print("Tremolo")
        #    tremolo(self, freq, depth=40)#tremolo takes two parameters: frequency and depth (max 100)"""
        fx=fx.tremolo(freq=freq, depth=depth)
    
    if random.random()<EFFECTS["reverse"]:
        print("Reverse")
        fx=fx.reverse()

    # Apply phaser and reverb directly to an audio file.
    fx(infile, outfile)

    if random.random()<EFFECTS["overlay"]:
        print("Overlay")
        original = AudioSegment.from_file(infile)
        distorted = AudioSegment.from_file(outfile)
        length = min(len(original), len(distorted))
        original=original-1
        combined = original[:length].overlay(distorted[:length]- random.randrange(2, 8), loop=True)
        combined.export(outfile, format='wav')

    # Mix loop2 with a reversed, panned version
    #loop2.reverse().pan(-0.5).overlay(loop2.pan(0.5))

    #fade in: .fade_in(fade_time)
    #fade out: .fade_out(fade_time)



random_distortion(sound_path1, sound_path2)