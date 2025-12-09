# tests/test_parse.py
from perception import parse

def test_sexpr_simple():
    s = "(see 10 (b 0.1 1.2) (p l 7 10 20) (p r 4 12 -30))"
    res = parse.parse_see(s)
    assert res["time"] == "10"
    assert res["ball"] is not None
    assert len(res["players"]) == 2
    assert res["players"][0]["side"] == "l"
