#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time

from aip import AipSpeech
from utils import getProperty, runCommand, OutputPath

try:
    import alsaaudio

    def record(filename, seconds=5, channels=1, rate=16000):

        print('alsaaudio')

        FORMAT = alsaaudio.PCM_FORMAT_S16_LE
        TRUCK = 160

        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        inp.setchannels(channels)
        inp.setrate(rate)
        inp.setformat(FORMAT)
        inp.setperiodsize(TRUCK)

        fp = open(filename, 'wb')

        try:
            for loops in range(1000000 * seconds):

                # Read data from device
                l, data = inp.read()
              
                if l:
                    fp.write(data)
                    time.sleep(.001)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            fp.close()

except:

    import pyaudio

    def record(filename, seconds=5, channels=1, rate=16000):

        print('pyaudio')

        FORMAT = pyaudio.paInt16
        CHUNK = 1024

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=CHUNK)

        fp = open(filename, 'wb')

        try:
            for i in range(0, int(rate / CHUNK * seconds)):
                data = stream.read(CHUNK)
                fp.write(data)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
        finally:
            fp.close()

            stream.stop_stream()
            stream.close()

            p.terminate()

class Speech:

    def __init__(self, configFile):

        appId = getProperty(configFile, 'baidu-aip-app-id')
        apiKey = getProperty(configFile, 'baidu-aip-api-key')
        secretKey = getProperty(configFile, 'baidu-aip-secret-key')

        self.aipSpeech = AipSpeech(appId, apiKey, secretKey)

    def __repr__(self):
        pass

    def voiceOut(self, stringContent):

        result = self.aipSpeech.synthesis(stringContent, 'zh', 1, {'vol': 15, 'per': 0})

        if not isinstance(result, dict):

            path = OutputPath.getDataPath('voice', 'wav')
            with open(path, 'wb') as fp:
                fp.write(result)

            cmd = 'mplayer {}'.format(path)
            runCommand(cmd)

    def getVoiceText(self):

        # XXX record from micphone
        filename = None

        with open(filename, 'rb') as fp:
            return self.aipSpeech.asr(fp.read())

        return None

