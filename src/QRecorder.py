
from PyQt5 import QtCore, QtMultimedia
import logging
import typing
import env


class QRecorder(QtCore.QObject):

    onRecorded = QtCore.pyqtSignal(QtCore.QByteArray)

    # maybe move this to constructor args
    SAMPLERATE = env.SAMPLERATE
    CHANNELS   = env.CHANNELS
    SAMPLESIZE = env.SAMPLESIZE
    CODEC      = env.CODEC

    def __init__(self, duration : int):
        r''' Class for recording audio from default input device. 
            Uses env.py for parameter specification. 
            * :param:`duration` - recording duration in seconds
        '''
        super().__init__()

        self._sharedByteArray = QtCore.QByteArray()

        self._destBuffer = QtCore.QBuffer(self._sharedByteArray)
        self._destBuffer.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        self._recordedBuffer = QtCore.QBuffer(self._sharedByteArray)
        self._recordedBuffer.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)

        self._format = QtMultimedia.QAudioFormat()
        self._format.setSampleRate(self.SAMPLERATE)
        self._format.setChannelCount(self.CHANNELS)
        self._format.setSampleSize(self.SAMPLESIZE)
        self._format.setCodec(self.CODEC)
        self._format.setByteOrder(
            QtMultimedia.QAudioFormat.Endian.LittleEndian
        )
        self._format.setSampleType(
            QtMultimedia.QAudioFormat.SampleType.SignedInt
        )

        self._devInfo = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        assert self._devInfo.isFormatSupported(self._format), \
            f"{self._format} Format is not supported"

        self.duration = duration
        self._sampleCount = duration * self.SAMPLERATE

        self.audioInput = QtMultimedia.QAudioInput(format=self._format, parent=self)
        self.audioInput.stateChanged.connect(self._stateChangedHandler)
        self.audioInput.setNotifyInterval(duration * 10)

        self.recTimer = QtCore.QTimer(self)
        self.recTimer.timeout.connect(self.stopRecording)


    @QtCore.pyqtSlot(QtMultimedia.QAudio.State)
    def _stateChangedHandler(self, state : QtMultimedia.QAudio.State):
        logging.info(f'[QRecorder] Current state {state}')


    @QtCore.pyqtSlot()
    def startRecording(self) -> None:
        self.recTimer.start(self.duration * 1000)
        logging.info(f'[QRecorder] Recording started...')
        self.audioInput.start(self._destBuffer)


    @QtCore.pyqtSlot()
    def stopRecording(self) -> None:
        self.audioInput.stop()
        self.recTimer.stop()
        logging.info(f'[QRecorder] Recording stopped...')
        self.onRecorded.emit(self._sharedByteArray)
        self._recordedBuffer.seek(0)
        self._destBuffer.seek(0)
        # TODO: move this to del
        # self._recordedBuffer.close()
        # self._destBuffer.close()


    def getProgressInTime(self) -> typing.Tuple[int, int]:
        r'''get recording progress as tuple(seconds, milliseconds)'''
        microsecs = self.audioInput.processedUSecs()
        millisecs = microsecs // 1000
        seconds = millisecs // 1000
        millisecs = millisecs % 1000
        return (seconds, millisecs)


    def getProgressInPercents(self) -> int:
        r'''get recording progress in percents'''
        arraySize = self._format.bytesForFrames(self._sampleCount)
        return (self._destBuffer.pos() * 100) // arraySize
