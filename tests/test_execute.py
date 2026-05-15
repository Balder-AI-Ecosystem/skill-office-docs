from unittest.mock import MagicMock, patch

def make_req(capability_id, **params):
    req = MagicMock()
    req.capability_id = capability_id
    req.parameters = params
    return req

def test_search_doc_returns_list():
    from src.skill_office_docs.main import Skill
    skill = Skill()
    with patch.object(skill, '_office_module') as mock_office:
        mock_office.search_doc.return_value = {"status": "ok", "docs": [], "total": 0}
        result = skill.execute(make_req("office_docs.search_doc", query="project plan"))
    assert result["status"] == "ok"
    assert isinstance(result["docs"], list)

def test_create_doc_dry_run_returns_preview():
    from src.skill_office_docs.main import Skill
    skill = Skill()
    with patch.object(skill, '_office_module') as mock_office:
        mock_office.create_doc.return_value = {"status": "preview", "preview": {"title": "Test Doc"}}
        result = skill.execute(make_req("office_docs.create_doc", title="Test Doc", dry_run=True))
    assert result["status"] == "preview"
