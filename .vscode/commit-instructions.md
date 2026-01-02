# Commit Message Instructions

## General

The guidelines follow the rules given by [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification).

## Subject Line Guidelines

When creating commit messages, please follow these guidelines:

- Use conventional commit format with leading gitmoji: (emoji) type(scope): Description.
- Description: One-line semantic commit message summarizing the change. Be concise, action-oriented language.
- Use types: feat, fix, docs, style, refactor, perf, test, chore, ci.
- Examples for gitmoji usage: feature: ✨, fix: 🐛, refactor: ♻️, style: 💄, docs: 📝, chore: 🎨, test: ✅, etc.
- Include scope when relevant (e.g., api, ui, auth).
- Use imperative mood: 'Add feature' not 'Added feature'.
- Only use "style:" or mention formatting/linting if that's the ONLY change
- Keep subject line under 72 characters.

## Body Guidelines

For additional details, use a well-structured body section.

- Separate subject and body with a blank line.
- Use bullet points (\*) for clarity.
- Summarize the key changes made in this commit, referencing affected files, implemented features, bug fixes, or documentation updates in up to (one sentence per bullet point) ...
  - one bullet point for small to medium changes,
  - two bullet points for medium-large changes,
  - three bullet points for large commits.
  - For very large commits (more than 10 files or more than 150 affected lines of code), up to four bullet points may exceptionally be used.
- For minor changes (in terms of few files and/or changed lines), a body may be emitted.
- Do not add bullet points for trivial changes or if the subject line already covers it.
- Do not repeat the subject line in the body.
- Do not add repeated bullet points for each file. If multiple files contain similar changes, summarize it once in the body.
