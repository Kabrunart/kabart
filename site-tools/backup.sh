#!/usr/bin/env bash
# Rotate the two site backups on GitHub BEFORE changing the live site.
#   backup-older  <- what backup-newest was
#   backup-newest <- the live site (main) right now
# Each backup is a separate branch holding a complete copy of the site.
# Run from the repository root.
set -euo pipefail

git fetch -q origin main
NEWEST=$(git ls-remote --heads origin backup-newest | cut -f1)
MAIN=$(git rev-parse origin/main)

if [ -n "$NEWEST" ] && [ "$NEWEST" != "$MAIN" ]; then
  git fetch -q origin backup-newest
  git push -q --force origin "$NEWEST:refs/heads/backup-older"
fi
git push -q --force origin "$MAIN:refs/heads/backup-newest"

echo "backup-newest -> $(git ls-remote --heads origin backup-newest | cut -c1-7)"
echo "backup-older  -> $(git ls-remote --heads origin backup-older | cut -c1-7)"
