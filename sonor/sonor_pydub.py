



import random
import pathlib
# sound_path=str(pathlib.Path(__file__).parent.parent.absolute())+"/collective_memory/text/"

from pydub import AudioSegment
from pydub.playback import play

sound_path1=str(pathlib.Path(__file__).parent.absolute())+"/voice.wav"
sound_path2=str(pathlib.Path(__file__).parent.absolute())+"/taiyuan.wav"


# main class in Pydub is AudioSegment. 
# An AudioSegment acts as a container to load, manipulate, and save audio.
loop1 = AudioSegment.from_wav(sound_path1)
loop2 = AudioSegment.from_wav(sound_path2)

#cf https://betterprogramming.pub/simple-audio-processing-in-python-with-pydub-c3a217dabf11
#Pydub is fantastic for simple audio tasks. 
# However, if you want to do more complex processing such as speeding up or slowing down sounds, changing pitch, 
# or applying time-varying effects, it’s not the best option.

def random_distortion_duo(sound1, sound2):
    """
    """
    proba_overlay=0.1
    distorted1=random_distortion(sound1)
    distorted2=random_distortion(sound2)

    n=random.random()
    if n<proba_overlay:
        print("Overlay")
        length = min(len(distorted1), len(distorted2))
        #pan before differently:
        distorted1=distorted1.pan(random.randrange(-0.5, 0))
        distorted2=distorted2.pan(random.randrange(0, 0.5))
        final=distorted2[:length].overlay(distorted1[:length])
    else:
        final=distorted1

     #fade in: .fade_in(fade_time)
    #fade out: .fade_out(fade_time)
    #overlay: = sound2[:length].overlay(sound1)

    return final

def random_distortion(sound):
    """
    """
    #Effects: low pass filter, reverse, pan. Overlay with itself?
    proba_lowpass=0.3
    proba_reverse=0.2
    proba_overlay_reverse=0.3

    distorted=sound 

    if random.random()<proba_lowpass:
        freq=random.randrange(200, 3000)
        print("Low pass at {}".format(freq))
        # Filter the beat at 3kHz #TODO:not uniform filtration ?
        distorted = sound.low_pass_filter(freq)
    if random.random()<proba_overlay_reverse:
        print("Reverse overlay and pan")#TODO: create different mix left and right
        reverse = distorted.reverse()
        reverse=reverse.pan(random.randrange(-0.5, 0))
        distorted=distorted.pan(random.randrange(0, 0.5))
        # Mix loop with the reversed loop at -XdB
        distorted=distorted.overlay(reverse - random.randrange(0, 5), loop=True)
    elif random.random()<proba_reverse:
        print("Reverse")
        distorted = distorted.reverse()

    # Mix loop2 with a reversed, panned version
    #loop2.reverse().pan(-0.5).overlay(loop2.pan(0.5))

    #fade in: .fade_in(fade_time)
    #fade out: .fade_out(fade_time)

    return distorted


distorted=random_distortion_duo(loop1, loop2)
play(distorted)