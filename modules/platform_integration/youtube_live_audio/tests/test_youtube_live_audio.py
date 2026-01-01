from modules.platform_integration.youtube_live_audio import AudioStreamConfig, YouTubeLiveAudioSource


def test_default_config_values():
    source = YouTubeLiveAudioSource()
    assert isinstance(source.config, AudioStreamConfig)
    assert source.config.sample_rate_hz == 16000
    assert source.config.channels == 1
    assert source.config.sample_format == "s16le"
