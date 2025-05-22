

import pyaudio
import numpy

from PyQt5 import QtCore



class Recorder(QtCore.QObject):

	onRecorded = QtCore.pyqtSignal()

	def __init__(self, bufferSize : int, sr : int, dur : int):
		self.p = pyaudio.PyAudio()
		self._sampleType = pyaudio.paInt16
		self._bufferSize = bufferSize
		self._channelCount = 1
		self._sampleRate = sr
		self.stream = None
		self.recordBuffer = numpy.zeros(sr * dur, dtype=numpy.int16)
		self._recordBufferPointer = 0 # where to write recorded buffer


	def getStream(self):
		
		if self.stream is not None:
			self.stream.stop_stream()
			self.stream.close()
		
		self.stream = self.p.open(
			format=self._sampleType,
			channels=self._channelCount,
			rate=self._sampleRate,
			input=True,
			output=False,
			frames_per_buffer=self._bufferSize,
			stream_callback=self.recordCallback
		)
		return self.stream


	def recordCallback(self, in_data, frame_count, time_info, status):
		b = self._recordBufferPointer
		e = self._recordBufferPointer + self._bufferSize
		if b == len(self.recordBuffer):
			return (0, pyaudio.paComplete)
		else:
			self._data = numpy.frombuffer(in_data, dtype=numpy.int16)
			self.recordBuffer[b:e] = self._data
			self._recordBufferPointer = e
			# отстреливать в UI о проценте заполнения буфера
			return (self._data, pyaudio.paContinue)


	def getProgress(self) -> tuple:
		seconds = int(self._recordBufferPointer / self._sampleRate)
		percentage = int(100 * self._recordBufferPointer / len(self.recordBuffer))
		if self._recordBufferPointer > len(self.recordBuffer):
			self.stream.stop_stream()
		return (seconds, percentage)

	



	def getRecording(self) -> numpy.ndarray:
		return self.recordBuffer
		


	



