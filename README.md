# PhiKas Information/Token Sieve (v2.0.0)

An intelligent, token-normalized pipeline built to audit, filter, and model raw streaming system log sequences. By moving away from strict character-matching, the **Token Sieve** dynamically extracts structural metrics and contextually correlates distributed incident markers across isolated timelines.

---

## 🔍 Core Processing Lifecycle

1. **Ingestion & Strict Audit:** Validates raw text payloads against maximum character constraints, catches and logs unformatted anomalies, and isolates exact string duplicates.
2. **Structured Pattern Parsing:** Maps clean rows into structured schema sequences (`date | ticket_id | category | description`) or flags them gracefully as unstructured data with extracted severity markers (e.g., `CRITICAL`, `WARN`).
3. **Timeline Group Modeling:** Organizes active tickets by unique asset IDs and non-destructively sorts individual event chains into strict chronological history tracks.
4. **Token-Normalized Sieve:** Normalizes message descriptions by stripping punctuation and removing common grammatical stop words. It performs a contextual Jaccard-style token intersection check to catch paraphrased, cross-ticket infrastructure events matching a boundary ratio threshold (≥ 0.82).

---

## 📂 Repository Structure

```text
phikas-information-token-sieve/
├── .gitignore                      # Prevents caching, build packages, and local output clutter
├── LICENSE                         # Project distribution terms (MIT License)
├── README.md                       # Main architectural blueprint and usage guide
├── requirements.txt                # System framework dependencies (e.g., pytest)
├── setup.py                        # Python package compilation and distribution config
│
├── phikas_engine/                  # Target distribution package root directory
│   ├── __init__.py                 # Core module exposure initialization
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py               # Optimized v2.0.0 pipeline processing engine
│   └── utils/
│       ├── __init__.py
│       └── token_helpers.py        # Token isolation and keyword stop-dictionaries
│
├── tests/                          # Automated validation testing suites
│   ├── __init__.py
│   └── test_engine.py              # PyTest validation cases for token intersection checks
│
├── notebooks/                      # Development scratchpads and cloud integrations
│   ├── phikas_colab_package.ipynb  # Interactive Google Colab construction package script
│   └── scratchpad_v1_archive.ipynb # Historical v1.3.0 layout for reference tracking
│
├── scripts/                        # Maintenance and operational runner hooks
│   ├── run_console.sh              # Local shell shortcut to spin up text inputs
│   └── deploy.sh                   # Decoupled repository manual push script
│
└── examples/                       # Reference payloads for pipeline verification
    ├── baseline_logs.txt           # Standard diagnostic test lines
    └── sample_output.json          # Expected engine runtime JSON file output
```

---

## ⚙️ Direct Local Setup & Package Installation

You can install this module directly from your workspace directory as an editable package:

```bash
pip install .
```

### Basic Interactive Execution
To launch the interactive chat-style log pasting environment natively, execute the core package interface from your terminal:

```bash
python3 -m phikas_engine.core.engine
```

### Advanced CLI Category Filtering
To filter out specific informational categories or noise domains dynamically on ingestion, leverage the `--ignore` or `-i` flag parameters:

```bash
python3 -m phikas_engine.core.engine logs.txt --ignore INFO METRIC NETWORK
```

