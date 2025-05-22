import typing
import logging
import librosa
import numpy
import sklearn.preprocessing

import env


class MFCCExtractor:

    def __init__(self):
        pass

    def extract(self, data : typing.Any) -> numpy.ndarray:
        r'''Recieves a time-domain data (numpy array) and computes MFCC'''
        logging.info(f'[MFCCExtractor] Extracting from {type(data)}')
        scaler = sklearn.preprocessing.StandardScaler()
        data = librosa.util.buf_to_float(data, n_bytes=env.SAMPLEBYTES)
        mfccs : numpy.ndarray = librosa.feature.mfcc(
            y=data,
            sr=env.SAMPLERATE,
            n_mfcc=env.N_MFCCS,
            dct_type=env.LIBROSA_DCT_TYPE,
            n_fft=env.N_FFT,
            hop_length=env.HOP_LENGTH
        )
        return scaler.fit_transform(mfccs.T).T


class DeltasExtractor:

    def __init__(self):
        pass

    def extract(self, data: numpy.ndarray) -> numpy.ndarray:
        r'''Recieves a time-frequency feature (numpy array) and computes delta'''
        logging.info(f'[DeltasExtractor] Extracting from {type(data)}')
        return librosa.feature.delta(data, width=3)

