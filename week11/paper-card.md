# Paper Card｜LoRA

| 项目 | 内容与原始出处 |
| --- | --- |
| 论文 | Edward J. Hu等，**LoRA: Low-Rank Adaptation of Large Language Models**；[arXiv:2106.09685v2](https://arxiv.org/abs/2106.09685v2)，v2日期2021-10-16；本卡固定v2 |
| 可核查实现 | [Microsoft官方仓库](https://github.com/microsoft/LoRA)，核对commit `c4593f060e6a368d7bb5af5273b8e42810cdef90`；[Linear实现](https://github.com/microsoft/LoRA/blob/c4593f060e6a368d7bb5af5273b8e42810cdef90/loralib/layers.py#L83)；代码MIT |
| 与本项目关系 | Week08/09已使用LoRA做合成文档文字的字段抽取；本周追问其机制、参数预算与合并性质。它不是文档解析专用论文，也不是视觉模型论文 |
| 问题（论文事实，§1/2） | 大模型为每个任务更新并保存全部参数，成本较高 |
| 方法（论文事实，§4.1） | 冻结原权重W₀，训练低秩A、B；有效权重W₀+(α/r)BA；可将增量合并回W₀ |
| 核心主张（作者主张，§5） | 在论文所测任务中，用较少的可训练参数获得有竞争力的适配效果 |
| 关键证据（论文事实，§5、§7.2/Table6） | 论文给出任务对照及多rank实验；Table6展示其GPT-3任务上小rank亦可有效，作者没有保证所有任务均适用 |
| 作者解释与边界 | 更新可能具有较低内在秩（§7），属于由实验支持的解释；“小rank足以解决任意任务”不在可支持范围内（§7.2脚注6） |
| 本地最小验证 | 重新训练SmolLM2-135M的r4/r8；检查JSON抽取、完整基座哈希、零初始化增量、delta公式、合并logits与greedy预测；事前标准见[计划](experiment-plan.md) |
| 未覆盖 | 未运行作者benchmark、全参微调、大模型GPU/吞吐实验；不验证论文分数、内存节约倍数或普适最优rank |

论文、作者代码与本地实现需要分开看：论文§4.1写A Gaussian、B零；该固定官方`Linear.reset_parameters`实际使用A Kaiming uniform、B零；本地PEFT0.19.0默认也用Kaiming uniform。核对的是代码语句而非附近容易误读的注释。三者仍有相同的初始零增量，但不能写成初始化分布完全相同。[原文](https://arxiv.org/html/2106.09685v2#S4.SS1)、[作者代码](https://github.com/microsoft/LoRA/blob/c4593f060e6a368d7bb5af5273b8e42810cdef90/loralib/layers.py#L110)。

**本地观察与个人推测**放在[复现报告](reports/reproduction-report.md)，不回填进论文事实。本卡由Codex检索和起草，本人阅读、五句话讲解与证据抽查待完成。
