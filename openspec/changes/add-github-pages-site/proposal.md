# Proposal: Add GitHub Pages Site with Astro Starlight

## Why

The GhostWire project will benefit from a dedicated static site built with Astro Starlight that showcases documentation, lore, and a quick start guide. The site should heavily lean into the over all theme found in GHOSTWIRE/FLAVOR_TEXT and the various style and theme files, creating a cyberpunk, neon-themed experience that embodies the GhostWire aesthetic.

## What Changes

- Create a static web app using Astro Starlight with cyberpunk/neon aesthetic
- Add a `site/` directory with source files that incorporate the GhostWire themes, lore, and flavor
- Configure build scripts in `package.json` to support Astro Starlight
- Add GitHub Actions workflow to publish to `gh-pages` branch
- Create content that includes the project lore, documentation, and quick start guides

## Impact

- A new `static-site` capability will appear in `openspec/specs/static-site/spec.md`.
- No changes to existing APIs or runtime services.
- The site will use Astro Starlight with a cyberpunk/neon theme reflecting the GhostWire aesthetic
- Site will feature the GhostWire lore, operator guides, and technical documentation
