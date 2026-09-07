# Local-first Markdown wiki

A small, Git-backed notebook for research, project, and reading notes. The
repository keeps notes as ordinary Markdown files and is intended to work well
with Neovim and Mkdnflow/vimwiki.

## Personal wiki

## Layout

- [inbox/new.md](inbox/new.md) is the default unstructured capture buffer.
  Process entries only when explicitly requested.
- [Diary/](diary/) is an optional list of daily notes that can be used as an
  alternative to the inbox.
- [Wiki conventions](src/WikiConventions.md) is the rules set to help maintain
  and scale the wiki.
- [src/](src/) is the Mkdnflow notebook root and contains substantive notes.
- [src/Tags.md](src/Tags.md) defines the available note-status tags.
- [src/README.md](src/README.md) is the human-maintained starting point.

## Working with notes

Start Neovim from `src/` so Mkdnflow resolves links relative to the current
note. Use GitHub-Flavored Markdown, give normal notes a single H1 heading, and
use `CamelCase.md` filenames. Links should be current-file-relative and include
their `.md` extension.

The full note, link, privacy, and maintenance rules are in
[WikiConventions.md](src/WikiConventions.md). Read them before contributing or
automating changes.

## Branch workflow

The `init` branch on GitHub is the shared reference starting point. Create a
local `main` branch from `github/init` for an actual wiki, then push that branch
to a personal remote. This keeps the public reference separate from the
working notebook and its history.

```bash
git switch -c main github/init
git remote add origin <your-remote-url>
git push -u origin main
```

Then merge upstream changes (if any) with:

```bash
git pull github init  # while on main
```
