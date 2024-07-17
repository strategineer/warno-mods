import re
import sys
import pathlib
import time
import tempfile
import queue

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

DESCRIPTORS_PATH = "GameData/Generated/Sound/AcknowDescriptors.ndf"
MOD_SOUNDS_BASEPATH = "C:\dev\warno_bark_mod\GameData\Assets\Sons\Acknows"

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())




print("Record Warno VO")
# TODO go through each voice line one by one
# TODO press spacebar to start/stop the recording of each and save to the right place as an ogg file
# TODO have a param to filter files by filename/prefix, to overwrite them or not so we can continue where we left off, 
ls = []
txt = ""
with open(DESCRIPTORS_PATH) as input_file:
    txt = input_file.read()
    ls = re.findall("Identifier = '([^']+)'", txt)
for lang in set([l[:2] for l in ls]):
    p = pathlib.Path(MOD_SOUNDS_BASEPATH, lang)
    p.mkdir(exist_ok=True)
# TODO make this filter a parameter
ls = [l for l in ls if l.startswith("FR/")]
samplerate = 48000
channels = 1
sd.default.device = ("Microphone (Blue Snowball), Windows WASAPI", None)
sd.default.samplerate = samplerate
sd.default.channels = channels
wasapi_exclusive = sd.WasapiSettings(exclusive=True)
sd.default.extra_settings = wasapi_exclusive
for f in ls:
    q = queue.Queue()
    output_filepath = pathlib.Path(MOD_SOUNDS_BASEPATH, f"{f}.ogg")
    if output_filepath.exists():
        print(f"{output_filepath} already exists, skipping to fix file")
        continue
    k = input(f"Press Enter to record for: {f}")
    if k:
        sys.exit()
    print("...")
    time.sleep(0.1)
    print("..")
    time.sleep(0.1)
    print(".")
    time.sleep(0.1)
    print("Go!")
    try:
        # Make sure the file is opened before recording anything:
        with sf.SoundFile(output_filepath, mode='x', samplerate=samplerate,
                        channels=channels) as file:
            with sd.InputStream(samplerate=samplerate, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while True:
                    file.write(q.get())
    except KeyboardInterrupt:
        continue
    except Exception as e:
        sys.exit(type(e).__name__ + ': ' + str(e))