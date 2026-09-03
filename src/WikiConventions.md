# Wiki Conventions

## Scope and ownership

- This is a local-first knowledge base for research, project, and reading
  notes. Do not file journal, health, financial, or similarly personal material
  without explicit approval.
- The user alone stages, commits, merges, and publishes. Agents inspect and
  preserve uncommitted work before editing, state intended files and changes,
  and leave edits unstaged.
- Nothing from a conversation is filed automatically. Do not browse the web or
  send note content to an external service without explicit permission.
- `diary/` is outside the notebook. Do not read, search, summarize, link, lint,
  or modify it unless the user explicitly asks.
- Stop before incorporating a possible secret or sensitive material and flag it
  for the user.

## Layout and Markdown

- `src/` is the Mkdnflow notebook root; substantive notes and explicit
  subdirectories live there. Root `index.md` and `Inbox.md` are outside the
  notebook graph.
- Use GitHub-Flavored Markdown and `CamelCase.md` names. Every normal note
  starts with one H1, then an optional colon tag on the next line.
- Keep notes small and atomic where practical. Split dense subjects into a
  concise overview and linked detail notes. Purposeful stubs explain why they
  exist and link to the prompting note.
- Do not add front matter, attachments, images, PDFs, opaque IDs, raw-source
  archives, databases, semantic search, or RAG unless explicitly requested.
- Mermaid fenced blocks are allowed.

## Links, moves, and backlinks

- Use standard, current-file-relative Markdown links with explicit `.md`
  targets. Root files may link to `src/Name.md`; notes under `src/` link from
  their own directory.
- Start Neovim from `~/vimwiki/src`. Mkdnflow must use
  `path_resolution.primary = 'current'`; do not configure root-relative
  resolution.
- Use `:MkdnBacklinks` for dynamic backlinks and `:MkdnBacklinksRefresh` after
  command-line edits. Backlinks are never written into notes.
- Use `.agents/scripts/move_note.py` for cross-directory moves. Review its
  default dry-run output; use `--apply` only after review. It supports only
  one-line inline Markdown links with explicit local `.md` targets.
- Run `:MkdnDeadLinks notebook` after a move or during a read-only review.
  Routine checking is local-only; checking external URLs needs permission.

## Tags and quality

- Tags are the only metadata. `Tags.md` is the sole tag registry.
- Initial status tags are `source`, `my-thinking`, `open-question`, and
  `review`. Tags are optional.
- Use `:review:` only when agent-authored material is both extensive and low
  confidence; state the uncertainty and affected files. Remove it only after
  the user accepts or revises the material.
- Express uncertainty in prose or with `:open-question:`. Report conflicting
  notes and discuss them before editing. An associated project repository wins
  for implementation facts.

## Reviews and maintenance

- There is no scheduled or autonomous maintenance.
- “Review the wiki” is a read-only delta review from a user-specified Git
  revision; absent one, compare the current worktree with the last commit.
- Report link issues, persistent orphan candidates, tag issues, contradictions,
  and candidate connections. Do not edit until the user approves.
- A note is an orphan candidate only when it remains unlinked across reviews,
  not when it is new or deliberately standalone.
- Prefer deletion to archives. Before deletion, search inbound links and obtain
  approval for cleanup or retargeting.

## Tooling

- Mkdnflow and Neovim are configured in WSL dotfiles, not this repository.
  Record pinned versions and the Mkdnflow settings in the dotfiles repository.
- Python tooling uses `uv`; `.venv/` is ignored. Tool upgrades are explicit and
  reviewed. Install the repository hooks with `uv run pre-commit install`.
- Markdown is formatted at 80 columns where the formatter can do so safely.
  Native pre-commit hooks format and lint non-diary Markdown, and scan every
  staged file for secrets.
- Secret findings block commits. A false positive may be allowlisted only when
  it is reviewed and demonstrably harmless.
