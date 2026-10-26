from ready import llm
from ready.repo import Candidate


class _Msg:
    def __init__(self, content):
        self.message = type("M", (), {"content": content})


def test_model_cannot_invent_paths(monkeypatch, shop):
    monkeypatch.setenv("READY_API_KEY", "x")
    monkeypatch.setenv("READY_MODEL", "m")

    class FakeClient:
        def __init__(self, **kw):
            self.chat = type("C", (), {"completions": self})()

        def create(self, **kw):
            return type("R", (), {"choices": [_Msg('{"ranked": ["evil/new.py", "shop/cart.py"], "summary": "s", "acceptance": []}')]})

    import openai
    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    d = llm.rank_and_draft("t", [Candidate("shop/cart.py", 1.0)], shop, ["Cart"])
    assert d.ranked == ["shop/cart.py"]
