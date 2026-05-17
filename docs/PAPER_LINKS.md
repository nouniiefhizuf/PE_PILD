# Paper Links & References

## This Paper

- **arXiv**: [2501.xxxxx](https://arxiv.org/abs/2501.xxxxx) (coming soon)
- **OpenReview**: TBD
- **NeurIPS 2025**: [neurips.cc](https://neurips.cc)
- **Code**: [github.com/medtech-tn/physreason-800](https://github.com/medtech-tn/physreason-800)
- **Dataset**: Included in this repository (`data/physreason800.json`)
- **PCS Scorer**: `pip install physreason-pcs`

---

## Referenced Datasets

| Dataset | Paper | URL | License |
|---------|-------|-----|---------|
| SciQ | Welbl et al., EMNLP 2017 | [github.com/allenai/sciq](https://github.com/allenai/sciq) | CC-BY 4.0 |
| PhysicsQA | Liu et al., arXiv 2023 | [arXiv:2311.02512](https://arxiv.org/abs/2311.02512) | Custom |
| ARC | Clark et al., arXiv 2018 | [allenai.org/data/arc](https://allenai.org/data/arc) | CC-BY 4.0 |
| MMLU | Hendrycks et al., ICLR 2021 | [github.com/hendrycks/test](https://github.com/hendrycks/test) | MIT |

---

## Referenced Models

| Model | Organization | URL | Access |
|-------|-------------|-----|--------|
| GPT-4o | OpenAI | [openai.com](https://openai.com) | API |
| Claude 3.5 Sonnet | Anthropic | [anthropic.com](https://anthropic.com) | API |
| Gemini 1.5 Pro | Google | [deepmind.google](https://deepmind.google) | API |
| Llama-3-70B | Meta AI | [llama.meta.com](https://llama.meta.com) | Together AI / Self-host |
| Mixtral-8x22B | Mistral AI | [mistral.ai](https://mistral.ai) | Together AI / Self-host |

---

## Key Related Work

1. **Chain-of-Thought Prompting**: Wei et al., NeurIPS 2022 — [arXiv:2201.11903](https://arxiv.org/abs/2201.11903)
2. **Zero-Shot CoT**: Kojima et al., NeurIPS 2022 — [arXiv:2205.11916](https://arxiv.org/abs/2205.11916)
3. **Self-Consistency**: Wang et al., ICLR 2023 — [arXiv:2203.11171](https://arxiv.org/abs/2203.11171)
4. **Role-Play Prompting**: Kong et al., arXiv 2023 — [arXiv:2308.07702](https://arxiv.org/abs/2308.07702)
5. **PhysicsBench**: Liu et al., arXiv 2023 — [arXiv:2311.02512](https://arxiv.org/abs/2311.02512)
6. **BERTScore**: Zhang et al., ICLR 2020 — [arXiv:1904.09675](https://arxiv.org/abs/1904.09675)
7. **LLM-as-Judge**: Zheng et al., NeurIPS 2024 — [arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
8. **Prompt Sensitivity**: Mizrahi et al., TACL 2024; Sclar et al., ICLR 2024
9. **Politeness Taxonomy**: Yin et al., arXiv 2023 — [arXiv:2306.10226](https://arxiv.org/abs/2306.10226)

---

## Citation

```bibtex
@inproceedings{soltani2025physical,
  title={Do Physical Laws Help LLMs Think? Graded Prompt Engineering for Physical Reasoning in Large Language Models},
  author={Soltani, Ahmed and Chanchah, Ryan and Darghouth, Skander and Ben Rejeb, Khalil},
  booktitle={NeurIPS},
  year={2025}
}
```
