# far-analogy skill
Install: unzip into ~/.claude/skills/ (or your agent's skills folder). Scripts need `pip install pyyaml`.
- SKILL.md: procedure (motif door, obstacle door, 6 steps, output format).
- data/core_en.yaml: 103 core correspondences in English (breaks + sources, unchecked).
- data/graph_vi.yaml: 2,133 machine-generated correspondences in Vietnamese (sources unchecked).
- data/translation_vi_en.yaml: links Vietnamese core node names to English ones so paths cross languages.
- data/families.yaml: 45 coarse families (Vietnamese + English keywords).
- scripts/find_path.py, scripts/check_arxiv.py.
Status counts in graph_vi are likely inflated (74% "theorem"); treat it as raw material.
