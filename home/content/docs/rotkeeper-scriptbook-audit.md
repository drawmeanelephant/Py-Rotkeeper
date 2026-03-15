# Rotkeeper Scriptbook Audit

**Scope:** Cleanup and consistency review

## Focus Areas

-   Hard-coded paths that should use rc-env
-   Scripts not relying on rc-utils.sh
-   Duplicate helper logic
-   Minimal behavior-preserving fixes

Scripts are embedded in the Rotkeeper scriptbook between markers:

    <!-- START: path/to/file -->
    ...
    <!-- END: path/to/file -->

The goal of this audit is **consistency improvements without redesigning
the system**.

------------------------------------------------------------------------

# 1. Hard-coded Paths

Several scripts directly reference paths under `bones/` instead of using
environment variables defined by `rc-env`.

## rc-assets.sh

### Issue

    MANIFEST="$ROOT_DIR/bones/asset-manifest.yaml"

### Fix

    --- a/bones/scripts/rc-assets.sh
    +++ b/bones/scripts/rc-assets.sh
    @@
    - MANIFEST="$ROOT_DIR/bones/asset-manifest.yaml"
    + MANIFEST="$BONES_DIR/asset-manifest.yaml"

------------------------------------------------------------------------

### Issue

    mkdir -p "$OUTPUT_ASSET_DIR" "$ARCHIVE_DIR" "$(dirname "$REPORT")"

### Fix

    - mkdir -p "$OUTPUT_ASSET_DIR" "$ARCHIVE_DIR" "$(dirname "$REPORT")"
    + mkdir -p "$OUTPUT_ASSET_DIR" "$ARCHIVE_DIR" "$REPORT_DIR"

------------------------------------------------------------------------

## rc-book.sh

### Issue

    find "$ROOT_DIR"/bones/scripts "$ROOT_DIR"

### Fix

    --- a/bones/scripts/rc-book.sh
    +++ b/bones/scripts/rc-book.sh
    @@
    - find "$ROOT_DIR"/bones/scripts "$ROOT_DIR"
    + find "$BONES_DIR/scripts" "$ROOT_DIR"

------------------------------------------------------------------------

### Issue

    find "$ROOT_DIR/bones/config" "$ROOT_DIR/bones/templates"

### Fix

    --- a/bones/scripts/rc-book.sh
    +++ b/bones/scripts/rc-book.sh
    @@
    - find "$ROOT_DIR/bones/config" "$ROOT_DIR/bones/templates"
    + find "$CONFIG_DIR" "$TEMPLATES_DIR"

------------------------------------------------------------------------

# 2. rc-utils Usage

All scripts source `rc-utils.sh`, but some bypass the helpers it
provides.

## rc-audit.sh

### Issue

Duplicate logging helper:

    log_entry() {
      local level="$1"
      local message="$2"
      echo "[$level] $message"
    }

### Fix

Remove helper and use shared logger.

    --- a/bones/scripts/rc-audit.sh
    +++ b/bones/scripts/rc-audit.sh
    @@
    -log_entry() {
    -  local level="$1"
    -  local message="$2"
    -  echo "[$level] $message"
    -}

Example replacement:

    - log_entry "ERROR" "Missing asset manifest"
    + log "ERROR" "Missing asset manifest"

------------------------------------------------------------------------

## rc-api.sh

### Issue

    check_dependencies

### Fix

    --- a/bones/scripts/rc-api.sh
    +++ b/bones/scripts/rc-api.sh
    @@
    - check_dependencies
    + require_bins curl yq

------------------------------------------------------------------------

# 3. Duplicate Helper Logic

## Timestamp Generation

Common pattern:

    TIMESTAMP=$(date +%Y-%m-%d_%H%M)

If `rc-utils.sh` contains a helper:

    - TIMESTAMP=$(date +%Y-%m-%d_%H%M)
    + TIMESTAMP=$(timestamp)

------------------------------------------------------------------------

## Error Trap Pattern

Examples:

    trap 'trap_err $LINENO' ERR

vs

    trap 'echo "Error on line $LINENO"; exit 1' ERR

### Fix

    --- a/bones/scripts/rc-book.sh
    +++ b/bones/scripts/rc-book.sh
    @@
    -trap 'echo "Error on line $LINENO"; exit 1' ERR
    +trap 'trap_err $LINENO' ERR

------------------------------------------------------------------------

# 4. Logging Initialization

Ensure `init_log` is called early.

    --- a/bones/scripts/rc-audit.sh
    +++ b/bones/scripts/rc-audit.sh
    @@
     source "$(dirname "${BASH_SOURCE[0]}")/rc-utils.sh"
    +init_log "rc-audit"

------------------------------------------------------------------------

# 5. Shell Consistency

Standard safety block:

    set -euo pipefail
    IFS=$'\n\t'

If missing:

     set -euo pipefail
    +IFS=$'\n\t'

------------------------------------------------------------------------

# 6. Summary

  Category                 Count     Notes
  ------------------------ --------- -----------------------------
  Hard-coded paths         4         Mostly `ROOT_DIR/bones/...`
  Duplicate helpers        2         Logging and traps
  Dependency checks        1         `check_dependencies`
  Logging initialization   1         `rc-audit.sh`
  Shell consistency        several   `IFS`, traps

------------------------------------------------------------------------

# 7. Suggested Workflow

Create cleanup branch:

    git checkout -b cleanup/rc-consistency

Affected scripts:

    bones/scripts/rc-api.sh
    bones/scripts/rc-assets.sh
    bones/scripts/rc-audit.sh
    bones/scripts/rc-book.sh

These fixes preserve behavior while improving maintainability.

------------------------------------------------------------------------

# 8. Conclusion

The Rotkeeper scripts are already structurally modular. The issues
identified are minor cleanup opportunities rather than architectural
problems.

Applying these fixes will:

-   remove path duplication
-   standardize logging and traps
-   reduce helper duplication
-   improve maintainability
