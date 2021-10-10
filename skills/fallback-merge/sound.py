
#Main sound library used, #cf https://github.com/carlthome/python-audio-effects
from pysndfx import AudioEffectsChain 
#Second library in use currently, for overlay
from pydub import AudioSegment 
import random


######*****************************************************************************************
######*********************** SOUND PROCEDURES ***********************************************
######*****************************************************************************************

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
    "reverse": 0.4

}


def random_distortion(infile, outfile, infile2=None,  proba_overlay=0.8, min_gain_drop=4, max_gain_drop=8, max_length=0):
    """
    infile: adress of sound file 
    proba_overlay: probability of overlaying original sound with distored (when want to still hear...)
    gain: gain applied to distorted sound if overlay
    max_length: cut to a max length if not 0

    """

    fx = AudioEffectsChain()

    if random.random()<EFFECTS["lowpass"]:
        # lowshelf(gain=-20.0, frequency=100, slope=0.5) # "lowshelf takes 3 parameters: a signed number for gain or attenuation in dB, filter frequency in Hz and slope (default=0.5, maximum=1.0)."
        freq=random.randint(100, 500)
        print("Lowpass at {}".format(freq))
        fx=fx.lowshelf(frequency=freq)
       
    if random.random()<EFFECTS["highpass"]:
        #highshelf(self, gain=-20.0, frequency=3000, slope=0.5) 
        freq=random.randint(1000, 4000)
        print("Highpass at {}".format(freq))
        fx=fx.highshelf(frequency=freq)
    
    if random.random()<EFFECTS["reverb"]:
        # reverb(self, reverberance=50, hf_damping=50, room_scale=100, stereo_depth=100, pre_delay=20, wet_gain=0, wet_only=False) #reverb takes 7 parameters: reverberance, high-freqnency damping, room scale, stereo depth, pre-delay, wet gain and wet only (True orFalse)"""
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


    if random.random()<EFFECTS["overdrive"]:
        print("Overdrive")
        #    overdrive(self, gain=20, colour=20)  # overdrive takes 2 parameters: gain in dB and colour which effects the character of the distortion effet. Both have a default value of 20. TODO - changing color does not seem to have an audible effect
        fx=fx.overdrive()

    # if random.random()<EFFECTS["pitch"]:#TODO: Add
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

    if random.random()<proba_overlay:
        print("Overlay")
        original = AudioSegment.from_file(infile)
        distorted = AudioSegment.from_file(outfile)
        length = min(len(original), len(distorted))
        if max_length>0:
            length=min(length, max_length)
        original=original-2
        min_gain_drop=max(min_gain_drop, 2)
        max_gain_drop=max(min_gain_drop+1, max_gain_drop)
        combined = original[:length].overlay(distorted[:length]- random.randrange(min_gain_drop, max_gain_drop), loop=True)
        combined.export(outfile, format='wav')
    elif max_length>0 and len(distorted)>max_length:
        print("Cut file to max length")
        distorted = AudioSegment.from_file(outfile)
        combined = distorted[:max_length]-2#also attenuate a bit
        combined.export(outfile, format='wav')
     