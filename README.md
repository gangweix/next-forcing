<h1 align="center">Next Forcing: Causal World Modeling with Multi-Chunk Prediction</h1>

<p align="center">
  <strong>Gangwei Xu, Qihang Zhang, Jiaming Zhou, Xing Zhu, Yujun Shen, Xin Yang, Yinghao Xu</strong>
</p>

<p align="center">
  <a href="https://gangweix.github.io/next-forcing/"><img src="https://img.shields.io/badge/Project-Page-blue" alt="Project page"></a>
  <a href="https://arxiv.org/pdf/2606.11187"><img src="https://img.shields.io/badge/Paper-arXiv-b31b1b" alt="Paper"></a>
  <a href="https://github.com/gangweix/next-forcing"><img src="https://img.shields.io/badge/Code-coming_soon-lightgrey" alt="Code"></a>
</p>

## Overview

Next Forcing is a multi-chunk prediction framework for causal world modeling. Standard autoregressive video world models are trained with teacher-forced next-chunk denoising, which can become shortcut-prone: adjacent chunks are visually similar, especially at high frame rates, so the model can reduce loss by copying local appearance instead of learning long-range dynamics.

Next Forcing addresses this myopic supervision by adding lightweight Multi-Chunk Prediction (MCP) modules that predict multiple future video chunks, such as `next^1`, `next^2`, and `next^3`, alongside the main model. The MCP modules form a causal prediction chain and inject dense temporal supervision back into the main world model. At inference time, the same MCP modules can be retained to predict the next video chunk in parallel with the current one, enabling faster rollout.

This repository currently hosts the project page and visual assets. Code will be released upon paper acceptance.

## Highlights

- **Multi-chunk prediction objective:** supervises multiple future horizons instead of only the current chunk.
- **Causal MCP chain:** near-future MCP predictions inform farther-future predictions while preserving causality.
- **Multi-layer feature fusion:** MCP modules consume intermediate representations from several backbone layers, improving gradient flow into the main model.
- **Zero-overhead deployment option:** discard MCP modules at inference and keep the improved main model.
- **Parallel chunk generation option:** retain the depth-1 MCP module to generate the next chunk in parallel and obtain `2x` inference acceleration.

## Method

<p align="center">
  <img src="assets/figures/next-forcing-method-architecture.png" alt="Next Forcing method architecture" width="95%">
</p>

During training, the main model denoises the current chunk as in standard teacher forcing. In parallel, three auxiliary MCP modules denoise future shifted targets. The modules are lightweight transformer blocks initialized from the main model and conditioned on fused intermediate features from the backbone. A higher MCP timestep shift encourages the auxiliary modules to rely on the main model's temporal representations rather than solving the future denoising task independently.

The same trained checkpoint supports two inference modes:

- **Zero-overhead mode:** remove MCP modules and run the main model exactly like the baseline.
- **MCP-accelerated mode:** keep the first MCP module so one autoregressive step produces both the current chunk and the next chunk.

## Results

### RoboTwin

Next Forcing achieves the best average success rate on the RoboTwin benchmark across 50 bimanual manipulation tasks.

| Method | Clean | Random |
| --- | ---: | ---: |
| X-VLA | 72.9 | 72.8 |
| pi_0 | 65.9 | 58.4 |
| pi_0.5 | 82.7 | 76.8 |
| Motus | 88.7 | 87.0 |
| Being-H0.7 | 90.2 | 89.6 |
| Fast-WAM | 91.9 | 91.8 |
| LingBot-VA | 92.9 | 91.5 |
| **Next Forcing** | **94.1** | **93.5** |

<p align="center">
  <img src="assets/figures/robotwin-convergence-results.png" alt="RoboTwin convergence comparison" width="95%">
</p>

At `50 fps`, Next Forcing shows the largest gains: at `5k` training steps it reaches `70.2 / 61.6%` success on Clean / Random, compared with `45.5 / 31.9%` for LingBot-VA. It matches LingBot-VA's `45k`-step Random accuracy at only `20k` steps, corresponding to `2.3x` faster convergence.

### Inference Acceleration

MCP-accelerated inference predicts the next video chunk in parallel with the current chunk. It preserves comparable accuracy while reducing sequential video denoising cost.

| FPS | Standard Clean | Standard Random | MCP-acc. Clean | MCP-acc. Random |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 94.1 | 93.5 | 93.5 | 90.6 |
| 25 | 92.6 | 91.4 | 91.0 | 89.8 |
| 50 | 91.8 | 90.5 | 92.2 | 91.3 |

### PhyWorld

On PhyWorld, Next Forcing improves both video quality and physical consistency over LingBot-VA.

| Method | OOT FVD | IT FVD | OOT Abnormal Ratio | IT Abnormal Ratio |
| --- | ---: | ---: | ---: | ---: |
| LingBot-VA | 5.3 | 3.5 | 12% | 3% |
| **Next Forcing** | **4.7** | **3.2** | **8%** | **2%** |

### General Video Pretraining

On 3.5M in-house general video clips, Next Forcing also improves pure video generation after removing the action stream.

<p align="center">
  <img src="assets/figures/general-video-fvd-curves.png" alt="General video pretraining FVD curves" width="80%">
</p>

At `50k` training steps, Next Forcing reduces FVD by `58%` on Test Set 1 (`94` vs. `225`) and by `52%` on Test Set 2 (`97` vs. `204`). It also surpasses LingBot-VA's `50k`-step FVD with only `10k` training steps.

## Project Status

- [x] Project page and demos
- [x] Paper
- [ ] Training and inference code
- [ ] Model checkpoints

## Citation

```bibtex
@article{nextforcing,
  title={Next Forcing: Causal World Modeling with Multi-Chunk Prediction},
  author={Gangwei Xu and Qihang Zhang and Jiaming Zhou and Xing Zhu and Yujun Shen and Xin Yang and Yinghao Xu},
  journal={},
  year={2026}
}
```

