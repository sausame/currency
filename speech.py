#!/usr/bin/env python
# -*- coding:utf-8 -*-

import subprocess
from aip import AipSpeech
from utils import getProperty, runCommand, OutputPath

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

