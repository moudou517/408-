# -*- coding: utf-8 -*-
"""Authored flow / decision diagrams for 408 problem solving."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viz  # noqa: E402

ROOT = r"E:\CST\408"
FIG = os.path.join(ROOT, "out", "fig")
os.makedirs(FIG, exist_ok=True)


def P(name):
    return os.path.join(FIG, name)


def flow(name, title, nodes, subject, note=None, figsize=(15, 22)):
    return viz.draw_flow(title, nodes, P(name), figsize=figsize,
                         subject=subject, note=note)


# ---------------------------------------------------------------- 1. 三轮
def roadmap():
    nodes = [
        {"kind": "start", "text": "开始：确定目标分 120"},
        {"kind": "step", "text": "① 用本报告第二章，把四科目标分写死：DS 38 / CO 34 / OS 27 / NET 21",
         "right": "允许失分 30 分"},
        {"kind": "note", "text": "自测诊断：限时做最近 2 套真题，按题号统计各科得分率"},
        {"kind": "decide", "text": "哪一科得分率 < 55%？",
         "right": "该科 = 第一轮重点"},
        {"kind": "step", "text": "② 第一轮 · 基础（8–10 周）\n按考纲章节顺序过教材/复习书，每章配套做题\n顺序建议：数据结构 → 计组 → 操作系统 → 网络"},
        {"kind": "decide", "text": "选择题正确率 ≥ 60% 且能默写每章主干？",
         "right": "否：回补该章"},
        {"kind": "step", "text": "③ 第二轮 · 强化（5–6 周）\n按第四/五章高频考点定向刷真题\n四大专题集中突破：Cache、流水线、PV、子网"},
        {"kind": "decide", "text": "选择题正确率 ≥ 80%？大题能独立写标准过程？",
         "right": "否：只补薄弱专题"},
        {"kind": "step", "text": "④ 第三轮 · 冲刺（3–4 周）\n每周 2 套限时套卷（180 min，严格计时）\n错题本二刷；背诵点（协议字段、寄存器、口诀）过 3 遍"},
        {"kind": "decide", "text": "套卷稳定在 115–125 分？",
         "right": "否：回到错题本，不要开新资料"},
        {"kind": "end", "text": "⑤ 考前一周：只看错题本 + 本报告图表，不做新题"},
    ]
    return flow("10_三轮复习流程.png",
                "408 三轮复习总流程（目标 120 分）", nodes, "MIX",
                note="验收标准写死在流程里——每一轮不达标就不要进下一轮",
                figsize=(16, 24))


# ---------------------------------------------------------------- 2. DS 大题
def ds_big():
    nodes = [
        {"kind": "start", "text": "41/42 题（数据结构综合，共 23 分）"},
        {"kind": "decide", "text": "题目要求的是「算法设计」还是「应用题」？"},
        {"kind": "step", "text": "【41 算法设计 13 分】三段式答题模板\n① 算法基本设计思想（2–3 句人话，讲清用什么结构、怎么走）\n② C/C++ 代码（含注释，用题目给的结点/数组定义）\n③ 时间复杂度 + 空间复杂度（必须写，通常占 1–2 分）"},
        {"kind": "note", "text": "常见套路：双指针 / 快慢指针 / 辅助数组计数 / 递归遍历 / 栈消除递归 / 归并思想",
         "right": "先写暴力，再优化"},
        {"kind": "step", "text": "【42 应用题 10 分】\n图论类：画邻接矩阵/邻接表 → 手工跑 Prim/Kruskal/Dijkstra/拓扑/关键路径\n树类：画树 → 标层次 → 算 WPL / 判断平衡 / 哈夫曼编码\n散列类：画表 → 依次插入 → 统计 ASL（成功/失败分别算）"},
        {"kind": "decide", "text": "是否要求「最优」复杂度？",
         "right": "是：先想 O(n) 一遍扫描"},
        {"kind": "step", "text": "写出完整过程：每一步的中间结果都要留在卷面上（判卷按步骤给分）"},
        {"kind": "end", "text": "检查：边界条件（空表/单结点/全部相同）是否处理"},
    ]
    return flow("11_DS大题流程.png", "数据结构 41/42 题实战流程", nodes, "DS",
                note="41 题哪怕写不出最优解，也要写出暴力解并说明复杂度——不会 0 分",
                figsize=(16, 20))


# ---------------------------------------------------------------- 3. CO 大题
def co_big():
    nodes = [
        {"kind": "start", "text": "43/44 题（计组综合，共 23 分）"},
        {"kind": "decide", "text": "题目主体是「存储/Cache」还是「指令/数据通路」？"},
        {"kind": "step", "text": "【存储类】先拆地址：\n① 由「按字节编址 + 页大小/块大小」求出 页内偏移/块内偏移 位数\n② 剩余高位 = 页号 / 主存块号 / tag+组号\n③ Cache：块大小→块内地址；行数→行号；组相联：组数=行数/路数"},
        {"kind": "step", "text": "【存储类续】命中率与平均访问时间：\nT = h·Tc + (1−h)·Tm；写回法要注意脏位与写回开销"},
        {"kind": "step", "text": "【指令类】先定格式：\n定长指令字 → 数一数操作码/寄存器/立即数各几位\n扩展操作码：从「短操作码留出全 1 前缀」倒推可扩展条数\n寻址方式：算出有效地址 EA，再取操作数"},
        {"kind": "step", "text": "【数据通路类】按指令周期拆微操作：\n取指（PC→MAR→M→MDR→IR，PC+1）→ 译码 → 取数 → 执行 → 写回\n每个微操作写出控制信号（Rd/Wr/ALUop/MUX选择）"},
        {"kind": "decide", "text": "是否涉及流水线？",
         "right": "是：画时空图"},
        {"kind": "step", "text": "【流水线】k 段、n 条指令：\n总周期 = (k + n − 1) × Δt（无冒险）\n有数据冒险：插入气泡/转发，重算总周期\n吞吐率 = n / 总时间；加速比 = 串行时间 / 流水时间"},
        {"kind": "end", "text": "检查：位数加总是否等于机器字长；单位（ns/cycle/B）是否统一"},
    ]
    return flow("12_CO大题流程.png", "计算机组成原理 43/44 题实战流程", nodes, "CO",
                note="计组大题的失分几乎全部来自「位数算错」和「单位没统一」",
                figsize=(16, 24))


# ---------------------------------------------------------------- 4. OS 大题
def os_big():
    nodes = [
        {"kind": "start", "text": "45/46 题（操作系统综合，共 15 分）"},
        {"kind": "decide", "text": "题目是「同步互斥」还是「内存/文件」？"},
        {"kind": "step", "text": "【同步互斥 · PV】四步建模：\n① 找共享资源 → 每个资源一个互斥信号量 mutex=1\n② 找「可用数量」→ 计数信号量 = 初始空闲数\n③ 找「先后顺序」→ 同步信号量初值 0，前 V 后 P\n④ 写出每个进程的 P/V 序列，检查不会死锁"},
        {"kind": "note", "text": "口诀：互斥 P/V 夹住临界区；同步「先 V 后 P」；多个 P 的顺序不能反（先资源后互斥）",
         "right": "P 顺序错→死锁"},
        {"kind": "step", "text": "【内存 · 页式】\n① 由「页大小」定页内偏移位数\n② 虚地址 → 页号 + 偏移；查页表 → 页框号\n③ 物理地址 = 页框号 × 页大小 + 偏移\n④ TLB/多级页表：逐级拆分页号"},
        {"kind": "step", "text": "【页面置换】画表逐行模拟：\nOPT（往后看最久不用）/ FIFO（队列，注意 Belady）/\nLRU（最近最久未用）/ CLOCK（访问位）\n每访问一次记一次缺页，最后算缺页率"},
        {"kind": "step", "text": "【文件】\n索引结点：直接/一级/二级/三级间接 → 算最大文件长度\n混合索引：地址项个数 × 盘块大小 逐级累加\n空闲空间：位示图 → 字号/位号；成组链接 → 分组跳跃"},
        {"kind": "decide", "text": "是否要求画图/列表？",
         "right": "是：必须画，按表格给分"},
        {"kind": "end", "text": "检查：信号量初值、缺页次数、地址换算单位（KB/MB）"},
    ]
    return flow("13_OS大题流程.png", "操作系统 45/46 题实战流程", nodes, "OS",
                note="PV 大题只要把「资源 + 顺序」两个维度拆干净，就不存在写不出来",
                figsize=(16, 24))


# ---------------------------------------------------------------- 5. NET 大题
def net_big():
    nodes = [
        {"kind": "start", "text": "47 题（计算机网络综合，9 分）"},
        {"kind": "decide", "text": "题目主线：地址类 / 传输类 / 时延类？"},
        {"kind": "step", "text": "【地址类】子网划分五步：\n① 写出 IP 与掩码的二进制（至少到第 3 字节）\n② 掩码中 1 的个数 = 前缀长度；/n → 主机位 = 32−n\n③ 子网数 = 2^(新前缀−原前缀)；每子网地址数 = 2^主机位\n④ 网络地址 = IP AND 掩码；广播地址 = 网络地址 + 地址数 − 1\n⑤ 可用主机 = 地址数 − 2（减去网络地址与广播地址）"},
        {"kind": "step", "text": "【地址类续】CIDR 聚合：把多条前缀写成二进制，找公共前缀，取最长\n路由转发：最长前缀匹配，逐条试"},
        {"kind": "step", "text": "【传输类】TCP 窗口计算：\n发送窗口 = min(拥塞窗口, 接收窗口)\n序号/确认号按「字节」编号，不是按报文编号\n吞吐量 = 窗口大小 / RTT"},
        {"kind": "step", "text": "【传输类续】拥塞控制：\n慢开始（cwnd 指数增长到 ssthresh）→ 拥塞避免（线性+1）\n超时：ssthresh = cwnd/2，cwnd = 1\n3 个重复 ACK：快重传 + 快恢复（cwnd = ssthresh）"},
        {"kind": "step", "text": "【时延类】\n发送时延 = 数据长度 / 带宽\n传播时延 = 距离 / 电磁波速度（光纤 ≈ 2×10⁸ m/s）\n总时延 = 各段发送 + 传播 + 处理 + 排队；\n分组交换要乘「跳数」；电路交换要先加建立时间"},
        {"kind": "decide", "text": "是否问「至少/最多」？",
         "right": "是：注意边界（不满一个分组也要发）"},
        {"kind": "end", "text": "检查：b/B 是否混用（bit vs Byte，1B = 8b）；1M = 10⁶ 还是 2²⁰"},
    ]
    return flow("14_NET大题流程.png", "计算机网络 47 题实战流程", nodes, "NET",
                note="网络的失分 80% 来自单位换算和二进制手算错误，不是不会",
                figsize=(16, 22))


# ---------------------------------------------------------------- 6. 存储层次贯通
def storage_chain():
    nodes = [
        {"kind": "start", "text": "一条访存指令的完整地址旅程（计组 3 章 + OS 3 章）"},
        {"kind": "step", "text": "① CPU 发出虚拟地址 VA（32/48 位）"},
        {"kind": "step", "text": "② MMU 拆分 VA：页号 VPN + 页内偏移 offset\n页大小 4KB → offset = 12 位；VPN = VA 高位"},
        {"kind": "decide", "text": "③ 查 TLB 命中？",
         "right": "命中：直接得页框号"},
        {"kind": "step", "text": "④ TLB 未命中 → 查页表（可能多级）\n页表项 = 页框号 PPN + 有效位 + 访问位 + 脏位 + 保护位"},
        {"kind": "decide", "text": "⑤ 页表项有效位 = 1（页面在内存）？",
         "right": "否：缺页异常 → 调页"},
        {"kind": "step", "text": "⑥ 缺页处理：OS 选一个页框，按置换算法淘汰\n若被淘汰页脏位=1 → 先写回磁盘\n从磁盘读入所需页 → 更新页表 → 重新执行指令"},
        {"kind": "step", "text": "⑦ 得到物理地址 PA = PPN × 页大小 + offset"},
        {"kind": "step", "text": "⑧ 用 PA 访问 Cache：PA 拆成 tag + 组号 + 块内地址\n（直接映射：tag + 行号 + 块内地址）"},
        {"kind": "decide", "text": "⑨ Cache 命中？",
         "right": "否：访主存"},
        {"kind": "step", "text": "⑩ Cache 缺失 → 从主存取整个块装入 Cache\n直接映射：位置固定；组相联：组内任选一行，按 LRU 替换\n写策略：写回（脏位）/ 写直达"},
        {"kind": "end", "text": "⑪ 数据返回 CPU。全程可能发生 1 次缺页 + 1 次 Cache 缺失"},
    ]
    return flow("20_存储层次贯通.png",
                "存储层次贯通：Cache — 主存 — 虚拟存储", nodes, "CO",
                note="这张图是计组第三章与 OS 第三章的公共骨架，两边大题都用它",
                figsize=(15, 24))


# ---------------------------------------------------------------- 7. Cache 地址划分
def cache_addr():
    nodes = [
        {"kind": "start", "text": "Cache 地址划分与容量计算"},
        {"kind": "step", "text": "已知：机器字长、按字节编址、Cache 容量 C、块大小 B、路数 k"},
        {"kind": "step", "text": "① 块内地址位数 = log2(B)\n例：块大小 64B → 6 位"},
        {"kind": "step", "text": "② Cache 行数 = C / B\n例：32KB / 64B = 512 行"},
        {"kind": "decide", "text": "映射方式？"},
        {"kind": "step", "text": "【直接映射】行号位数 = log2(行数)\n地址 = tag | 行号 | 块内地址",
         "right": "tag = 主存地址位数 − 行号 − 块内"},
        {"kind": "step", "text": "【全相联】无行号\n地址 = tag | 块内地址",
         "right": "tag = 主存地址 − 块内"},
        {"kind": "step", "text": "【k 路组相联】组数 = 行数 / k\n组号位数 = log2(组数)\n地址 = tag | 组号 | 块内地址"},
        {"kind": "step", "text": "③ Cache 总容量 = 行数 × (数据位 + tag位 + 有效位 + 脏位 + 替换控制位)"},
        {"kind": "decide", "text": "题目问的是「数据区」还是「总容量」？",
         "right": "总容量要加标记位"},
        {"kind": "end", "text": "④ 平均访问时间 = h·Tc + (1−h)·(Tc + Tm)\n或 = Tc + (1−h)·Tm（同时访问时）"},
    ]
    return flow("21_Cache地址划分.png", "Cache 地址位数计算流程", nodes, "CO",
                note="90% 的错误是「把总容量当数据区」或「行号/组号搞混」",
                figsize=(15, 18))


# ---------------------------------------------------------------- 8. 流水线
def pipeline():
    nodes = [
        {"kind": "start", "text": "指令流水线：冒险判定与性能计算"},
        {"kind": "step", "text": "① 画时空图：横轴时钟周期，纵轴指令，每个流水段一行\n（这是唯一不会错的方法，不要心算）"},
        {"kind": "decide", "text": "有结构冒险（同一部件被两条指令同时用）？",
         "right": "是：停顿 / 增加部件"},
        {"kind": "decide", "text": "有数据冒险（后指令用前指令结果）？",
         "right": "是：转发 or 插入气泡"},
        {"kind": "step", "text": "数据冒险判定：看「写回段」与「读寄存器段」谁先\nRAW：后读前写 → 需要转发；转发不了要停 1–2 拍\n（load-use 冒险通常必须停 1 拍）"},
        {"kind": "decide", "text": "有控制冒险（转移指令）？",
         "right": "是：延迟槽 / 分支预测"},
        {"kind": "step", "text": "② 计算：\nk 段流水线执行 n 条指令，无冒险：T = (k + n − 1)·Δt\n有停顿：T = (k + n − 1 + 停顿数)·Δt"},
        {"kind": "step", "text": "③ 指标：\n吞吐率 TP = n / T\n加速比 S = 串行执行时间 / T = n·k·Δt / T\n效率 E = S / k"},
        {"kind": "end", "text": "④ 检查：Δt 是否等于最慢流水段耗时（含流水寄存器开销）"},
    ]
    return flow("22_流水线分析.png", "指令流水线分析流程", nodes, "CO",
                note="一定画时空图。心算停顿数是最常见的失分方式",
                figsize=(15, 20))


# ---------------------------------------------------------------- 9. PV 建模
def pv():
    nodes = [
        {"kind": "start", "text": "PV 操作建模：从自然语言到信号量"},
        {"kind": "step", "text": "① 数「进程/角色」：每个能独立并发的行为主体 = 一个进程\n（生产者、消费者、读者、写者、甲、乙、丙…）"},
        {"kind": "step", "text": "② 找「互斥资源」：一次只能一个人用的东西\n→ mutex = 1，使用时 P(mutex) … V(mutex) 夹住"},
        {"kind": "step", "text": "③ 找「计数资源」：有多少个可用\n→ 信号量初值 = 空闲数量\n取用 P，归还 V"},
        {"kind": "step", "text": "④ 找「先后顺序」：A 完成后 B 才能开始\n→ 信号量初值 = 0；A 末尾 V(s)；B 开头 P(s)"},
        {"kind": "decide", "text": "有「缓冲区/容量上限」？",
         "right": "是：再加 empty=容量, full=0"},
        {"kind": "step", "text": "⑤ 每个进程写成：while(1){ 准备; P(...); 临界区; V(...); }\n检查：P 的顺序先资源后互斥；V 的顺序随意"},
        {"kind": "decide", "text": "会不会死锁？（两个进程互相等对方持有的资源）",
         "right": "会：调整 P 顺序 / 一次申请全部"},
        {"kind": "end", "text": "⑥ 写出信号量定义（名字 + 初值 + 含义），这三样都要写，判卷给分"},
    ]
    return flow("23_PV建模.png", "PV 操作建模流程", nodes, "OS",
                note="经典模型：生产者-消费者 / 读者-写者 / 哲学家进餐 / 理发师 — 全部可用这五步套出来",
                figsize=(15, 20))


# ---------------------------------------------------------------- 10. 页面置换
def paging():
    nodes = [
        {"kind": "start", "text": "页面置换手工模拟（OPT / FIFO / LRU / CLOCK）"},
        {"kind": "step", "text": "① 画表：列 = 页框（编号 1..m），行 = 每次页面访问\n最后一列记「是否缺页」"},
        {"kind": "step", "text": "② 第一次访问：必然缺页，装入空闲页框"},
        {"kind": "decide", "text": "③ 页面已在内存？",
         "right": "命中：不换，只更新访问信息"},
        {"kind": "decide", "text": "④ 还有空闲页框？",
         "right": "有：直接装入"},
        {"kind": "step", "text": "⑤ 无空闲 → 按算法选victim：\nOPT：往后看，淘汰最久不被访问的（理论上界）\nFIFO：淘汰最早进入的（用队列，注意 Belady 异常）\nLRU：淘汰最久未使用的（往前看）\nCLOCK：循环扫描，访问位=1 则置 0 跳过，=0 则淘汰"},
        {"kind": "decide", "text": "被淘汰页「脏位」= 1？",
         "right": "是：多一次写磁盘"},
        {"kind": "step", "text": "⑥ 统计：缺页次数 / 访问次数 = 缺页率\n注意：置换本身不增加缺页计数（只算访问未命中）"},
        {"kind": "end", "text": "⑦ 检查：FIFO 与 LRU 结果是否相同（小规模下常相同，别抄错）"},
    ]
    return flow("24_页面置换.png", "页面置换算法手工模拟流程", nodes, "OS",
                note="一定要逐行画表，不要跳步；LRU 与 FIFO 的区别只有「用没用过」",
                figsize=(15, 18))


# ---------------------------------------------------------------- 11. 子网划分
def subnet():
    nodes = [
        {"kind": "start", "text": "子网划分 / CIDR / 最长前缀匹配"},
        {"kind": "step", "text": "① 把 IP 地址与掩码写成二进制（至少前 3 字节）\n例 192.168.1.130 / 26\n掩码 255.255.255.192 = 11111111.11111111.11111111.11000000"},
        {"kind": "step", "text": "② 前缀长度 n = 掩码中 1 的个数\n主机位 = 32 − n；每子网地址数 = 2^(32−n)\n可用主机 = 2^(32−n) − 2"},
        {"kind": "step", "text": "③ 网络地址 = IP AND 掩码\n广播地址 = 网络地址 + 2^(32−n) − 1\n可用范围 = 网络地址+1 ~ 广播地址−1"},
        {"kind": "decide", "text": "题目要求「划分成 k 个子网」？",
         "right": "是：借位 = ceil(log2 k)"},
        {"kind": "step", "text": "④ 借 m 位 → 新前缀 = n + m\n新掩码 = 原掩码 + m 个 1\n每子网地址数 = 2^(32−n−m)"},
        {"kind": "decide", "text": "题目要求「路由聚合 / CIDR」？",
         "right": "是：找公共前缀"},
        {"kind": "step", "text": "⑤ 聚合：把多条前缀写二进制，从左向右找所有条目的公共前缀\n聚合后前缀长度 = 公共前缀长度；反例：若某条不满足，需回退"},
        {"kind": "end", "text": "⑥ 转发：最长前缀匹配；检查地址是否落在该前缀范围内"},
    ]
    return flow("25_子网划分.png", "子网划分与 CIDR 计算流程", nodes, "NET",
                note="「可用主机数减 2」和「借位取整」是两个高频陷阱",
                figsize=(15, 20))


# ---------------------------------------------------------------- 12. TCP
def tcp():
    nodes = [
        {"kind": "start", "text": "TCP 连接管理 + 窗口/拥塞控制计算"},
        {"kind": "step", "text": "① 连接建立（三次握手）：\nSYN(seq=x) → SYN+ACK(seq=y, ack=x+1) → ACK(seq=x+1, ack=y+1)\n注意：SYN 和 FIN 各消耗 1 个序号，纯 ACK 不消耗"},
        {"kind": "step", "text": "② 连接释放（四次挥手）：\nFIN → ACK → FIN → ACK；主动关闭方进入 TIME_WAIT（2MSL）"},
        {"kind": "step", "text": "③ 可靠传输：序号按「字节」编号\n有效载荷 = 段长；下一段序号 = 本段序号 + 载荷长度\n确认号 = 期望收到的下一个字节序号（累积确认）"},
        {"kind": "decide", "text": "题目给了「接收窗口 rwnd」和「拥塞窗口 cwnd」？",
         "right": "是：发送窗口 = min"},
        {"kind": "step", "text": "④ 发送窗口 = min(cwnd, rwnd)\n可发送字节数 = 发送窗口 − 已发未确认"},
        {"kind": "step", "text": "⑤ 拥塞控制：\n慢开始：每 RTT cwnd 翻倍，直到 ssthresh\n拥塞避免：每 RTT cwnd +1\n超时：ssthresh = cwnd/2，cwnd = 1，重新慢开始\n3 个重复 ACK：快重传 + 快恢复，ssthresh = cwnd/2，cwnd = ssthresh"},
        {"kind": "step", "text": "⑥ 吞吐量 = 窗口 / RTT；或 = 窗口 × 速率（视题目）"},
        {"kind": "end", "text": "⑦ 检查：字节 vs 报文段；序号回绕（mod 2³²）；发送/接收窗口方向"},
    ]
    return flow("26_TCP状态.png", "TCP 计算流程（连接管理 / 窗口 / 拥塞）", nodes, "NET",
                note="题目里「第几个字节」和「第几个报文段」是最容易混的，先统一成字节编号",
                figsize=(15, 22))


# ---------------------------------------------------------------- 13. 图算法
def graph_alg():
    nodes = [
        {"kind": "start", "text": "图算法选择决策树（选择题 + 42 题）"},
        {"kind": "step", "text": "先看题目要什么：连通性 / 最短路 / 顺序 / 最长路"},
        {"kind": "decide", "text": "求「连接所有顶点、代价最小」？",
         "right": "→ 最小生成树"},
        {"kind": "step", "text": "MST：\nPrim：从一个顶点起，每次并入最近顶点（适合稠密图，O(V²)）\nKruskal：按边权排序，不成环就加入（适合稀疏图，O(ElogE)）",
         "right": "两者结果代价相同，但树可能不同"},
        {"kind": "decide", "text": "求「两个顶点之间最短路径」？",
         "right": "→ 最短路径"},
        {"kind": "step", "text": "最短路径：\n单源、无负权：Dijkstra O(V²)\n多源 / 有负权：Floyd O(V³)\n无权图：BFS 即可"},
        {"kind": "decide", "text": "求「顶点的执行先后顺序」？",
         "right": "→ 拓扑排序"},
        {"kind": "step", "text": "拓扑排序：反复输出入度为 0 的顶点并删除其出边\n存在拓扑序列 ⇔ 有向图无环（DAG）\n序列唯一 ⇔ 每一步只有一个入度为 0 的顶点"},
        {"kind": "decide", "text": "求「工程最短完成时间 / 哪些活动不能拖延」？",
         "right": "→ 关键路径"},
        {"kind": "step", "text": "关键路径（AOE）：\n① 拓扑序求事件最早发生时间 ve\n② 逆拓扑序求最迟发生时间 vl\n③ 活动最早开始 e = ve(起点); 最迟开始 l = vl(终点) − 持续时间\n④ l − e = 0 的活动 = 关键活动；关键活动构成关键路径"},
        {"kind": "end", "text": "检查：无向图求 MST；有向图求拓扑/关键路径——不要混用"},
    ]
    return flow("27_图算法.png", "图算法选择决策树", nodes, "DS",
                note="42 题最爱考：拓扑排序 + 关键路径（AOE）；一定要把 ve/vl 表画出来",
                figsize=(16, 24))


if __name__ == "__main__":
    for fn in (roadmap, ds_big, co_big, os_big, net_big, storage_chain,
               cache_addr, pipeline, pv, paging, subnet, tcp, graph_alg):
        print(fn())
