import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  output: "static",
  site: "https://ghostwire-refractory.github.io",
  integrations: [
    starlight({
      title: "⚡️ GhostWire Refractory",
      description:
        "A cyber‑punk lattice that whispers in neon, refactored for performance and mystique",
      logo: {
        src: "./src/assets/logo.png",
        alt: "GhostWire Logo",
      },
      social: {
        github: "https://github.com/ghostwire-refractory/ghostwire-refractory",
      },
      sidebar: [
        {
          label: "⚡️ The Wire",
          items: [
            { label: "Overview", link: "/" },
            { label: "Neon Oracle", link: "/neon-oracle/" },
            { label: "Quick Start", link: "/quickstart/" },
          ],
        },
        {
          label: "📚 The Codex",
          items: [
            { label: "API Reference", link: "/api/" },
            { label: "Architecture", link: "/architecture/" },
            { label: "Benchmarks", link: "/benchmarks/" },
          ],
        },
        {
          label: "🔮 The Undercity",
          items: [
            { label: "Lore", link: "/lore/" },
            { label: "Manifesto", link: "/manifesto/" },
            { label: "Operator Manual", link: "/operator/" },
          ],
        },
      ],
      customCss: ["./src/styles/custom.css"],
      lastUpdated: true,
      editLink: {
        baseUrl:
          "https://github.com/ghostwire-refractory/ghostwire-refractory/edit/main/site/src/content/docs/",
      },
    }),
  ],
});
