from modules.communication.voice_command_ingestion import VoiceCommandIngestion


def test_default_trigger_token():
    ingestion = VoiceCommandIngestion()
    assert ingestion.trigger_token == "0102"
