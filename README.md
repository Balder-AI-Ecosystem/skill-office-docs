# skill-office-docs

Standalone office document skill repo for meeting-note summarization and office document composition.

## Responsibility

This repo owns the office document boundary. Core should discover and execute it only through the shared skill contract.

Capabilities declared in `skill.yaml`:

- `office_docs.meeting_notes_summary`
- `office_docs.compose_document`

## Contract

- Mode: `local_plugin`
- Entrypoint: `src.skill_office_docs.main:Skill`
- Healthcheck: `src.skill_office_docs.main:healthcheck`
- Core API compatibility: `>=1.0,<2.0`

## Permissions

- `external_actions: false`
- `internet_access: false`
- `file_write: false`
- `read_memory: false`
- `write_memory: false`

## Integration rule

Core integration must stay at the skill boundary defined by `skill.yaml`. Core should not import document builders or summarizers from this repo directly.
## Verification

- Recommended command: `python -m pytest -q`
- Current minimum coverage: manifest and contract smoke tests inside `tests/`

## Implementation status

This repo currently wraps legacy office-document behavior behind the skill boundary. The repo is acceptable for the current extraction stage because the contract is explicit and independently testable.

Current dependency note: the runtime path still resolves the core repo location, so implementation independence is not complete yet.