# sparse-city

**Experimental local MVP.** Partial-observability planning toy: buy information vs act vs abstain under budget, with a reproducible scorecard.

Independent personal remix — **not** an official SCI-Arc publication. Synthetic city grids only.

See [ATTRIBUTION.md](./ATTRIBUTION.md), [PROVENANCE.md](./PROVENANCE.md), [LIMITATIONS.md](./LIMITATIONS.md), [CITATION.cff](./CITATION.cff).

## Lineage authors (from source cards)

Do not flatten into sole authorship. `takeru_role: unknown`.

- **Views of Planet City:** Liam Young, Casey Rehm, John Cooper, Jennifer Chen, Damjan Jovanovic, Angelica Lorenzi, Namik Mackic
- **How Cities See:** Benjamin Bratton, Casey Rehm, Laure Michelon
- **Backyard Home Data Explorer:** Mimi Zeiger, Casey Rehm, Yundi Zhang, Yashwanth Munuhoti, Saghyun Suh, plus additional listed contributors on the source card
- **Multifamily Housing in Somaliland** (mechanism hint only): Frederik Emil Seehusen, Masha Hupalo, Anders Michelsen, Rashid Ali, Artem Panchenko, Emily Dinnerman, Nicholas Gochnour, Esin Karaosman, Malvin Wibowo, Lance Arevalo — **no** Somaliland personal data; **no** speaking for communities

## Core promise

```text
fogged synthetic city  →  QUERY (priced) / ANSWER / ABSTAIN  →  scorecard JSON
reward ≈ accuracy − λ·info_cost − μ·wrong   (abstain scored, avoids μ)
```

**Ten-second demo:** エージェントが観測タイルを購入し、不確実ならabstainして罰を避ける。

## One-command run

```bash
cd projects/sciarc-remix-swarm/worktrees/sparse-city
chmod +x scripts/run.sh
./scripts/run.sh
```

Or manually:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python scripts/write_golden.py   # first time
pytest -q
python -m sparse_city eval --agent greedy_abstain --fixture seed42
```

Local CI: `./scripts/ci-local.sh`

## Quick CLI

```bash
# Eval one baseline (default seed 42)
python -m sparse_city eval --agent greedy_abstain

# Compare baselines
python -m sparse_city leaderboard --seed 42

# Wasteful buyer vs wiser abstain
python -m sparse_city demo --seed 42
```

Agents: `always_guess`, `wasteful_buyer`, `threshold_abstain`, `greedy_abstain`.

## Layout

| Path | Role |
|---|---|
| `src/sparse_city/env.py` | POMDP-lite synthetic grid + priced queries |
| `src/sparse_city/scoring.py` | Scorecard + abstain kill-gate helpers |
| `src/sparse_city/agents/baselines.py` | Baseline agents |
| `fixtures/episodes/seed42.json` | Synthetic episode fixture |
| `benchmarks/seed42/` | Expected scorecard + leaderboard JSON |
| `tests/` | Pricing, abstain ordering, golden hash, brand lint |

## Ethics / data policy (hard)

- **Synthetic Toyville only** — invented parcels/layers; not a map of any real city
- **No speaking for communities** — this bench does not represent Somaliland (or any) residents, governments, or housing outcomes
- **No real personal data**, no risk scores on real people, no Zillow/Yelp/Twitter, no DTLA LIDAR blobs
- **No Planet City exhibition assets** — mechanism lineage only; not a re-exhibition
- **No GitHub org writes / deploy / PR** from this worktree by default

Lineage note: `mech-sparse-data-abstention` is a portable *evaluation* idea (prefer gathering info / abstaining over overconfident claims under sparse data). It is **not** a claim about any real place.

## Kill conditions

- Abstain not scored → fail
- Maze-only game without abstain metrics → out of scope
- Planet City re-exhibition → kill

## License

MIT — see [LICENSE](./LICENSE).
