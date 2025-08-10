import logging
import pytest
from modules.platform_integration.youtube_proxy import YouTubeProxy

@pytest.fixture
def proxy():
    logger = logging.getLogger("YouTubeProxyTest")
    return YouTubeProxy(logger=logger, config={})
