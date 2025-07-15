"""
X Twitter DAE Communication Node Source Module

First decentralized autonomous entity communication node implementing
WSP 26-29 compliance with entangled authentication, autonomous communication,
and smart DAO evolution capabilities with WRE integration.
"""

from .x_twitter_dae import (
    XTwitterDAENode,
    DAEIdentity,
    DAEIdentityState,
    AuthenticationLevel,
    CommunicationMode,
    SocialEngagementToken,
    AutonomousPost,
    CABRInteraction,
    DAEAuthenticator,
    CABREngine,
    create_x_twitter_dae_node,
    test_x_twitter_dae
)

__version__ = "1.0.0"
__all__ = [
    'XTwitterDAENode',
    'DAEIdentity',
    'DAEIdentityState', 
    'AuthenticationLevel',
    'CommunicationMode',
    'SocialEngagementToken',
    'AutonomousPost',
    'CABRInteraction',
    'DAEAuthenticator',
    'CABREngine',
    'create_x_twitter_dae_node',
    'test_x_twitter_dae'
] 