import typing
import numpy
import logging

from Extractor import MFCCExtractor, DeltasExtractor
from LocalStorage import LocalStorage
import env


class MixtureChecker:

    def __init__(self):
        self._localStorage = LocalStorage()
        # ? move extractor to a thread
        self._mfccsExtractor = MFCCExtractor()
        self._deltasExtractor = DeltasExtractor()

    def setUser(self, login : str):
        self._user = self._localStorage.users[login]
        logging.info(f'[MixtureChecker] set user {login}')

    def compareWithPCM(self, pcm : typing.Any):
        r'''returns distance between stored mean and `pcm` -- bytes-like object with audio samples'''
        currentMFCCs = self._mfccsExtractor.extract(pcm)
        currentDelta = self._deltasExtractor.extract(currentMFCCs)
        test = numpy.vstack((currentMFCCs, currentDelta)).T
        gmm = self._user.speechData
        means = numpy.squeeze(gmm.means_)
        cov = numpy.squeeze(gmm.covariances_)
        distList = [env.mahalanobis(x, means, numpy.linalg.inv(cov)) for x in test]
        meanDist = numpy.mean(distList)
        thresholdDist = self._localStorage.threshold * self._user.trainMeanDistance
        logging.info(f'[MixtureChecker] User auth distance: {meanDist}, threshold distance: {thresholdDist}')
        if meanDist < thresholdDist:
            return True
        else:
            return False