# sparse-city

What should an agent do when the useful answer is hidden, looking costs money, and guessing confidently is worse than saying “I don't know”?

`sparse-city` is a tiny, deterministic environment for that question. An agent can buy a cell or a whole information layer, answer, or abstain. The score charges for information, penalizes wrong answers, and makes abstention visible instead of quietly treating it as failure.

```text
fogged grid → QUERY (priced) / ANSWER / ABSTAIN → scorecard.json
```

## Run the small argument

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

sparse-city demo --seed 42
```

The demo puts three deliberately simple baselines beside each other:

- `wasteful_buyer` purchases an irrelevant hazard layer and still guesses wrong;
- `greedy_abstain` purchases the target land-use cell and answers;
- `threshold_abstain` has too little budget to learn, so it abstains.

For machine-readable output:

```bash
sparse-city eval --agent greedy_abstain --seed 42
sparse-city leaderboard --seed 42
pytest -q
```

The agents are baselines, not trained models. The environment uses explicit dictionary actions rather than pretending to implement a Gymnasium contract it cannot satisfy cleanly.

## A design choice that matters

Early versions made abstention easy to overlook. Here it has its own outcome, cost, scorecard field, and regression test. A timeout is also scored as abstention, so an agent cannot improve its apparent accuracy by wandering forever.

The default world is a generated 3×3 grid. It is intentionally small enough that a reviewer can inspect a complete trajectory. Scaling the grid is less interesting than adding agents that decide whether another query is worth its price.

## Limits

- All places, prices, and layers are synthetic.
- This is a POMDP-like evaluation toy, not a city-planning model.
- Four hand-written baselines are included; no model leaderboard is claimed.
- Reward weights encode one particular preference about the cost of error.

## Research lineage

I worked as a research assistant at SCI-Arc Research from May 2024 to January 2025. This is an independent implementation inspired by questions about partial urban knowledge in *Views of Planet City*, *How Cities See*, *Backyard Home Data Explorer*, and *Multifamily Housing in Somaliland*. It does not reproduce those projects or represent their communities. The original contributors are credited in [ATTRIBUTION.md](ATTRIBUTION.md), with implementation provenance in [PROVENANCE.md](PROVENANCE.md).

MIT — see [LICENSE](LICENSE).
