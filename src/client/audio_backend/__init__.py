import enum
from src.log import log, warn

from openal import (
    oalOpen,
    oalStream,
    oalQuit,
    AL_PLAYING
)


class PlaybackStatus(enum.Enum):
    PAUSED = 0
    PLAYING = 1


class PlaybackStrategy(enum.Enum):
    LAZY_STREAM = 0
    PRIORITIZE_LOAD = 1


class Audio:
    def __init__(self, filename: str, playback_strategy: PlaybackStrategy, audio_backend):
        self.playback_strategy = playback_strategy
        if playback_strategy == PlaybackStrategy.PRIORITIZE_LOAD:
            self.source = oalOpen(filename)
        else:
            self.source = oalStream(filename)

    def lifetime(self, task):
        if self.get_state() == PlaybackStatus.PLAYING:
            pass
        return task.cont

    def play(self):
        self.source.play()

    def stop(self):
        self.source.stop()

    def get_state(self) -> PlaybackStatus:
        if self.source.get_state() == AL_PLAYING:
            return PlaybackStatus.PLAYING
        return PlaybackStatus.PAUSED


class AudioBackend:
    """
    Work-in-progress audio backend -- this is not ready for use yet and probably never will.
    """

    def __init__(self, instance,
                 channels: int = 2, rate: int = 22100, ogg_buffer_size: int = 16384, max_stream_buffer_count: int = 4):
        self.instance = instance
        instance.get_event('on_exit').subscribe(self.cleanup_al)

    def cleanup_al(self):
        log('Cleaning up OpenAL devices.', 'Worker/AudioBackend')
        oalQuit()
