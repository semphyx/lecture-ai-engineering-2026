"""第6回 宿題（実装）: make_quiz のテスト（LLM も API キーも使わない）。"""

import json

import pytest
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.test import TestModel

from app import tools
from app.mcp_agent import MCP_CONFIG, build_mcp_agent


def test_quiz_comes_from_the_lecture():
    quiz = json.loads(tools.make_quiz(2))
    assert quiz["lecture"] == 2
    assert quiz["question"].endswith("の意味は？")
    definitions = {e["definition"] for e in tools.load_glossary() if e["lecture"] == 2}
    assert quiz["answer"] in definitions


@pytest.mark.parametrize("lecture", [0, -1, 14, 99])
def test_out_of_range_returns_message(lecture):
    message = tools.make_quiz(lecture)
    assert f"第{lecture}回はありません" in message
    assert "第1回〜第13回" in message


def test_lecture_without_terms_returns_message():
    assert 5 not in {e["lecture"] for e in tools.load_glossary()}
    assert "まだ用語集にない" in tools.make_quiz(5)


def test_make_quiz_is_offered_and_message_comes_back_through_mcp(tmp_path):
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    path = tmp_path / "mcp_servers.json"
    path.write_text(json.dumps({"mcpServers": {"glossary": config["mcpServers"]["glossary"]}}), encoding="utf-8")

    model = TestModel(call_tools=["glossary_make_quiz"])  # TestModel は lecture=0 のようなダミーの引数で呼ぶ
    result = build_mcp_agent(path).run_sync("クイズを作って", model=model)

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert "glossary_make_quiz" in offered
    returns = [p for m in result.all_messages() for p in m.parts if isinstance(p, ToolReturnPart)]
    assert returns and returns[0].tool_name == "glossary_make_quiz"
    assert "ありません" in str(returns[0].content) or "の意味は？" in str(returns[0].content)
