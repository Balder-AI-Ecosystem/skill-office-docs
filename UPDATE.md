# UPDATE PLAN — skill-office-docs

> Audit date: 2026-04-21 | Grade: **C** | Priority: High

---

## Vấn đề tìm thấy

### 1. Schemas chưa khai báo properties (CRITICAL)
2 capabilities đều dùng schema rỗng.

### 2. `dependencies = []` — gây hiểu nhầm
Khai báo rỗng nhưng thực tế phụ thuộc `OfficeAssistantModule` từ core.

### 3. Test coverage tối thiểu
Chỉ manifest check. Không có functional tests.

### 4. Chỉ 2 capabilities — có thể thiếu
Hiện có `office_docs.create_doc` và `office_docs.search_doc`. Thực tế người dùng cũng cần `read_doc` (đọc nội dung doc), `update_doc` (sửa).

---

## Fix cần làm

### Fix 1 — Cập nhật schemas trong skill.yaml

```yaml
# office_docs.create_doc
input_schema:
  type: object
  required: [title]
  properties:
    title:
      type: string
      description: "Document title"
    content:
      type: ["string", "null"]
      description: "Initial content (markdown or plain text)"
    template:
      type: ["string", "null"]
      description: "Template name or ID to use"
    folder_id:
      type: ["string", "null"]
      description: "Drive folder ID to save to. Null = My Drive root."
    dry_run:
      type: boolean
      default: false
    confirmed:
      type: boolean
      default: false
    confirmation_token:
      type: ["string", "null"]
  additionalProperties: false
output_schema:
  type: object
  required: [status]
  properties:
    status:
      type: string
      enum: [ok, error, preview, confirmation_required]
    doc_id: {type: ["string", "null"]}
    doc_url: {type: ["string", "null"]}
    title: {type: ["string", "null"]}
    preview: {type: object}
    confirmation_token: {type: ["string", "null"]}
    detail: {type: ["string", "null"]}

# office_docs.search_doc
input_schema:
  type: object
  required: [query]
  properties:
    query:
      type: string
      description: "Search query (full text or filename)"
    folder_id:
      type: ["string", "null"]
      description: "Scope search to a specific folder"
    max_results:
      type: integer
      default: 10
      maximum: 50
    file_types:
      type: array
      items: {type: string}
      default: []
      description: "Filter by MIME type (e.g. ['application/vnd.google-apps.document'])"
  additionalProperties: false
output_schema:
  type: object
  required: [status]
  properties:
    status:
      type: string
      enum: [ok, error, empty]
    docs:
      type: array
      items:
        type: object
        properties:
          id: {type: string}
          title: {type: string}
          url: {type: string}
          modified_at: {type: string}
          owner: {type: string}
    total: {type: integer}
```

### Fix 2 — Cân nhắc thêm capabilities còn thiếu

Thêm vào skill.yaml (sau khi implement):

```yaml
  - id: office_docs.read_doc
    description: Read the content of a document.
    input_schema:
      type: object
      required: [doc_id]
      properties:
        doc_id: {type: string}
        format:
          type: string
          enum: [markdown, plain_text, html]
          default: markdown
      additionalProperties: false
    output_schema:
      type: object
      required: [status]
      properties:
        status: {type: string}
        title: {type: ["string", "null"]}
        content: {type: ["string", "null"]}
        word_count: {type: integer}
    risk_level: low
    confirmation_required: false
    retry_policy: bounded_backoff
```

### Fix 3 — Sửa pyproject.toml

```toml
[project]
# Depends on OfficeAssistantModule from core ecosystem.
# Core must be on sys.path (injected by JARVIS loader).
dependencies = []  # runtime: ecosystem.domains.office (injected)
```

### Fix 4 — Thêm functional tests

```python
# tests/test_execute.py
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
```

---

## Không cần làm
- `OfficeAssistantModule` delegation pattern đúng
- Không cần thay đổi permissions
- `create_doc` là destructive action — `confirmation_required: true` đúng rồi
