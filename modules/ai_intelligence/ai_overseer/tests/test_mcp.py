from modules.ai_intelligence.ai_overseer.src.mcp_integration import RubikDAE


def test_rubik_compose_enum_value():
    assert RubikDAE.COMPOSE.value == "rubik_compose"
