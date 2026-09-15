# Investment Research Copilot — Architecture Blueprint

## 1. Goal

Build a research copilot that takes a stock ticker (HOSE/HNX) and produces a disciplined, source-backed investment memo with:

- clean financial history
- company and industry research
- data auditing and reconciliation
- counter-argument / rebuttal agent
- valuation and sensitivity analysis
- explicit thesis gaps and assumptions
- exportable research deck

The system must assist the analyst, not decide for them.

---

## 2. Core principle

The product should be designed around a causal chain:

industry -> catalyst -> backlog / revenue -> profit / FCF -> valuation

Every conclusion must trace back to evidence and time.

---

## 3. High-level workflow

1. Input ticker
2. Collect raw data from public sources and filings
3. Normalize & audit data
4. Build company profile
5. Build industry map
6. Generate thesis hypotheses
7. Run evidence and rebuttal agents
8. Run valuation models
9. Produce dashboard and export artifacts

---

## 4. System components

### 4.1 Data Acquisition Layer

Responsibilities:

- Fetch financial statements: BCTC, audited annual reports, quarterly reports
- Collect market/industry data: revenue mix, backlog, capex, macro indicators
- Capture official and second-source references
- Store source metadata: title, URL, date, source type, page section, last accessed

Core modules:

- ticker resolver
- financial fetcher
- annual report crawler
- press / investor relations parser
- source registry

### 4.2 Data Normalization Layer

Responsibilities:

- standardize metric names
- convert units and currency
- map Vietnamese accounting lines to canonical metrics
- normalize year and quarter labels
- remove duplicate rows and noise

Canonical metrics:

- revenue
- EBITDA
- EBIT
- net profit
- operating cash flow
- free cash flow
- capex
- debt
- net debt
- current assets / liabilities
- equity
- ROE / ROA / ROIC
- gross margin / EBITDA margin
- working capital

### 4.3 Data Auditor Layer

This is essential.

Responsibilities:

- detect mismatch between sources
- flag duplicate records
- detect unit mismatch (VND vs millions vs billions)
- detect year mismatch or quarter mismatch
- compare audited vs unaudited numbers
- highlight impossible changes or sign reversals
- mark uncertainty if source is unofficial or stale

Example checks:

- revenue trend vs segment breakdown
- net profit vs cash flow trend
- debt growth vs equity growth
- capex vs depreciation relationship
- audited balance sheet vs investor presentation reconciliation

Outputs:

- audit log
- exception list
- confidence score per metric
- source confidence matrix

### 4.4 Company Research Layer

Responsibilities:

- summarize company history and strategy
- analyze business segments
- detect revenue concentration and risk
- review growth drivers and margin structure
- map management comments to numbers
- identify catalyst events and key operating KPIs

Typical evidence sources:

- annual reports
- investor presentations
- earnings releases
- press release / management guidance
- industry reports

### 4.5 Industry Research Layer

Responsibilities:

- identify industry structure and competitive position
- collect company peer set
- compare operating metrics
- map supply-demand and regulation
- assess macro drivers
- investigate cyclical or secular trends

Outputs:

- industry overview
- peer comparison table
- macro scenarios
- catalysts and risks

### 4.6 Thesis & Counterfactual Layer

This is the “mentor / critic” layer.

Responsibilities:

- take a thesis from user or generated from detected catalysts
- split into evidence for and against
- challenge assumptions
- find missing links
- ask what must be true for thesis to hold
- trace causal chain from industry to outcome

Recommended agents:

- Evidence Finder
- Data Integrity Agent
- Counterargument Agent
- Risk Agent
- Valuation Assumption Checker
- Thesis Gap Detector

Each agent should output:

- claim
- evidence
- source
- date
- confidence
- rebuttal or caveat

### 4.7 Valuation Layer

Allowed models:

- DCF / FCFF
- FCFE
- P/E
- EV / EBITDA
- P/B
- peer comparison

Rules:

- no hidden assumption
- every assumption must be explicit and traceable
- user-specified inputs remain user-owned
- model outputs show sensitivity and scenario ranges

### 4.8 Reporting Layer

Responsibilities:

- assemble dashboard and narrative
- generate Excel outputs
- generate PDF / slide-ready presentation
- produce evidence tables with source links

Dashboard sections:

- Financial Data
- Company Research
- Industry Research
- Investment Thesis
- Bull / Bear Case
- Risks
- Thesis Gaps
- Valuation
- Sources

---

## 5. Data model

### 5.1 Tables

- raw_source
- source_reference
- company
- ticker
- financial_statement
- statement_metric
- metric_alias
- audit_issue
- thesis_claim
- evidence_item
- valuation_input
- valuation_result

### 5.2 Key concepts

- source_id
- ticker
- fiscal_year
- fiscal_quarter
- metric_name
- value
- unit
- currency
- source_type
- source_url
- accessed_at
- confidence_score
- is_audited
- is_reconciled

---

## 6. Agent design

### 6.1 Research Agent

Collects facts and structure them by topic.

### 6.2 Data Auditor Agent

Checks metrics for quality and consistency.

### 6.3 Company/Industry Analyst Agent

Builds narrative and explains operating dynamics.

### 6.4 Thesis Critic Agent

Finds counter-evidence and weak assumptions.

### 6.5 Valuation Analyst Agent

Builds valuation with explicit assumptions.

### 6.6 Synthesis Agent

Writes the final investment memo with evidence references and unanswered questions.

---

## 7. Recommended architecture stack

- Python
- Pandas / Polars
- SQLAlchemy / DuckDB
- requests + Playwright + BeautifulSoup
- openpyxl / xlsxwriter
- Streamlit for dashboard
- optional LangGraph or custom orchestration
- PDF / slide export via reportlab / pptx

---

## 8. Implementation roadmap

### Phase 1: Data foundation

- ticker intake
- raw source collection
- financial statement normalization
- source metadata table
- audit checks

### Phase 2: Research engine

- company overview
- segment analysis
- peer comparison
- industry structure
- catalysts and risks

### Phase 3: Critique engine

- thesis decomposition
- evidence for/against
- assumption challenge
- causal chain validation

### Phase 4: Valuation engine

- DCF / FCFF / FCFE
- multiples
- peer comparison
- scenario analysis

### Phase 5: Output layer

- dashboard
- Excel export
- PDF / presentation export

---

## 9. Minimum viable “research copilot” version

1. User inputs a ticker.
2. System downloads 5–10 years of financial statement tables.
3. System normalizes the metrics into a clean DataFrame.
4. System audits the metrics for anomalies.
5. System creates a succinct company and industry summary.
6. System asks for or uses user assumptions.
7. System evaluates a thesis with support and rebuttal.
8. System runs valuation and outputs a dashboard.

This is the right MVP scope.

---

## 10. Non-negotiable UX rules

- no silent AI conclusion without evidence
- no assumption without label
- no valuation without source or explicit user override
- every fact must include source and date
- every thesis must include evidence + rebuttal + uncertainty
- output should be decision support, not decision replacement

---

## 11. Suggested first delivery

Build a backend-first MVP with these modules:

- ticker intake
- data acquisition
- financial normalization
- data auditing
- thesis engine
- valuation pane
- dashboard export

This can be shipped in stages without pretending to solve the full research stack at once.

---

## 12. Recommended final product promise

“Enter a stock code, and the system researches the company, challenges the thesis, audits the data, values the business, and provides evidence-backed outputs for the investor to decide.”
