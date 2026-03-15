---
title: "Quickstart Guide for Rotkeeper"
author: "draw me an elephant"
date: 2026-03-15
tags: [quickstart, tutorial]
toc: true
---

# Quickstart Guide for Rotkeeper

## Requirements Setup

Before using Rotkeeper, make sure your environment is properly set up.

### Create a Virtual Environment

```bash
python3 -m venv venv
```

### Activate the Virtual Environment

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### Upgrade pip, setuptools, and wheel

```bash
pip install --upgrade pip setuptools wheel
```

### Install Python Dependencies

Install all required Python packages from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Optional: Install Pandoc System Binary

Rotkeeper may require Pandoc for certain rendering features. Install Pandoc using your system package manager or download it from the [Pandoc website](https://pandoc.org/installing.html).

For example, on macOS with Homebrew:

```bash
brew install pandoc
```

On Ubuntu/Debian:

```bash
sudo apt-get install pandoc
```

> **Note:** Rotkeeper requires Python 3.7 or higher.

## Installing Dependencies

After activating the virtual environment, install Rotkeeper and its dependencies.

To install the latest released version from PyPI:

```bash
pip install rotkeeper
```

Alternatively, to install the package in editable mode for development:

```bash
pip install -e .
```

## Running Rotkeeper Commands

You can run Rotkeeper commands using the `rotkeeper` CLI tool.

### Show Help

To see all available commands and options:

```bash
rotkeeper --help
```

### Initialize a New Project

To initialize a new Rotkeeper project:

```bash
rotkeeper init
```

### Render Rotations

To render rotations based on your configuration:

```bash
rotkeeper render
```
