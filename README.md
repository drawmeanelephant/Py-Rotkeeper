# Py-Rotkeeper

![Patch](rc/rotkeeper/sources/images/mascot.png)

Py-Rotkeeper is a modular Python pipeline for content rendering, log rotation, and project scaffolding. It replaces scattered scripts with a **central CONFIG-driven structure**, multi-site safe workflow, and modular CLI commands.

## Short Description

Okay this whole thing is AI slopvibecoded and a rewrite of the old rotkeeper for BASH. The writer took a lot bit of liberties about it and honestly the BASH version did pretty much everything this currently does and more… better. It's a work in progress and this bit of text is the only portion of the project not made by ChatGPT with the sporadic advice from Grok and the mascot was cleaned up by Gemini and generated in a Sora video. It's slop on top of slop. Also the project was initially constructed in Codex. Pretty much anything but Claude has touched it.

Py-Rotkeeper simplifies and organizes project pipelines by:

- Modularizing CLI commands under `rc/rotkeeper/lib/`
- Centralizing paths, flags, and settings via `CONFIG`
- Using canonical sources for content, templates, styles, and images
- Supporting incremental rendering with YAML manifests
- Multi-site safe: multiple project folders can co-exist

## Features

- Modular CLI commands (`init`, `render`, `sitemap`, `nav`, etc.)
- CONFIG singleton for consistent paths, flags, and dry-run/debug modes
- Canonical `sources/` folder for reusable templates, SCSS, images, and sample content
- Incremental render with state tracking
- Frontmatter-aware template overrides
- SCSS compilation (Python 3 safe, Bulma deprecation filtered)
- Multi-site safe: everything relative to current working directory
- Dry-run and verbose logging

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/drawmeanelephant/Py-Rotkeeper
```

2. Navigate to the project directory:

```bash
cd Py-Rotkeeper
```

3. Set up a Python virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Use the main CLI entry point:

```bash
python -m rc.rotkeeper.rc <command> [options]
```

Example: Initialize a new project:

```bash
python -m rc.rotkeeper.rc init --project my-site
```

## Directory Structure Overview

```text
rc/
  rotkeeper/
    rc.py            # CLI entry point
    config.py        # Central CONFIG singleton
    lib/             # Modular command scripts
    sources/         # Canonical sources for new projects
      content/       # index.md, sample.md
      templates/     # default.html, rot-doc.html
      styles/        # main.scss, partials
      images/        # mascot.png
```

- `rc/rotkeeper/` contains the main pipeline logic and modular commands.
- `sources/` holds all canonical files for initializing new projects.
- Project folders created with init will replicate this structure under HOME and BONES paths defined in CONFIG.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository  
2. Create a branch for your feature or bugfix  
3. Commit changes with clear messages  
4. Submit a pull request  

Guidelines:

- Follow PEP8 and project style conventions.  
- Include tests for new functionality.  
- Document new commands or changes in the CLI help output.  

## License

This project is licensed under the MIT License.