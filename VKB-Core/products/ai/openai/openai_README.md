---
title: OpenAI for Nonprofits
type: offer
x-civic:
  profile: civic/0.5
  status: ACTIVE
  category: AI
  sub_category: General
  alias:
    - Chatgpt
  relations:
    - target: anthropic
      type: alternative
      note: comparable general-purpose LLM assistant; pick one
  offer:
    type: Discount
    summary: Discounted ChatGPT Team & Enterprise
    badges:
      - Discount
  eligibility:
    eligible_audiences:
      - nonprofit
    regions:
      - ALL
    pcs_subject:
      - ALL
    min_budget: 0
  provenance:
    source: TechSoup VKB
    vendor_url: https://help.openai.com/en/articles/9359041-openai-for-nonprofits
    last_audited: '2026-05-16'
---
## Level 1 (Quick Glance)

OpenAI for Nonprofits provides reduced pricing on their premium AI workspaces. Nonprofits can access ChatGPT Team at $20/month per user (discounted from $30) or receive custom discounts on ChatGPT Enterprise for large deployments, enabling secure usage of advanced GPT models.

## Level 2 (Detailed Eligibility Matrix)

- Open to 501(c)(3) nonprofits globally.
- Academic and healthcare organizations may have distinct access channels.
- Requires applying through the OpenAI portal and verifying status via TechSoup or Percent.

## Level 3 (Implementation & Maintenance Requirements)

- **Technical Prerequisites:** None for ChatGPT Team. API access requires software development resources.
- **IT Expertise Required:** Low for the chat interface; High for custom API integrations.
- **Maintenance Overhead:** Low. Managing users in the admin console is straightforward.

### Embedded Parameters

- **Security Posture:** Enterprise and Team tiers are SOC2 compliant and offer SSO.
- **AI Functionality:** The core product is generative AI. Crucially, on the Team and Enterprise tiers, OpenAI **does not** train its foundational models on customer workspace data by default.
- **Long-Term Sustainability:** Medium. While the discount is helpful, per-user pricing can quickly scale for large organizations. The zero-retention data policies are excellent for maintaining donor privacy.

## Alternatives

- [Anthropic (Claude) for Nonprofits](anthropic_README.md) — a substitute general-purpose assistant.
