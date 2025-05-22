

from typing import Union
import librosa
import numpy
from torchaudio.transforms import MFCC
import torch
import torchaudio





from Extractor import MFCCExtractor



class Checker:

    def __init__(self, threshhold):
        self._threshhold = threshhold
        # ? move extractor to a thread
        self._extractor = MFCCExtractor()
        self._mse = torch.nn.MSELoss()

    def load(self, filename):
        self._storedMFCC = torch.load(filename)


    def compareWith(self, currentData : Union[str, numpy.ndarray, torch.Tensor]):
        r'''returns mse loss between stored MFCC and `currentData`'''
        
        if isinstance(currentData, str):
            # is a path
            _currentMFCC = self._getFromPath(currentData)
            self._err = self._mse(self._storedMFCC, _currentMFCC)
            return self._err

        elif isinstance(currentData, numpy.ndarray):
            # is a waveform
            _currentMFCC = self._getFromWaveform(currentData)
            self._err = self._mse(self._storedMFCC, _currentMFCC)
            return self._err

        elif isinstance(currentData, torch.Tensor):
            # is a MFCC tensor
            self._err = self._mse(self._storedMFCC, currentData)
            return self._err

        else:
            # TODO: message
            raise TypeError(f'expected types str, ndarray or Tensor, but got {type(currentData)}')


    def _getFromPath(self, path) -> torch.Tensor:
        w, sr = torchaudio.load()
        return self._extractor.extract(w)

    def _getFromWaveform(self, waveform : numpy.ndarray) -> torch.Tensor:
        return self._extractor.extract(waveform)


    def areSame(self, a, b):
        # TODO: mfccs 
        pass







