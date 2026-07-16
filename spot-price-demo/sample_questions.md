# Demo questions — NEM spot price / trading intelligence

Grouped by how many of the three sources they exercise:
**live** (`get_live_nem_price`), **history** (Genie tables), **docs** (AEMO reports in Drive).

## Single source (baseline / warm-up)
- Live: "What's the current spot price in SA1?"
- History: "Show the top 5 price spikes in NSW1 this week."
- History: "What's the average generation by fuel type in VIC1 over the last week?"
- Docs: "Per the AEMO QED Q1 2026 report, what drove wholesale prices and what share did batteries set?"

## Two sources — live vs history (the "two tools, one agent" moment)
- "Is SA1's live spot price above or below its 7-day average?"
- "Which region has the biggest gap between its live price right now and its 14-day average?"
- "Is current demand in VIC1 higher than its typical demand over the last two weeks?"

## Three sources — live + history + docs
- "What's the live SA1 price right now, how does it compare to its 14-day average in our data, and what does the AEMO QED Q1 2026 report say was driving South Australian prices?"
- "AEMO's Q1 report says batteries set prices in 32% of intervals. Do our own generation and price data show batteries shaping prices this week — and what's the live VIC1 price now?"
- "AEMO reports renewables hit a record 46.5% of generation in Q1 2026. What's the wind+solar share in our data this week, is the live price low right now as we'd expect, and how does that track the report's narrative?"

## Complex + causal ("why did this happen")
- "We had a price spike in NSW1 this week — using the NEM Fact Sheet on how spot prices are set plus the QED price-driver analysis, explain what most likely caused it, and tell me if the live price is anywhere near that level now."
- "We saw negative prices midday in SA1 this week. The QED report attributes daytime lows to solar and battery charging — why did it go negative, does our fuel-mix data confirm solar was the cause, and what's the live price now that we're past midday?"

## Hero question (all three + causal reconciliation, one turn)
> "Right now the live SA1 price is one thing, our 14-day data shows another trend, and AEMO's Q1 2026 report tells a third story about what's driving SA prices. Reconcile all three: is the current market behaving the way the historical data and AEMO's analysis would predict — and if not, why?"

## Demo notes
- The **"why" questions are the highest-variance** — the agent reliably fetches the sources; the causal narrative quality depends on the model. Rehearse phrasing before a live demo.
- `get_live_nem_price` is **single-region per call** — multi-region live questions may only return one region unless the agent iterates.
- The three-source questions only land in **OneChat** (which combines the Genie Agent + Drive docs). Inside the Genie Agent alone, use only the live + history questions.
