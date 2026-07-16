# Genie One for Energy

Repeatable **Genie One / Databricks One** demo use cases for energy customers,
built on one reusable pattern:

> **One agent, three source types — governed UC tables + a live UC function +
> unstructured docs — on Databricks One with in-region Claude, no vector store.**

Each use case is that template with the connectors swapped for a different
domain (audit, regulatory, risk, retail, finance, …).

## The reusable template

| Layer | Building block | Swappable per use case |
|---|---|---|
| Structured | Genie Agent over UC gold tables | the domain's data |
| Live | UC SQL function → public API via HTTP connection | AEMO / AER / BOM weather / CER / OpenElectricity |
| Unstructured | Docs in a UC Volume or Google Drive | regulations, contracts, policies, reports |
| Governance | UC permissions + lineage, in-region Claude, audit via system tables | (constant) |

## Use cases

| Status | Use case | Persona | Live source | Docs |
|---|---|---|---|---|
| ✅ Built | [`spot-price-demo`](spot-price-demo/) | Trader / market analyst | AEMO live spot price | AEMO QED + fact sheets |
| 🔜 | Regulatory obligation tracker | Compliance / legal | AEMO market notices | AER/AEMC/ESV rule changes |
| 🔜 | Portfolio risk copilot | Risk manager | AEMO live prices | Risk policy / limits |
| 🔜 | Retail bill-explainer | Retail ops / CX | Live wholesale + tariff | AER retail rules, product T&Cs |
| 🔜 | Hedge coverage & MtM | Finance / treasury | AEMO live prices | PPA / hedge contracts |

(See the trading demo for the proven end-to-end pattern; the others reuse its scaffold.)

## Repo layout

```
genie-one-for-energy/
  README.md                     # this file — the template + use-case catalogue
  spot-price-demo/              # use case 1 (built)
    README.md                   # setup instructions
    scripts/                    # config-driven setup (01 data, 02 fn, 03 agent, test)
    docs/                       # AEMO Google Drive docs setup
    sample_questions.md         # single/two/three-source + causal questions
    reference/                  # serialized Genie space reference
```

## Getting started
Start with [`spot-price-demo/README.md`](spot-price-demo/README.md). Each new use
case follows the same 3 scripts + docs pattern.

## Key lessons baked in
- Live external data needs a **table-valued** UC function (so Genie can call it)
  over a UC **HTTP connection** with `bearer_token 'none'` for public APIs.
- Genie attaches functions under `instructions.sql_functions` (not `data_sources`).
- OneChat's Drive connector reads **Google-native docs only** (convert PDFs).
- OneChat **auto-routes** across accessible agents (no pre-question picker) —
  scope with permissions or `force_space_id` for a deterministic demo.
