# GitPushDAE - Autonomous Git Push Daemon
# WSP 91 Compliant DAEMON for autonomous development publishing

from .src.git_push_dae import GitPushDAE, PushContext, PushDecision, HealthStatus

__all__ = [
    'GitPushDAE',
    'PushContext',
    'PushDecision',
    'HealthStatus'
]

__version__ = '1.0.0'
__author__ = '0102'
__description__ = 'WSP 91 compliant DAEMON for autonomous git push decisions'
