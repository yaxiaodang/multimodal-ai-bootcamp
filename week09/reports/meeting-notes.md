# Week09几分钟讲解

1. 我们要解决的不是再训练一个更大模型，而是让每个结论能回查到一组配置、数据与产物。
2. 在Week08入口加入可选追踪。每次创建一个W&B run；config说怎么跑，history记每一步，summary记最后结论。只改学习率，从相同base重新训练A/B。
3. baseline先落盘，训练过程中记录loss、lr、NLL、CPU/内存/耗时，最后用相同validation生成；保存adapter后重新加载，核对预测一致。
4. artifact相当于一组带版本的实验文件。我们记录dataset/code/model/evaluation的本地digest和文件SHA256，关联run ID、代码commit及数据freeze。云端版本号要同步后才有。
5. 展示[曲线](curves.png)和[报告结果表](report.md)。exact回答“生成是否正确”，NLL回答“参考答案在模型下是否更可能”，不要混为一谈。
6. 原始失败包括base的非JSON输出和一次沙箱SDK启动失败；另做了第2步主动中断演练，明确不算自然训练故障、不加入A/B排名。
7. 当前限制：CPU文本合成小样本、单seed、小验证集，尚无独立测试和真实文档泛化结论。两个训练run同分时不凭NLL或单次时间宣布赢家。
8. 本人收尾：登录同步，核对云端artifact版本，创建网页Report，抽查原始预测，填写真实学习时间。接下来Week10先对齐文本字段抽取与PDF解析的评测范围，再考虑独立测试和错误分析。

AI完成实施和自动核验；这份讲稿不等于本人已经学习或核验。
