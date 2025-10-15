<!-- OPENSPEC:START -->

# Design: Static Site Implementation

## Architecture Pattern

The static site follows an Astro Starlight-based architecture with the following components:

- **Frontend Framework**: Astro Starlight for documentation site generation
- **Theming**: Custom CSS with neon/cyberpunk aesthetic
- **Content Management**: MDX files in src/content/docs/
- **Deployment**: GitHub Actions to gh-pages branch

## Components Design

### Astro Configuration

- **Framework**: Astro v4 with Starlight integration
- **Routing**: File-based routing from src/content/docs/
- **Styling**: Custom CSS with CSS variables for theme consistency
- **Navigation**: Configured sidebar with themed sections

### Themed Styling System

- **Color Palette**: Deep purples, magentas, and glowing accents
- **Effects**: Neon glow effects using CSS text-shadows and box-shadows
- **Typography**: Monospace fonts for terminal-like aesthetic
- **Backgrounds**: Grid patterns and gradient effects for cyberpunk feel

### Content Organization

- **Structure**: Organized into thematic sections matching GhostWire lore
- **Navigation**: Hierarchical sidebar matching "The Wire", "The Codex", "The Undercity"
- **Styling**: Each page maintains consistent aesthetic while serving specific purpose

## Integration Design

The static site integrates with the existing GhostWire ecosystem:

- Uses the same thematic language and concepts as the codebase
- Incorporates GhostWire lore from GHOSTWIRE/FLAVOR_TEXT files
- Maintains visual consistency with the cyberpunk aesthetic
- Provides documentation that complements the runtime services

## Security Considerations

- Static site generation prevents server-side vulnerabilities
- Client-side scripts are limited to Astro Starlight functionality
- No authentication required for documentation access
- Content is sanitized during build process

## Performance Considerations

- Static asset optimization during build
- Minimal JavaScript for enhanced performance
- Efficient bundling and compression
- CDN delivery via GitHub Pages

## Extensibility Considerations

- New documentation pages can be added by creating MDX files
- Theme can be updated by modifying CSS variables
- Navigation can be extended by updating the sidebar configuration
- Content structure supports both technical and thematic documentation

<!-- OPENSPEC:END -->
