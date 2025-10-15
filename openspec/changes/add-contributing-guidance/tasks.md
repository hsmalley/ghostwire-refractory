<!-- OPENSPEC:START -->
# Tasks: add-contributing-guidance

- id: 1
  title: Draft CONTRIBUTING.md
  owner: @hsmalley
  estimate: 0.25h
  description: |
    Create `CONTRIBUTING.md` at repo root. Include Purpose, Where to use the flavor, When to avoid it, Emoji/log opt-out example, Simple run instructions, and links to theme/flavor files.

- id: 2
  title: Add README link
  owner: @hsmalley
  estimate: 0.05h
  description: |
    Add a one-line pointer under Development Setup in `README.md` linking to `CONTRIBUTING.md`.

- id: 3
  title: Review & land PR
  owner: Maintainers
  estimate: 0.1h
  description: |
    Open a small PR, request review from maintainers, and land once approved. Confirm CI is green.

- id: 4
  title: (Optional) Implement logger opt-out
  owner: @hsmalley
  estimate: 0.5h
  description: |
    If desired, add env var (`GHOSTWIRE_NO_EMOJI`) handling into logging configuration so emoji/ANSI output can be disabled. Add a unit test verifying behavior.

<!-- OPENSPEC:END -->
