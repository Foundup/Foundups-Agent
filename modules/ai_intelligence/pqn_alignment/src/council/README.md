# Council Roles & Scoring (Stub)

Roles / Biases
- ModelA: maximize PQN (seek high pqn_per_1k)
- ModelB: minimize paradox (seek low paradox_per_1k)
- ModelC: alternation explorer (encourage &^# patterns)

Scoring (aggregate)
- score = 3*pqn - 2*paradox + 1.5*res_hits + robustness_bonus + novelty_bonus
- Robustness: low variance across seeds
- Novelty: Jaccard distance from prior top scripts

Config
```yaml
roles:
  - name: ModelA
    bias: maximize PQN
  - name: ModelB
    bias: minimize paradox
  - name: ModelC
    bias: alternation explorer
```
