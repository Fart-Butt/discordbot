from butt_config import ButtConfig

a = ButtConfig(154337182717444096)


def test_allowed_bots():
    assert 249966240787988480 in a.allowed_bots
