> **ORGAN-I: Theoria** · [organvm-i-theoria](https://github.com/organvm-i-theoria) · *Narratological Algorithmic Lenses*

[![ORGAN-I: Theoria](https://img.shields.io/badge/ORGAN--I-Theoria-311b92?style=flat-square)](https://github.com/organvm-i-theoria)
[![Python](https://img.shields.io/badge/python-≥3.11-blue?style=flat-square)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?style=flat-square)]()
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

# Narratological Algorithmic Lenses

[![CI](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses/actions/workflows/ci.yml/badge.svg)](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-pending-lightgrey)](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses/blob/main/LICENSE)
[![Organ I](https://img.shields.io/badge/Organ-I%20Theoria-8B5CF6)](https://github.com/organvm-i-theoria)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses)
[![Python](https://img.shields.io/badge/lang-Python-informational)](https://github.com/organvm-i-theoria/narratological-algorithmic-lenses)


**Formalizing narrative principles from master storytellers into executable algorithms.**

14 narratological studies. 79 axioms. 92 algorithms. A full-stack analysis system — CLI, REST API, and web dashboard — that transforms centuries of storytelling craft into structured, computable knowledge, then proves itself against real creative material.

---

## Table of Contents

- [Theoretical Purpose](#theoretical-purpose)
- [Philosophical Framework](#philosophical-framework)
- [Core Concepts](#core-concepts)
- [Technical Architecture](#technical-architecture)
- [Installation & Quick Start](#installation--quick-start)
- [CLI Reference](#cli-reference)
- [API Server](#api-server)
- [Web Dashboard](#web-dashboard)
- [Code Examples](#code-examples)
- [The Open View Case Study](#the-open-view-case-study)
- [Primary Sources & Study Corpus](#primary-sources--study-corpus)
- [Cross-Organ References](#cross-organ-references)
- [Related Work](#related-work)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author & Contact](#author--contact)

---

## Theoretical Purpose

Narrative theory is rich but scattered. Aristotle's *Poetics* sits in philosophy departments, Pixar's story rules circulate as informal listicles, Tarkovsky's temporal theories live in film criticism, and Tolkien's mythopoetic principles are buried in literary scholarship. Each tradition has distilled genuine structural insight about how stories work — but those insights remain trapped in prose, inaccessible to computational analysis, and disconnected from one another.

This project asks a concrete question: **what happens when you treat narrative principles not as literary commentary but as formal algorithms?** When Aristotle's reversal-recognition pattern becomes a function signature? When Tarkovsky's "sculpting in time" becomes a measurable temporal-density metric? When Pixar's emotional engineering becomes a diagnostic you can run against an actual screenplay?

The answer is a system that bridges literary theory and software engineering in a way that neither field has attempted at this scale. Not "AI that writes stories" — that flattens the problem. Instead: a compendium of formalized narrative knowledge that can analyze, diagnose, and map the structural DNA of any narrative work, drawing simultaneously on traditions spanning 2,400 years of storytelling craft.

### The Gap This Fills

Existing computational narrative tools either operate at the surface level (sentiment analysis, word frequency) or impose a single framework (the Hero's Journey, three-act structure). Narratological Algorithmic Lenses provides **92 distinct analytical algorithms** derived from **14 different storytelling traditions**, enabling multi-framework analysis that respects the genuine diversity of narrative thought. The system does not flatten Bergman into Campbell or reduce Tarkovsky to McKee. Each tradition retains its own axioms, its own algorithms, its own diagnostic questions — and the system's power comes from their deliberate juxtaposition.

---

## Philosophical Framework

### Narrative Theory Meets Computation

The intellectual premise of this project sits at the intersection of three fields that rarely communicate:

**Narratology** — the structural study of narrative — provides the theoretical substance. From Aristotle's identification of *peripeteia* (reversal) and *anagnorisis* (recognition) through Genette's taxonomy of narrative time to McKee's scene-level craft mechanics, narratology has accumulated a vast inventory of structural observations about how stories function. But these observations are almost exclusively expressed in natural language, making them resistant to systematic comparison and impossible to execute.

**Software engineering** — specifically, the discipline of formalizing procedures into executable specifications — provides the methodological bridge. An algorithm is a precisely specified procedure that transforms defined inputs into defined outputs. When Tarkovsky says that cinema is "sculpting in time," that metaphor becomes an algorithm when you specify: *given a sequence of scenes with measurable durations, compute the temporal density gradient and identify zones of dilation and compression*. The formalization does not reduce the insight; it makes the insight testable.

**Computational epistemology** — the study of what knowledge becomes when it is made computable — provides the philosophical context. This project is not merely a software tool. It is an experiment in whether aesthetic and structural knowledge can survive formalization without losing the qualities that make it knowledge. Every axiom in the compendium carries this double burden: it must be faithful to its source tradition *and* precise enough to generate executable procedures.

### Why Formalization Matters

The act of formalizing a narrative principle is itself an act of analysis. When you attempt to convert Pixar's "once upon a time / every day / one day / because of that / until finally" into a function with typed inputs and outputs, ambiguities in the original principle become visible. Does "every day" describe the protagonist's routine or the audience's expectations? Is "because of that" a causal link within the story or a perceived causal link in the viewer's mind? The algorithm forces these questions into the open.

This is the core methodology: **formalization as interrogation**. The 79 axioms and 92 algorithms in the compendium are not transcriptions of existing theory — they are the products of a systematic interrogation of 14 storytelling traditions, conducted through the discipline of trying to make those traditions execute.

---

## Core Concepts

### The Compendium Model

The system's intellectual architecture is a three-layer hierarchy: **Compendium → Study → Axiom / Algorithm / Diagnostic Question**. Each of the 14 narratological studies extracts principles from a specific master storyteller or tradition, decomposes those principles into axioms (irreducible claims about narrative), then derives algorithms (executable procedures) and diagnostic questions (analytical prompts) from those axioms.

The entire compendium is stored in dual form: human-readable Markdown studies for close reading, and a unified JSON structure (209 KB) for programmatic access. Pydantic data models enforce schema consistency across all 14 studies, ensuring that every axiom carries provenance, every algorithm has defined inputs and outputs, and every diagnostic question links back to its source axiom.

### Seven Sequence Pairs

The 14 studies are organized into **7 Sequence Pairs** — deliberate pairings of storytellers chosen for comparative friction:

| Pair | Theme | Storytellers |
|------|-------|-------------|
| **A** | Anthology & Myth-Remix | Ovid + Neil Gaiman |
| **B** | Cinematic Interiority | Andrei Tarkovsky + Ingmar Bergman |
| **C** | Formalism vs. Hypersigil | Alan Moore + Grant Morrison |
| **D** | Mythopoeia | Jack Kirby + J.R.R. Tolkien |
| **E** | Interactive Narrative | Zelda / Nintendo + Final Fantasy / Square Enix |
| **F** | Non-Linear Masters | Quentin Tarantino + Ovid |
| **G** | Emotional Engineering | Pixar + Final Fantasy |

Each pair generates insights that neither storyteller alone would produce. Tarkovsky's temporal sculpting gains precision when measured against Bergman's chamber-drama compression. Moore's formalist panel grids reveal their full implications only when contrasted with Morrison's reality-bleeding hypersigils. The pairing structure is itself a research methodology — comparative narratology as a generative engine.

### Algorithm Execution Engine

Algorithms are not metaphors here. Each of the 92 algorithms is registered in an execution engine with a defined interface: input narrative material, apply the algorithm's analytical procedure, produce structured output. The engine supports three execution modes:

- **Analyze** — Apply an algorithm to existing narrative text and produce structured findings, element identification, and a 0–1 alignment score.
- **Generate** — Use an algorithm's logic to produce new narrative content that embodies its principles.
- **Validate** — Check whether a given text satisfies an algorithm's criteria, returning pass/fail results per criterion with confidence scores.

The engine supports chaining (apply Aristotle's reversal detection, then pipe results into Pixar's emotional-arc mapper), filtering (run only algorithms from Sequence Pair B), and coverage analysis (which algorithms have been applied to a given work, and which remain).

### LLM Integration: The 8-Role Analyst System

The execution engine integrates with LLM providers (Anthropic Claude, OpenAI, Ollama for local inference, plus a MockProvider for deterministic testing) through an **8-role analyst system**. Each role applies a distinct analytical lens:

| Role | Focus |
|------|-------|
| **Aesthete** | Form, beauty, style, sensory patterns |
| **Dramaturgist** | Structure, rhythm, dramatic tension |
| **Narratologist** | Narrative mechanisms, causal binding |
| **Art Historian** | Historical context, influences, lineages |
| **Cinephile** | Comparable works, genre conventions |
| **Rhetorician** | Argument structure, dialogue craft |
| **Producer** | Practical feasibility, budget implications |
| **Academic** | Theoretical frameworks, scholarly rigor |

This multi-perspective architecture prevents the homogenization that occurs when a single prompt template drives all analysis. A scene analyzed by the Dramaturgist surfaces structural concerns; the same scene through the Aesthete lens reveals sensory patterns invisible to structural analysis.

### Report Types

The system produces three primary report types:

- **Beat Maps**: Structural decomposition using 15 function types (inciting incident, progressive complication, crisis, climax, resolution, and 10 additional granular beat types). Beat maps track tension levels (1–10 scale) and scene connectors (BUT, THEREFORE, AND THEN, MEANWHILE) to reveal the skeletal architecture of a narrative — where it accelerates, where it pauses, where it reverses.
- **Character Atlases**: Relational maps of character function, tracking not just who appears but what narrative role each character serves across the full taxonomy of the compendium's axioms.
- **Coverage Reports**: Gap analysis showing which algorithms and diagnostic questions have been applied to a given work. Includes logline generation, synopsis, six-axis ratings (Premise, Structure, Character, Dialogue, Originality, Marketability on a 0–10 scale), strengths/weaknesses, and a recommendation classification (CONSIDER, PASS, DEVELOP, URGENT).

---

## Technical Architecture

```
narratological-algorithmic-lenses/
├── specs/                          # Theoretical specifications
│   ├── 01-primary-sources/         # Aristotle, McKee, Bharata Muni, Horace, Plato
│   ├── 02-completed-studies/       # 14 Markdown narratological studies
│   ├── 03-structured-data/         # 14 JSON extracts + unified compendium (209 KB)
│   ├── 04-templates/               # Beat map, character, coverage, diagnostic templates
│   ├── 05-secondary-sources/       # Extended analyses (Larry David, Waller-Bridge, etc.)
│   ├── 06-open-view-drafts/        # Original screenplay drafts (validation corpus)
│   └── 07-skill-documentation/     # 8-role analyst methodology (SKILL.md)
│
├── open-view-analysis/             # Complete case study (32 documents)
│   ├── first-draft/                # P7 analysis, 13 supplementary reports
│   ├── second-draft/               # Revised analysis, critique report
│   └── protocol-worksheets/        # Fleabag, Curb, South Park protocols
│
├── packages/
│   ├── core/                       # Python core (Pydantic models, algorithms, diagnostics)
│   │   └── src/narratological/
│   │       ├── algorithms/         # ExecutableAlgorithm, AlgorithmRegistry
│   │       ├── diagnostics/        # Structural, Causal, Framework diagnostics
│   │       ├── generators/         # CoverageReport, BeatMap generators
│   │       ├── models/             # Pydantic data models (Study, Algorithm, Report)
│   │       ├── llm/               # Provider abstraction (Anthropic, OpenAI, Ollama, Mock)
│   │       └── loader.py          # Compendium loader from unified JSON
│   ├── cli/                        # Typer CLI (study, algorithm, analyze, diagnose, generate)
│   ├── api/                        # FastAPI REST backend (studies, analysis, diagnostics)
│   └── web/                        # React + TypeScript + Vite dashboard
│       └── src/components/         # StudyExplorer, AlgorithmViewer, DiagnosticRunner
│
├── pyproject.toml                  # Python workspace root (uv)
└── package.json                    # Node.js workspace root
```

### Dependency Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data models | Pydantic 2.6+ (strict mode) | Schema enforcement across 14 studies |
| Core library | Python 3.11+ | Algorithm registry, diagnostic framework, report generation |
| CLI | Typer + Rich | Terminal interface with formatted tables and progress bars |
| API | FastAPI + Uvicorn | REST endpoints with automatic OpenAPI documentation |
| Web | React 18 + TypeScript 5.6 + Vite | Interactive study explorer and diagnostic dashboard |
| LLM providers | anthropic, openai, ollama | Multi-provider analysis with MockProvider for testing |
| NLP (optional) | spaCy 3.7+ | Local linguistic analysis without LLM dependency |
| Build | uv (Python) + npm (TypeScript) | Workspace-aware package management |

---

## Installation & Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python workspace manager)
- Node.js 18+ and npm (for the web dashboard)

### Install

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

### Quick Start: Explore the Compendium

```bash
# List all 14 studies
narratological study list

# Show a specific study with its axioms and algorithms
narratological study show tarkovsky

# List algorithms from Sequence Pair B (Tarkovsky + Bergman)
narratological algorithm list --pair B

# Search algorithms by keyword
narratological algorithm search "temporal"
```

### Quick Start: Analyze a Script

```bash
# Full coverage report with beat map
narratological analyze script manuscript.md --reports all --provider anthropic

# Single scene analysis
narratological analyze scene "INT. KITCHEN - NIGHT. Sarah finds the letter." --provider ollama

# Batch analysis of an entire directory
narratological analyze batch ./scripts/ --pattern "*.txt" --output ./reports/
```

---

## CLI Reference

The `narratological` CLI exposes 5 command groups:

| Command Group | Description |
|--------------|-------------|
| `study` | Browse and inspect the 14 narratological studies |
| `algorithm` | List, search, filter, and execute individual algorithms |
| `analyze` | Full script analysis (coverage, beat map, scene, batch, compare) |
| `diagnose` | Run structural, causal, and framework-specific diagnostics |
| `generate` | Generate narrative structures using algorithm logic |

Key flags available across commands:

```bash
--provider, -p    # LLM provider: anthropic, openai, ollama (default: ollama)
--model, -m       # Model override (e.g., claude-sonnet-4-20250514, gpt-4o, llama3.1)
--base-url        # Custom API endpoint for self-hosted models
--output, -o      # Output directory for generated reports
--framework, -f   # Primary narratological framework to apply
--verbose, -v     # Enable verbose output
```

---

## API Server

```bash
# Start the FastAPI backend
cd packages/api
uvicorn narratological_api.main:app --reload

# Interactive docs at http://localhost:8000/docs
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/studies` | List all 14 studies with metadata |
| `GET` | `/studies/{id}` | Full study detail with axioms, algorithms, diagnostics |
| `GET` | `/stats` | Compendium statistics (study count, axiom count, algorithm count) |
| `POST` | `/analysis/beats` | Generate beat map for submitted text |
| `POST` | `/analysis/coverage` | Generate coverage report |
| `POST` | `/diagnostics/structural` | Run structural diagnostic |
| `POST` | `/diagnostics/causal` | Run causal-chain diagnostic |
| `POST` | `/diagnostics/framework` | Run framework-specific diagnostic questions |
| `GET` | `/health` | Health check |

The API loads the compendium at startup via the FastAPI lifespan handler, ensuring all 14 studies are available in memory for every request.

---

## Web Dashboard

```bash
cd packages/web
npm run dev
# Dashboard at http://localhost:5173
```

Three primary components:

- **StudyExplorer** — Browse all 14 studies, view axioms and algorithms, navigate sequence pairs
- **AlgorithmViewer** — Inspect individual algorithms: purpose, pseudocode, inputs/outputs, provenance chain
- **DiagnosticRunner** — Submit text and run diagnostic suites with real-time results

---

## Code Examples

### Exploring the Compendium Programmatically

```python
from narratological.loader import load_compendium

compendium = load_compendium()

# Iterate all studies
for study_id, study in compendium.studies.items():
    print(f"{study.creator}: {len(study.axioms)} axioms, "
          f"{len(study.core_algorithms)} algorithms")

# Access a specific study
tarkovsky = compendium.get_study("tarkovsky")
for axiom in tarkovsky.axioms:
    print(f"  [{axiom.id}] {axiom.name}: {axiom.statement}")
```

### Using the Algorithm Registry

```python
from narratological.algorithms.registry import AlgorithmRegistry

registry = AlgorithmRegistry()

# List all algorithms from a specific study
for algo in registry.list_by_study("pixar"):
    print(f"  {algo.name}: {algo.purpose}")

# Search across all studies
temporal_algos = registry.search("temporal")
print(f"Found {len(temporal_algos)} algorithms related to 'temporal'")

# Get algorithm counts per study
for study_id, count in registry.count_by_study().items():
    print(f"  {study_id}: {count} algorithms")
```

### Running an Algorithm Against Text

```python
from narratological.algorithms.registry import AlgorithmRegistry
from narratological.llm.providers import get_provider

registry = AlgorithmRegistry()
llm = get_provider("anthropic")  # or "openai", "ollama"

# Get a specific algorithm
algo = registry.get("tarkovsky", "temporal_density")

# Analyze narrative text
result = algo.analyze(
    text=open("screenplay.md").read(),
    llm=llm,
)

print(f"Score: {result.score:.2f}")
for finding in result.findings:
    print(f"  - {finding}")
```

### Running Framework Diagnostics

```python
from narratological.diagnostics.framework import FrameworkDiagnostic
from narratological.llm.providers import get_provider
from narratological.loader import load_compendium

compendium = load_compendium()
llm = get_provider("anthropic")

diagnostic = FrameworkDiagnostic(provider=llm, compendium=compendium)

# Run diagnostics against Bergman + Tarkovsky frameworks
issues = diagnostic.run(
    context=my_script_context,
    study_ids=["bergman", "tarkovsky"],
)

for issue in issues:
    print(f"  [{issue.severity}] {issue.description}")
    if issue.recommendation:
        print(f"    -> {issue.recommendation}")
```

---

## The Open View Case Study

The system's strongest validation is its application to real creative material. The repository includes a complete analysis of **"Open View"** — an original screenplay — across 2 drafts, using the system's own analytical protocols. This case study comprises **32 documents** organized into three analysis layers:

### First Draft Analysis (13 documents)
Full P7 comprehensive analysis using all 14 study lenses: coverage report, beat map, structural analysis, character atlas, thematic architecture, diagnostic report, theoretical correspondence mapping, revision roadmap, and five supplementary reports (production notes, comparative analysis, dialogue analysis, visual grammar, market positioning).

### Protocol Worksheets (8 documents)
Structured analysis using protocols derived from three additional storytelling traditions — Fleabag (Phoebe Waller-Bridge's "three things going on" technique), Curb Your Enthusiasm (Larry David's cascading consequence architecture), and South Park (the "therefore/but" rule). Includes a synthesis matrix, genre multiplicity extension, genre architecture worksheet, meta-genre container analysis, and mythological mapping.

### Second Draft Analysis (12 documents)
Revised analysis after applying revision roadmap recommendations, plus a critique report and a narratological algorithms report that evaluates how well the second draft responds to the diagnostic findings.

The case study is not a toy example. It demonstrates the system operating at production scale on material that did not exist when the algorithms were formalized — proving that the compendium generalizes beyond its source traditions.

---

## Primary Sources & Study Corpus

### Ancient & Classical Sources

The `specs/01-primary-sources/` directory contains the foundational texts that ground the compendium's theoretical claims:

- **Aristotle, *Poetics*** — The origin of Western narrative theory. Peripeteia, anagnorisis, hamartia, catharsis.
- **Bharata Muni, *Natyasastra*** — The Sanskrit treatise on dramatic arts. Rasa theory (the eight aesthetic flavors of emotional experience).
- **Horace, *Ars Poetica*** — Roman craft theory. In medias res, decorum, the dulce et utile principle.
- **Plato, *Republic*** — The philosophical challenge to mimesis. Censorship, ideal forms, the allegory of the cave.
- **Robert McKee, *Story*** — Contemporary screenwriting craft at the scene level. The gap between expectation and result.

### The 14 Studies

| Study | Creator | Category | Axioms | Algorithms |
|-------|---------|----------|--------|-----------|
| ovid-metamorphoses | Ovid | Classical | 5 | 5 |
| tarkovsky | Andrei Tarkovsky | Film | 6 | 6 |
| bergman | Ingmar Bergman | Film | 6 | 6 |
| alan-moore | Alan Moore | Comics | 7 | 5 |
| morrison | Grant Morrison | Comics | 7 | 5 |
| gaiman-sandman | Neil Gaiman | Comics | 5 | 7 |
| kirby-new-gods | Jack Kirby | Comics | 4 | 5 |
| tolkien | J.R.R. Tolkien | Literature | 4 | 6 |
| zelda | Nintendo | Interactive | 9 | 11 |
| final-fantasy | Square Enix | Interactive | 8 | 10 |
| tarantino | Quentin Tarantino | Film | 6 | 6 |
| pixar | Pixar Studios | Animation | 4 | 8 |
| warren-ellis | Warren Ellis | Comics | 4 | 6 |
| david-lynch | David Lynch | Film | 4 | 6 |

Each study exists in dual form: a human-readable Markdown document (24–45 KB each) for close reading, and a structured JSON extract for programmatic access. The unified compendium JSON (209 KB) aggregates all 14 studies with cross-references and metadata.

---

## Cross-Organ References

This repository provides the theoretical and analytical foundation for creative work across the ORGAN system. The dependency direction is strictly **I -> II -> III** — downstream organs consume the compendium and analytical engine; they never modify it.

| Organ | Relationship | Examples |
|-------|-------------|----------|
| **ORGAN-II: Poiesis** (Art) | Consumes algorithm registry for narrative-aware procedural generation | Beat-map output designed for integration with interactive narrative engines; sequence pair data drives generative art parameterization |
| **ORGAN-III: Ergon** (Commerce) | Draws on the diagnostic suite as a backend analytical service | Screenwriting assistant tools, narrative consulting products, theatre-dialogue analysis pipelines |
| **ORGAN-IV: Taxis** (Orchestration) | Governance and routing | Registry tracks this repo's documentation status and cross-organ dependency declarations |
| **ORGAN-V: Logos** (Public Process) | Documents the system's development | Essays reflecting on what formalization reveals (and conceals) about storytelling craft |

| Resource | Link |
|----------|------|
| ORGAN-I: Theoria | [organvm-i-theoria](https://github.com/organvm-i-theoria) |
| ORGAN-II: Poiesis | [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) |
| ORGAN-III: Ergon | [organvm-iii-ergon](https://github.com/organvm-iii-ergon) |
| ORGAN-IV: Taxis | [organvm-iv-taxis](https://github.com/organvm-iv-taxis) |
| ORGAN-V: Logos | [organvm-v-logos](https://github.com/organvm-v-logos) |
| ORGAN-VI: Koinonia | [organvm-vi-koinonia](https://github.com/organvm-vi-koinonia) |
| ORGAN-VII: Kerygma | [organvm-vii-kerygma](https://github.com/organvm-vii-kerygma) |
| System Registry | [registry-v2.json](https://github.com/organvm-iv-taxis/agentic-titan) |

---

## Related Work

**Computational narratology** as a field has produced tools like Mark Finlayson's *Analogical Story Merging* system, the *Story Workbench* annotation platform, and various narrative-generation systems (Meehan's TALE-SPIN, Turner's MINSTREL, Perez y Perez's MEXICA). These operate primarily as story generators or annotation tools within a single theoretical framework.

**Digital humanities** platforms like Voyant Tools, CATMA, and the Stanford Literary Lab's Pamphlets series apply computational methods to literary texts, but focus on linguistic and statistical features rather than narrative-structural algorithms.

**Screenwriting software** (Final Draft, WriterSolo, StoryO) provides structural templates but not multi-framework analytical diagnostics.

Narratological Algorithmic Lenses differs from all three lineages in its emphasis on **formalization across traditions**. It does not generate stories, annotate corpora, or template screenplays. It formalizes the *analytical knowledge* embedded in 14 distinct storytelling traditions and makes that knowledge executable against any narrative input.

---

## Roadmap

- [ ] Expand usage examples with annotated walkthroughs of each Sequence Pair
- [ ] API documentation (OpenAPI spec), contributor guide, architectural decision records
- [ ] Additional studies (David Lynch study exists in draft; Warren Ellis study in progress; Kubrick primary-source research complete)
- [ ] D3.js-powered algorithm dependency graphs and cross-study axiom networks in the web dashboard
- [ ] PDF report generation, LaTeX academic paper templates, Fountain screenplay integration
- [ ] Standardized narrative test corpus for measuring diagnostic accuracy across providers
- [ ] spaCy integration for local NLP analysis without LLM dependency

---

## Contributing

This repository is part of a coordinated multi-organ system. Contributions are welcome, particularly:

- **New narratological studies**: Propose a storyteller or tradition, draft axioms and algorithms following the existing study template in `specs/04-templates/`, and submit as a PR.
- **Algorithm implementations**: The execution engine accepts new algorithm registrations; see `packages/core/src/narratological/algorithms/` for the registration interface.
- **Diagnostic improvements**: Bug reports and accuracy improvements for structural, causal, and framework diagnostics.
- **Web dashboard features**: React component contributions for the StudyExplorer, AlgorithmViewer, and DiagnosticRunner.
- **Primary source research**: Additional source texts and secondary analyses for the `specs/` corpus.

Please open an issue before starting significant work to discuss scope and alignment with the compendium's editorial standards.

---

## License

[MIT](LICENSE)

---

## Author & Contact

**[@4444J99](https://github.com/4444J99)**

Part of the [ORGAN system](https://github.com/meta-organvm) — a creative-institutional architecture coordinating theory, art, commerce, orchestration, public process, community, and marketing across eight GitHub organizations.
