---
name: process-inbox
description: Process this vimwiki repository's inbox when the user asks to "process the inbox", "file the inbox", "clear the inbox", or asks to turn an inbox item into a wiki note. Use this skill for every inbox-filing request in this repository, including a request naming a particular inbox file.
---

# Process Inbox

Turn explicit inbox captures into concise, well-connected notes without
changing the user's existing work or treating the inbox as a dumping ground.

## Source of truth

Before inspecting or editing inbox content, read the applicable `AGENTS.md`
files and then read `src/WikiConventions.md` in full. The conventions govern
this workflow; do not duplicate, reinterpret, or override them here.

The inbox is outside the notebook graph. The notebook root is `src/`.

## Workflow

1. Inspect `git status --short` before editing. Preserve all pre-existing
   changes. State the files you expect to add, edit, move, or remove before
   making changes.
2. List direct files in `inbox/` and read only the items that the user asked to
   process. Do not inspect `diary/`.
3. Triage each item independently:
   - Stop and ask the user before filing personal, health, financial, secret,
     or otherwise sensitive material.
   - If it is ambiguous, contradictory, or lacks enough context to file
     responsibly, leave it in the inbox and explain what is needed.
   - Do not browse or send note content to external services unless the user
     explicitly authorizes it.
4. Search `src/` for direct, useful connections and duplicate notes. Do not
   force links. If notes conflict, report the conflict and wait for direction.
5. File the item as a normal note under the most appropriate `src/`
   subdirectory. Use a descriptive `CamelCase.md` name, one H1, optional
   registered tags, current-file-relative Markdown links with explicit `.md`
   targets, and no front matter.
6. Keep the filed note atomic and concise. Preserve the source URL and the
   key idea or actionable guidance; summarize rather than reproduce long
   source material. A source note will ordinarily fit in roughly 15–35 lines.
   Split only when the capture contains genuinely separate durable ideas.
7. Delete the inbox item only after its destination note has been created and
   reviewed. Do not add backlinks to notes. Use the repository's move utility
   only for moves wholly within `src/`, following its dry-run requirement.
8. Verify the resulting diff for whitespace and formatting issues, check that
   new local Markdown links resolve, and report what was filed, left behind,
   or flagged. Leave all changes unstaged.

## Filing judgment

- Prefer a new note when the capture has a durable concept, source, or
  playbook that would be hard to find if buried in another note.
- Prefer adding a short section to an existing note when it contributes only a
  small, clearly subordinate detail.
- Use only tags registered in `src/Tags.md`; topic tags are optional.
- Mark agent-authored material with `:review:` only when it is both extensive
  and low confidence, and state the uncertainty in the note.
- Preserve the user's wording where it is their analysis. Clearly distinguish
  it from a source summary when that matters.

## Response

Lead with the result. Name the filed notes, remaining inbox files, and any
material left for user review. Mention validation performed and that changes
remain unstaged. Do not claim that an external source was verified unless it
was actually checked with permission.
