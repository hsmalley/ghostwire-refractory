# Proposal: Add GitHub Pages Site

## Why
The GhostWire project will benefit from a dedicated static site that showcases documentation, lore, and a quick start guide.

## What Changes
- Create a static web app using Vite + MDX.
- Add a `site/` directory with source MDX files.
- Configure build scripts in `package.json`.
- Publish the output to `gh-pages` branch.

## Impact
- A new `static-site` capability will appear in `openspec/specs/static-site/spec.md`.
- No changes to existing APIs or runtime services.