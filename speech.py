#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import sys
import time

from aip import AipSpeech, AipNlp
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
            for loops in range(500000 * seconds):

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

class BaiduAiP:

    def __init__(self, configFile):

        appId = getProperty(configFile, 'baidu-aip-app-id')
        apiKey = getProperty(configFile, 'baidu-aip-api-key')
        secretKey = getProperty(configFile, 'baidu-aip-secret-key')

        self.init(appId, apiKey, secretKey)

    def init(self, appId, apiKey, secretKey):
        pass

class Speech(BaiduAiP):

    def init(self, appId, apiKey, secretKey):
        self.aipSpeech = AipSpeech(appId, apiKey, secretKey)

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
        path = OutputPath.getDataPath('input', 'pcm')

        record(path)

        '''
        cmd = 'aplay -r 16000 -f S16_LE -c 1 {}'.format(path)
        runCommand(cmd)
        '''

        with open(path, 'rb') as fp:

            obj = self.aipSpeech.asr(fp.read())

            error = obj.pop('err_no')

            if error is 0:
                res = obj.pop('result')

                if isinstance(res, list) and len(res) > 0:
                    return(res[0])
            else:
                print(obj.pop('err_msg'))

        return None

class Nlp(BaiduAiP):

    def init(self, appId, apiKey, secretKey):
        self.aipNlp = AipNlp(appId, apiKey, secretKey)

    def getItems(self, text):

        obj = self.aipNlp.lexer(text);

        if 'error_code' not in obj:
            items = obj.pop('items')

            if isinstance(items, list) and len(items) > 0:
                return items
        else:
            print('Error:', obj.pop('error_code'), ',', obj.pop('error_msg'))

        return None

    def getPersons(self, text):

        items = self.getItems(text);

        if items is None:
            return None

        persons = list()

        for item in items:

            ne = item.pop('ne')

            if 'PER' == ne or ('' == ne and 'nr' == item.pop('pos')):
                persons.append(item.pop('item'))

        if len(persons) is 0:
            return None

        return persons

    def getNumbers(self, text):

        # XXX: Sometimes, the last number will be not recognized, so append a full stop at the end.
        # That should be removed in future.
        text = '{}.'.format(text)

        items = self.getItems(text);

        if items is None:
            return None

        numbers = list()

        for item in items:

            if '' != item.pop('ne'):
                continue

            if 'm' != item.pop('pos'):
                continue

            numbers.append(item.pop('item'))

        if len(numbers) is 0:
            return None

        return numbers

    def isSimilar(self, text_1, text_2, options=None):

        SIMILAR_SCORE = 0.75

        obj = self.aipNlp.simnet(text_1, text_2, options)

        if 'error_code' not in obj:
            score = obj.pop('score')

            if score >= SIMILAR_SCORE:
                return True
        else:
            print('Error:', obj.pop('error_code'), ',', obj.pop('error_msg'))

        return False

