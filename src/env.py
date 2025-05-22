import numpy

# recorder settings
SAMPLERATE = 8000
CHANNELS   = 1
SAMPLESIZE = 16
CODEC      = 'audio/pcm'
SECONDS    = 2

SAMPLEBYTES = int(SAMPLESIZE / 8)


# mfccs extractor settings
N_MFCCS          = 12
LIBROSA_DCT_TYPE = 2 # 2 - the most commonly used form, 3 - inverse of DCT-II
N_FFT            = 512
HOP_LENGTH       = 256


LOCAL_STORAGE = 'storage'

DEFAULT_ADMIN = 'ADMIN'


def mahalanobis(x : numpy.ndarray, mean : numpy.ndarray, invcov : numpy.ndarray):
    return numpy.sqrt( (x - mean).T @ invcov @ (x - mean) )
