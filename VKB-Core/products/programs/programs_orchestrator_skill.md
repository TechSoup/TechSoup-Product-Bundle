---
type: orchestrator
title: Programs Category Orchestrator
description: Programs Category Orchestrator — maintains this category's VKB product entries.
---

# Programs Category Orchestrator
This agent is responsible for the overall integrity and maintenance of all **Programs** product entries in the VKB.

## Responsibilities
- **Swarm Management**: Delegate maintenance tasks to individual program-focused product agents (e.g., Salesforce, Bonterra).
- **Registry Oversight**: Monitor `offers_registry.csv` for new program management tools. When a new tool is identified, initialize its folder structure and register its product agent.
- **Integrity**: Aggregate status reports from sub-agents to ensure program entry data is correct.
- **Reporting**: Evaluate category-wide impacts on nonprofit program delivery and long-term sustainability.
