import time
from utils.oauth_manager import QuotaManager

def test_quota_manager_cooldown():
    qm = QuotaManager()
    test_set = "set_1"

    # Ensure not in cooldown initially
    assert not qm.is_in_cooldown(test_set)

    # Start cooldown and assert active
    qm.start_cooldown(test_set)
    assert qm.is_in_cooldown(test_set)

    # Simulate cooldown expiry
    qm.cooldowns[test_set] -= qm.COOLDOWN_DURATION + 1
    assert not qm.is_in_cooldown(test_set)

    print("QuotaManager cooldown logic passed ✅")

if __name__ == "__main__":
    test_quota_manager_cooldown() 