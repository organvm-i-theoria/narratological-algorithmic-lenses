> **ORGAN-I: Theory** · [organvm-i-theoria](https://github.com/organvm-i-theoria) · *Narratological Algorithmic Lenses*

[![ORGAN-I: Theory](https://img.shields.io/badge/ORGAN--I-Theory-1a237e?style=flat-square)](https://github.com/organvm-i-theoria)
[![Python](https://img.shields.io/badge/python-≥3.11-blue?style=flat-square)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?style=flat-square)]()
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

# Narratological Algorithmic Lenses

**Formalizing narrative principles from master storytellers into executable algorithms.**

14 narratological studies. 79 axioms. 92 algorithms. A full-stack analysis system — CLI, REST API, and web dashboard — that transforms centuries of storytelling craft into structured, computable knowledge, then proves itself against real creative material.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Core Concepts](#core-concepts)
- [Related Work](#related-work)
- [Installation & Usage](#installation--usage)
- [Examples](#examples)
- [Downstream Implementation](#downstream-implementation)
- [Validation](#validation)
- [Roadmap](#roadmap)
- [Cross-References](#cross-references)
- [Contributing](#contributing)
- [License](#license)
- [Author & Contact](#author--contact)

---

## Problem Statement

Narrative theory is rich but scattered. Aristotle's *Poetics* sits in philosophy departments, Pixar's story rules circulate as informal listicles, Tarkovsky's temporal theories live in film criticism, and Tolkien's mythopoetic principles are buried in literary scholarship. Each tradition has distilled genuine structural insight about how stories work — but those insights remain trapped in prose, inaccessible to computational analysis, and disconnected from one another.

This project asks a concrete question: **what happens when you treat narrative principles not as literary commentary but as formal algorithms?** When Aristotle's reversal-recognition pattern becomes a function signature? When Tarkovsky's "sculpting in time" becomes a measurable temporal-density metric? When Pixar's emotional engineering becomes a diagnostic you can run against an actual screenplay?

The answer is a system that bridges literary theory and software engineering in a way that neither field has attempted at this scale. Not "AI that writes stories" — that flattens the problem. Instead: a compendium of formalized narrative knowledge that can analyze, diagnose, and map the structural DNA of any narrative work, drawing simultaneously on traditions spanning 2,400 years of storytelling craft.

The gap this fills is specific. Existing computational narrative tools either operate at the surface level (sentiment analysis, word frequency) or impose a single framework (the Hero's Journey, three-act structure). Narratological Algorithmic Lenses provides **92 distinct analytical algorithms** derived from **14 different storytelling traditions**, enabling multi-framework analysis that respects the genuine diversity of narrative thought.

---

## Core Concepts

### The Compendium Model

The system's intellectual architecture is a three-layer hierarchy: **Compendium > Study > Axiom/Algorithm/Diagnostic Question**. Each of the 14 narratological studies extracts principles from a specific master storyteller or tradition, decomposes those principles into axioms (irreducible claims about narrative), then derives algorithms (executable procedures) and diagnostic questions (analytical prompts) from those axioms.

The entire compendium is stored in dual form: human-readable Markdown studies for close reading, and a unified JSON structure (209 KB) for programmatic access. The Pydantic data models enforce schema consistency across all 14 studies, ensuring that every axiom carries provenance, every algorithm has defined inputs and outputs, and every diagnostic question links back to its source axiom.

### Seven Sequence Pairs

The 14 studies are not arbitrary. They are organized into **7 Sequence Pairs** — deliberate pairings of storytellers chosen for comparative friction:

| Pair | Theme | Storytellers |
|------|-------|-------------|
| **A** | Anthology & Myth-Remix | Ovid + Neil Gaiman |
| **B** | Cinematic Interiority | Andrei Tarkovsky + Ingmar Bergman |
| **C** | Formalism vs. Hypersigil | Alan Moore + Grant Morrison |
| **D** | Mythopoeia | Jack Kirby + J.R.R. Tolkien |
| **E** | Interactive Narrative | Zelda/Nintendo + Final Fantasy/Square Enix |
| **F** | Non-Linear Masters | Quentin Tarantino + Ovid |
| **G** | Emotional Engineering | Pixar + Final Fantasy |

Each pair generates insights that neither storyteller alone would produce. Tarkovsky's temporal sculpting gains precision when measured against Bergman's chamber-drama compression. Moore's formalist panel grids reveal their full implications only when contrasted with Morrison's reality-bleeding hypersigils. The pairing structure is itself a research methodology — comparative narratology as a generative engine.

### Algorithm Execution Engine

Algorithms are not metaphors here. Each of the 92 algorithms is registered in an execution engine with a defined interface: input narrative material, apply the algorithm's analytical procedure, produce structured output. The engine supports chaining (apply Aristotle's reversal detection, then pipe results into Pixar's emotional-arc mapper), filtering (run only algorithms from Sequence Pair B), and coverage analysis (which algorithms have been applied to a given work, and which remain).

The execution engine integrates with LLM providers (Anthropic Claude, OpenAI, Ollama for local inference, plus a MockProvider for deterministic testing) through an 8-role analyst system. Each role — Aesthete, Dramaturgist, Narratologist, Art Historian, Cinephile, Rhetorician, Producer, Academic — applies a distinct analytical lens, preventing the homogenization that occurs when a single prompt template drives all analysis.

### Report Generation

The system produces three primary report types:

- **Beat Maps**: Structural decomposition using 15 function types (inciting incident, progressive complication, crisis, climax, resolution, and 10 additional granular beat types). Beat maps reveal the skeletal architecture of a narrative — where it accelerates, where it pauses, where it reverses.
- **Character Atlases**: Relational maps of character function, tracking not just who appears but what narrative role each character serves across the full taxonomy of the compendium's axioms.
- **Coverage Reports**: Gap analysis showing which algorithms and diagnostic questions have been applied to a given work, highlighting blind spots in any single-framework analysis.

---

## Related Work

**Computational narratology** as a field has produced tools like Mark Finlayson's *Analogical Story Merging* system, the *Story Workbench* annotation platform, and various narrative-generation systems (Meehan's TALE-SPIN, Turner's MINSTREL, Pérez y Pérez's MEXICA). These operate primarily as story generators or annotation tools within a single theoretical framework.

**Digital humanities** platforms like Voyant Tools, CATMA, and the Stanford Literary Lab's Pamphlets series apply computational methods to literary texts, but focus on linguistic and statistical features rather than narrative-structural algorithms.

**Screenwriting software** (Final Draft, WriterSolo, StoryO) provides structural templates but not multi-framework analytical diagnostics.

Narratological Algorithmic Lenses differs from all three lineages in its emphasis on **formalization across traditions**. It does not generate stories, annotate corpora, or template screenplays. It formalizes the *analytical knowledge* embedded in 14 distinct storytelling traditions and makes that knowledge executable against any narrative input.

---

## Installation & Usage

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python workspace manager)
- Node.js 18+ and npm (for the web dashboard)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/organvm-i-theoria/narratological-algorithmic-lenses.git
cd narratological-algorithmic-lenses

# Install Python packages (uv workspace)
uv sync

# Install web dashboard dependencies
cd packages/web && npm install && cd ../..

# Verify installation
narratological --help
```

### CLI Overview

The `narratological` CLI exposes 5 command groups:

```bash
# Browse the compendium
narratological study list                    # List all 14 studies
narratological study show tarkovsky          # Display a specific study
narratological algorithm list --pair B       # List algorithms from Sequence Pair B

# Analyze a narrative work
narratological analyze beats manuscript.md   # Generate beat map
narratological analyze characters script.md  # Generate character atlas
narratological analyze coverage work.json    # Run coverage report

# Run diagnostics
narratological diagnose structural draft.md  # Structural diagnostic
narratological diagnose causal draft.md      # Causal-chain diagnostic

# Generate reports
narratological generate report --format md --output analysis/
```

### API Server

```bash
# Start the FastAPI backend
cd packages/api
uvicorn main:app --reload

# Endpoints available at http://localhost:8000/docs
# GET  /studies          — List all studies
# GET  /studies/{id}     — Study detail with axioms and algorithms
# POST /analyze/beats    — Beat map analysis
# POST /diagnose         — Run diagnostic suite
```

### Web Dashboard

```bash
cd packages/web
npm run dev
# Dashboard at http://localhost:5173
# Components: StudyExplorer, AlgorithmViewer, DiagnosticRunner
```

---

## Examples

### Exploring the Compendium

```python
from narratological.core import Compendium

compendium = Compendium.load()

# Access all axioms across all studies
for study in compendium.studies:
    print(f"{study.name}: {len(study.axioms)} axioms, {len(study.algorithms)} algorithms")

# Filter by sequence pair
pair_b = compendium.get_pair("B")  # Tarkovsky + Bergman
for algo in pair_b.algorithms:
    print(f"  [{algo.id}] {algo.name}: {algo.description}")
```

### Running a Diagnostic

```python
from narratological.core import DiagnosticRunner
from pathlib import Path

runner = DiagnosticRunner(provider="anthropic")  # or "openai", "ollama"

# Structural diagnostic using Aristotelian framework
result = runner.run_structural(
    text=Path("screenplay.md").read_text(),
    frameworks=["aristotle", "pixar", "tarkovsky"]
)

print(result.summary)
for finding in result.findings:
    print(f"  [{finding.framework}] {finding.category}: {finding.detail}")
```

### Beat Map Generation

```python
from narratological.core import ReportGenerator

generator = ReportGenerator()
beat_map = generator.beat_map(
    text=Path("act_one.md").read_text(),
    function_types="all"  # All 15 beat function types
)

for beat in beat_map.beats:
    print(f"  {beat.position:>5} | {beat.function_type:<25} | {beat.description}")
```

---

## Downstream Implementation

This repository provides the theoretical and analytical foundation for creative work across the ORGAN system:

- **ORGAN-II (Poiesis)**: Generative art and performance projects consume the algorithm registry to drive narrative-aware procedural generation. The beat-map output format is designed for direct integration with interactive narrative engines.
- **ORGAN-III (Ergon)**: Commercial storytelling tools (screenwriting assistants, narrative consultants) draw on the diagnostic suite as a backend analytical service.
- **ORGAN-V (Logos)**: The public-process essay series documents the system's development, including reflections on what formalization reveals (and conceals) about storytelling craft.

The dependency direction is strictly **I → II → III** — downstream organs consume the compendium and analytical engine; they never modify it. This ensures the theoretical layer remains stable and independently verifiable.

---

## Validation

### Self-Application: The Open View Case Study

The system's strongest validation is its application to real creative material. The repository includes a complete analysis of **"Open View"** — an original screenplay — across 2 drafts, using the system's own analytical protocols. This case study comprises 32 documents:

- **P7 Comprehensive Analyses**: Full multi-framework analysis using all 14 study lenses
- **Protocol Worksheets**: Structured analysis using Fleabag, Curb Your Enthusiasm, and South Park narrative frameworks
- **Genre Multiplicity Analysis**: Demonstrating how the system handles works that resist single-genre classification
- **Mythological Mapping**: Applying Sequence Pair D (Kirby + Tolkien) mythopoetic algorithms to contemporary material

The case study is not a toy example. It demonstrates the system operating at production scale on material that did not exist when the algorithms were formalized — proving that the compendium generalizes beyond its source traditions.

### Technical Validation

- **Schema enforcement**: All 14 studies validate against Pydantic models (strict mode)
- **Algorithm registry**: 92 algorithms registered with unique IDs, input/output type signatures, and provenance chains
- **Dual-format consistency**: Markdown studies and JSON compendium are generated from the same source, preventing drift
- **LLM provider parity**: MockProvider enables deterministic testing; all providers implement the same interface

---

## Roadmap

- [ ] **Silver tier**: Expand usage examples with annotated walkthroughs of each Sequence Pair
- [ ] **Gold tier**: API documentation (OpenAPI spec), contributor guide, architectural decision records
- [ ] **Compendium expansion**: Additional studies (David Lynch study exists in draft; Warren Ellis study in progress)
- [ ] **Visualization layer**: D3.js-powered algorithm dependency graphs and cross-study axiom networks in the web dashboard
- [ ] **Export formats**: PDF report generation, LaTeX academic paper templates, Fountain screenplay integration
- [ ] **Benchmark suite**: Standardized narrative test corpus for measuring diagnostic accuracy across providers

---

## Cross-References

| Resource | Link |
|----------|------|
| ORGAN-I: Theory | [organvm-i-theoria](https://github.com/organvm-i-theoria) |
| ORGAN-II: Art | [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) |
| ORGAN-III: Commerce | [organvm-iii-ergon](https://github.com/organvm-iii-ergon) |
| ORGAN-IV: Orchestration | [organvm-iv-taxis](https://github.com/organvm-iv-taxis) |
| ORGAN-V: Public Process | [organvm-v-logos](https://github.com/organvm-v-logos) |
| System Registry | [registry-v2.json](https://github.com/organvm-iv-taxis/agentic-titan) |

---

## Contributing

This repository is part of a coordinated multi-organ system. Contributions are welcome, particularly:

- **New narratological studies**: Propose a storyteller or tradition, draft axioms and algorithms following the existing study template, and submit as a PR.
- **Algorithm implementations**: The execution engine accepts new algorithm registrations; see `packages/core/engine/` for the registration interface.
- **Diagnostic improvements**: Bug reports and accuracy improvements for structural and causal diagnostics.
- **Web dashboard features**: React component contributions for the StudyExplorer, AlgorithmViewer, and DiagnosticRunner.

Please open an issue before starting significant work to discuss scope and alignment with the compendium's editorial standards.

---

## License

[MIT](LICENSE)

---

## Author & Contact

**[@4444J99](https://github.com/4444J99)**

Part of the [ORGAN system](https://github.com/organvm-i-theoria) — a creative-institutional architecture coordinating theory, art, commerce, orchestration, public process, community, and marketing across eight GitHub organizations.
