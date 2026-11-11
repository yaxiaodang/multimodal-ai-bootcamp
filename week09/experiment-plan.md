# Week09 运行前计划（2026-11-11）

目标：在Week08训练入口接入真实W&B SDK，用CPU、离线模式运行两个可比较实验，保留可同步的原生spool和可在GitHub审查的JSON/曲线/报告。离线模式不等于已创建云端Report。

A/B唯一算法变量：learning_rate=0.001 / 0.0005；name仅为身份标签。沿用96 train、12 validation、seed42、SmolLM2-135M固定revision、LoRA r8/alpha16、60步、相同greedy生成及严格JSON字段指标。验证集不当作独立测试，不读取reserved-test内容，也不使用Week07 PDF测试集训练。

假设：两种学习率都可能改善生成格式；只比较任务准确率、参考答案NLL、训练曲线及资源。没有多seed和大测试集，不宣称学习率优劣或泛化。选择模型的规则：先核验数据与重加载；验证集严格exact优先，同时报告负面结果；同分时不凭单次耗时认定更优，暂不部署。

预算：CPU双线程，FP32，每个训练循环最多900秒，GPU小时=0，不购买云服务。W&B每步记录训练loss/lr/gradient norm、进程RSS/CPU、主机内存、耗时；SDK同时采集系统指标。CPU%可因双线程大于100，RSS是当前进程内存，peak RSS是进程历史峰值，均不代表整台VM总成本。

证据链：Git commit+源码SHA256 → 冻结数据SHA256 → W&B run ID → dataset/code/model/evaluation artifact本地digest和文件SHA256 → 原始预测/指标 → 比较报告。云端:vN和Report URL待登录同步后由本人补齐，禁止编造。

失败恢复探索：额外运行标注intentional-failure的演练，在第2步主动抛错，验证非零退出、failure.json、failed summary及日志保留；不参与A/B排名。真实失败也保留。恢复时重新运行创建新run，不修改原失败目录。

许可与隐私：继承Week08 dataset card，自制虚构账单，不含真实个人资料；基础模型Apache-2.0。仅跟踪明确列出的实验文件，禁用自动Git diff捕获以免带入其他周的工作区改动。不保存API key，不扫描/导出环境变量；W&B原生spool与缓存保存在本机且被Git忽略。AI实施与本人审阅分开披露。
