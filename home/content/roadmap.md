---
title: Py-Rotkeeper Roadmap
description: Development roadmap, status, and goals for the Py-Rotkeeper project.
date: 2024-06-11
---

# Py-Rotkeeper Roadmap

Welcome to the Py-Rotkeeper project roadmap. This document outlines the current status, short-term and long-term goals, and ongoing tasks for the project.

---

## Current Status

- Python rewrite of Rotkeeper CLI is functional.
- Core commands implemented:
  - `init`, `render`, `assets`, `collect-assets`, `book`, `reseed`, `sitemap`, `cleanup-bones`
- Markdown rendering via Pandoc (`render` command) works with manifest output.
- Asset collection and SCSS compilation are operational.
- Dependency management and virtual environment setup documented.

---

## Short-Term Goals

- [ ] Improve documentation and quickstart guides.
- [ ] Ensure all CLI commands have help text and robust error handling.
- [ ] Add comprehensive tests for core commands.
- [ ] Expand asset management features (e.g., asset deduplication).
- [ ] Polish Markdown-to-HTML rendering and template customization.
- [ ] Integrate continuous integration (CI) for basic checks.
- [ ] Review and clean Bulma Sass deprecation warnings and finalize SCSS structure.
- [ ] Implement user feedback collection and bug reporting system.
- [ ] Enhance logging and debugging capabilities.

---

## Medium-Term Goals

- [ ] Implement "book" binding and "reseed" features fully.
- [ ] Add support for custom themes and user-provided templates.
- [ ] Enhance reporting and manifest outputs (e.g., JSON/YAML options).
- [ ] Introduce plugin or extension system for custom commands.
- [ ] Improve performance for large sites or asset collections.
- [ ] Develop automated testing framework for plugins.
- [ ] Support multi-language content and localization features.

---

## Long-Term Goals

- [ ] Web UI for configuration and management.
- [ ] Cloud deployment and backup options.
- [ ] Automated upgrade/migration tools for legacy Rotkeeper data.
- [ ] Internationalization (i18n) and localization (l10n) support.
- [ ] Community-contributed plugin ecosystem.
- [ ] Mobile-friendly interface and management tools.
- [ ] Integration with popular CMS platforms.

---

## Optional / Future Goals

- [ ] Incorporate AI-assisted content generation and editing.
- [ ] Add analytics dashboard for site usage and performance.
- [ ] Support real-time collaboration features.
- [ ] Develop a marketplace for themes and plugins.
- [ ] Provide Docker containers for easy deployment.
- [ ] Explore integration with static site generators like Hugo or Jekyll.

---

## Checklist / To-Do

- [ ] Update and publish user documentation.
- [ ] Create example site and demo content.
- [ ] Write unit and integration tests for each CLI command.
- [ ] Add command to validate project structure.
- [ ] Improve error messages and logging.
- [ ] Document developer setup and contribution guidelines.
- [ ] Tag first alpha release on GitHub.
