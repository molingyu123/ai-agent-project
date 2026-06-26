from agents.supervisor import SupervisorAgent


def test_supervisor_heuristic_routes_legacy_sync():
    agent = SupervisorAgent()

    assert agent._heuristic_route("同步老系统数据") == "legacy"


def test_supervisor_heuristic_routes_analysis():
    agent = SupervisorAgent()

    assert agent._heuristic_route("分析项目趋势") == "analyzer"


def test_supervisor_heuristic_defaults_to_rag():
    agent = SupervisorAgent()

    assert agent._heuristic_route("这个制度是什么意思") == "retriever"
