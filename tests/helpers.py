from typing import Any


def assert_ship_stats_message_matches_json(message_str: str, expected_ship: dict[str, Any]) -> None:
    """Exhaustively verifies every parsed dynamic field from the ship model in the given message."""
    # basic fields
    assert f'`{expected_ship["id_"]}`' in message_str, (
        f'Catalog ID `{expected_ship["id_"]}` missing or malformed'
    )
    assert expected_ship['ship_name'] in message_str, 'Ship Name missing'
    assert expected_ship['pilot_name'] in message_str, 'Pilot Name missing'

    # shields
    assert f'**Shields**: `{expected_ship["shields"]}/' in message_str, (
        'Shields missing or malformed'
    )

    # damage cards
    damage_cards = expected_ship.get('damage_cards', [])
    faceup_card_ids = [card['id_'] for card in damage_cards if card.get('faceup') is True]
    facedown_card_count = sum(1 for card in damage_cards if card.get('faceup') is False)
    assert f'**Face-down Damage Cards**: `{facedown_card_count}`' in message_str, (
        'Facedown damage card count wrong'
    )
    assert str(faceup_card_ids) in message_str, (
        f'Face-up Damage Cards string mismatch. Expected: {faceup_card_ids}'
    )

    # charges (Force, Standard, Energy), which may be optional
    if expected_ship.get('force_charges') is not None:
        assert f'**Force Charges**: `{expected_ship["force_charges"]}/' in message_str, (
            'Force charges rendering missing'
        )
    if expected_ship.get('std_charges') is not None:
        assert f'**Standard Charges**: `{expected_ship["std_charges"]}/' in message_str, (
            'Standard charges rendering missing'
        )
    if expected_ship.get('energy_charges') is not None:
        assert f'**Energy**: `{expected_ship["energy_charges"]}/' in message_str, (
            'Energy charges rendering missing'
        )

    # tokens
    for token_type, count in expected_ship.get('tokens', {}).items():
        expected_token_line = f'`{token_type}: {count}`'
        assert expected_token_line in message_str, (
            f"Token tracking block entry '{expected_token_line}' missing"
        )

    # target lock
    assert f'**Target Lock**: `{expected_ship["target_lock"]}`' in message_str, (
        'Target lock rendering missing'
    )

    # conditions
    expected_conditions = [cond['id_'] for cond in expected_ship.get('conditions', [])]
    assert str(expected_conditions) in message_str, 'Conditions array rendering mismatch'

    # upgrades
    expected_upgrades = [up['id_'] for up in expected_ship.get('upgrades', [])]
    assert str(expected_upgrades) in message_str, 'Upgrades array rendering mismatch'

    # TODO positional stuff
