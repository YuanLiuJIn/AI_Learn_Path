page1：
{封面页：
大字标题：一场模型的文艺复兴：jev
汇报人：刘晋元
}

page2：
{
ppt上方小标题：什么是jev
1.官方定义a frontier-intelligence function call: unstructured state in, typed probabilistic decisions out
2.输入输出：输入	一个共享 state（字符串 / JSON / 数组）+ 若干 typed questions（一次请求可混用三类） 输出	类型化值 + 概率分布（Choice/Score 另给 confidence），无字符串输出
3.三类原语：Choice；Score；Noul
4.技术优势：并行求值；问题互相隔离；结构即契约
}

page3:
{
ppt上方小标题：jev训练范式    
列表格，表头：范式；奖励信号；解决问题
范式有：RLHF，RLVR，RLCD
（
范式	奖励信号	解决了什么	没解决什么
RLHF	人类偏好	流畅、讨喜	置信度毫无保证
RLVR	可验证对错	客观对错	只告诉你对不对，不告诉你多确定
RLCD	真值 + Brier 类校准指标	"说到做到"：说 0.8，长期约 80% 命中	需要真值；OOD 下是否守得住未知
）
}

page4：
{
ppt上方小标题：训练详解
中间放一句话：见jev研究笔记（助眠）
}

page5：
{
ppt上方小标题：我的思考
1.能力边界；
[
只给判断不给理由 → 不可审计、不可追溯；
问题之间无共享推理	不能让 Q2 依赖 Q1 的结论——没有链式判断
不做扩展推理	单个问题不能是"长链思考"，只能是 gut-check 级判断
]
2.官方隐藏了什么？
[
架构细节	只说"new model architecture + parallel sampler"，无规模、无 tokenizer、无数据来源
confidence 的确切定义	Choice 同时返回 probabilities 和 confidence，但 confidence 是 max p、熵、还是二阶量——未定义。你无法设阈值，也就无法做置信度门控
]
3.我们能用来做什么？   
[
参考架构，改进地质或者定制软件的confidence，解决黑盒问题；
参考deepseek加上多模态组件，增强vla判断功能；
]
}