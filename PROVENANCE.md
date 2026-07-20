# PROVENANCE — sparse-city

**Artifact ID:** `sparse-city`  
**As of:** 2026-07-20  
**Lane:** Build Pod (local MVP)  
**State note:** Swarm control plane may still show pending Human Plan Review; this worktree is an experimental local implementation under the remix card’s BUILD prior-art gate.

## One-sentence promise

Partial-observability planning toy: buy priced observations vs act vs abstain under budget; reproducible abstain-aware scorecard on **synthetic** city grids only.

## Mechanism lineage

| Layer | ID / title | Role |
|---|---|---|
| Source | `views-of-planet-city` | Radical scenario + unit-safe calc *mechanism* (exhibition unused) |
| Source | `how-cities-see` | Incomplete / machine perception of cities (no DTLA LIDAR used) |
| Source | `backyard-home-data-explorer` | Dense third-party data caution → synthetic substitutes |
| Source (mechanism hint) | `multifamily-housing-in-somaliland` | Sparse-context / multi-institution gathering → **abstention as eval idea only** |
| Mechanism | `mech-sparse-data-abstention` | Prefer info-gathering + abstain over overconfident claims |
| Mechanism | `mech-missingness-outside-cleaned-data` | Missingness is first-class, not cleaned away |
| Mechanism | `mech-radical-scenario-unit-safe-calc` | Keep extremes falsifiable via unit-safe scoring |
| Remix | `sparse-city` | POMDP-lite + priced queries + abstain scorecard |

Prefer `source_backed_summary` on source cards over interpretation.

### Ethics (Somaliland / communities)

The Somaliland multifamily research card is cited **only** for the portable idea that sparse local evidence should not license overconfident claims. This MVP:

- does **not** use Somaliland personal data, images, or stakeholder materials
- does **not** speak for Hargeisa residents, partners, or institutions
- does **not** score risk on real people or places
- uses an invented “Toyville” grid instead

## Prior art (differentiation)

Closest academic/tooling overlap (acknowledged; not copied):

- [POPGym](https://doi.org/10.48550/arxiv.2303.01859) — partially observable RL suite
- [Agentic Abstention](https://arxiv.org/pdf/2606.28733) — ANSWER / ABSTAIN / ACT under uncertainty
- Clarification-seeking agent benchmarks — underspecified tasks with info requests

**Differentiation shipped here:** urban/parcel-token partial observability + **priced** information purchase + abstain-aware leaderboard fixtures — not a generic POMDP mega-suite and not an exhibition remount.

## Inputs / outputs of this MVP

- **In:** synthetic grid seed, price table, baseline agent name
- **Out:** scorecard JSON (`accuracy`, `info_cost`, overconfidence / abstain fields), leaderboard JSON
- **Not in:** Planet City exhibition assets, DTLA LIDAR, Zillow/Yelp/Twitter, real personal data

## Attribution

See [ATTRIBUTION.md](./ATTRIBUTION.md) and [CITATION.cff](./CITATION.cff).

**Listed authors (source cards; do not flatten):**

- Views of Planet City — Young, Rehm, Cooper, Chen, Jovanovic, Lorenzi, Mackic
- How Cities See — Bratton, Rehm, Michelon
- Backyard Home Data Explorer — Zeiger, Rehm, Zhang, Munuhoti, Suh, + additional listed contributors
- Multifamily Housing in Somaliland (hint only) — Seehusen, Hupalo, Michelsen, Ali, Panchenko, Dinnerman, Gochnour, Karaosman, Wibowo, Arevalo

- **takeru_role:** unknown  
- **permission_status:** confirmed_by_takeru (audit trail only)  
- **Official SCI-Arc?** No

## Evidence paths (swarm)

- `projects/sciarc-remix-swarm/source-cards/views-of-planet-city.yaml`
- `projects/sciarc-remix-swarm/source-cards/how-cities-see.yaml`
- `projects/sciarc-remix-swarm/source-cards/backyard-home-data-explorer.yaml`
- `projects/sciarc-remix-swarm/source-cards/multifamily-housing-in-somaliland.yaml`
- `projects/sciarc-remix-swarm/remix-cards/sparse-city.yaml`
- `projects/sciarc-remix-swarm/prior-art/sparse-city.yaml`
- `projects/sciarc-remix-swarm/taste/sparse-city.yaml`
- `projects/sciarc-remix-swarm/build-plans/sparse-city.md`
