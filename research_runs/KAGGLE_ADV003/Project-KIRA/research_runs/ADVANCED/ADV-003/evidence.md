# ADV-003: Adaptive Defense Curve & Anti-Forgetting Evidence Report

## Executive Summary
- **Experiment ID**: `ADV-003`
- **Total Rounds Evaluated**: 10
- **Control Arms**: `static_blue`, `adaptive_challenger`, `replay_control`
- **Baseline Model Substrate**: Authoritative `run_tiny_s20260827_193f7897_40997ab` (Read-only, Unmodified)

## Adaptive Defense Curve Matrix
| Arm | Round | Blue Version | Val ASR | Legacy ASR | Held-Out ASR | Anti-Forgetting Delta | Promotion Decision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| static_blue | 0 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | INITIAL |
| static_blue | 1 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 2 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 3 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 4 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 5 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 6 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 7 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 8 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 9 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| static_blue | 10 | blue_v00_static_blue | 1.0000 | 1.0000 | 1.0000 | 0.0000 | REJECT |
| adaptive_challenger | 0 | blue_v00_adaptive_challenger | 1.0000 | 1.0000 | 1.0000 | 0.0000 | INITIAL |
| adaptive_challenger | 1 | blue_v01_adaptive_challenger | 0.8800 | 1.0000 | 1.0000 | 0.0000 | PROMOTE |
| adaptive_challenger | 2 | blue_v02_adaptive_challenger | 0.8800 | 1.0000 | 0.9200 | 0.0000 | PROMOTE |
| adaptive_challenger | 3 | blue_v03_adaptive_challenger | 0.8800 | 1.0000 | 0.9600 | 0.0000 | PROMOTE |
| adaptive_challenger | 4 | blue_v04_adaptive_challenger | 0.8800 | 0.9600 | 0.9600 | 0.0000 | PROMOTE |
| adaptive_challenger | 5 | blue_v04_adaptive_challenger | 0.9200 | 0.9600 | 0.9600 | 0.0400 | REJECT |
| adaptive_challenger | 6 | blue_v04_adaptive_challenger | 0.9200 | 0.9600 | 0.9600 | 0.0400 | REJECT |
| adaptive_challenger | 7 | blue_v07_adaptive_challenger | 0.7600 | 0.9600 | 0.7600 | 0.0000 | PROMOTE |
| adaptive_challenger | 8 | blue_v08_adaptive_challenger | 0.9200 | 0.9600 | 1.0000 | 0.0000 | PROMOTE |
| adaptive_challenger | 9 | blue_v08_adaptive_challenger | 0.9600 | 0.9600 | 1.0000 | 0.0400 | REJECT |
| adaptive_challenger | 10 | blue_v08_adaptive_challenger | 0.9200 | 0.9600 | 0.9600 | 0.0400 | REJECT |
| replay_control | 0 | blue_v00_replay_control | 1.0000 | 1.0000 | 1.0000 | 0.0000 | INITIAL |
| replay_control | 1 | blue_v01_replay_control | 0.9600 | 1.0000 | 0.9600 | 0.0000 | PROMOTE |
| replay_control | 2 | blue_v02_replay_control | 0.9600 | 1.0000 | 1.0000 | 0.0000 | PROMOTE |
| replay_control | 3 | blue_v03_replay_control | 0.9600 | 1.0000 | 1.0000 | 0.0000 | PROMOTE |
| replay_control | 4 | blue_v04_replay_control | 0.8400 | 1.0000 | 0.9200 | 0.0000 | PROMOTE |
| replay_control | 5 | blue_v04_replay_control | 0.9600 | 1.0000 | 0.9600 | 0.0000 | REJECT |
| replay_control | 6 | blue_v04_replay_control | 0.9600 | 1.0000 | 0.9600 | 0.0000 | REJECT |
| replay_control | 7 | blue_v07_replay_control | 0.9200 | 0.9200 | 0.9600 | 0.0000 | PROMOTE |
| replay_control | 8 | blue_v07_replay_control | 0.9600 | 0.9200 | 1.0000 | 0.0400 | REJECT |
| replay_control | 9 | blue_v07_replay_control | 0.9600 | 0.9200 | 1.0000 | 0.0400 | REJECT |
| replay_control | 10 | blue_v07_replay_control | 0.9200 | 0.9200 | 1.0000 | 0.0800 | REJECT |


## Promotion Gating & Anti-Forgetting Summary
- **Total Promotions**: 11
- **Total Rejections / Rollbacks**: 19
- **Anti-Forgetting Boundary**: Maximum allowable legacy degradation $\le 0.05$.

## Scientific Status Matrix
- **IMPLEMENTED**: `YES`
- **TESTED**: `YES` (100% unit tests passing)
- **STATUS**: `COMPLETED`
