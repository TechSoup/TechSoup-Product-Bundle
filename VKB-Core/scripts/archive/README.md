# Archive Scripts

This directory contains legacy or one-time utility scripts that have been superseded by the current VKB-Core architecture.

## ⚠️ Warning
These scripts should **not** be run on the current codebase as they may overwrite data or use outdated naming conventions (like generic `README.md` instead of `[slug]_README.md`).

## Contents
- **compile_catalog_cli.py:** Legacy regex-based catalog compiler. Superseded by `compile_catalog.py`.
- **update_yaml.py:** One-time migration script for injecting `max_budget` fields.
- **update_agent_personas.py:** Template application script. **Dangerous:** Running this will overwrite custom expert knowledge in agent skills.
- **swarm_discovery.py:** Mock lead generator used during initial registry testing.
