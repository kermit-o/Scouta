from app.planning_agent import plan
def test_plan_has_steps():
    p = plan("demo")
    assert "steps" in p and len(p["steps"]) >= 3
