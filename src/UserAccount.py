import typing
from sklearn.mixture import GaussianMixture


class UserAccount:

    def __init__(self, login : str, speechData : typing.Optional[GaussianMixture] = None, trainMeanDistance : float = None):
        self._login = login
        self._speechData = speechData
        self._trainMeanDistance = trainMeanDistance

    @property
    def login(self):
        return self._login

    @property
    def speechData(self) -> typing.Union[GaussianMixture, None]:
        return self._speechData

    @speechData.setter
    def speechData(self, data : GaussianMixture):
        self._speechData = data

    def isAdmin(self):
        return False

    def hasSpeechData(self) -> bool:
        return self._speechData is not None

    @property
    def trainMeanDistance(self) -> float:
        return self._trainMeanDistance

    @trainMeanDistance.setter
    def trainMeanDistance(self, mean : float):
        self._trainMeanDistance = mean

    


class Admin(UserAccount):

	def isAdmin(self):
		return True
