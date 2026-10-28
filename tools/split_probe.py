"""Split a year's extracted text into individual questions and report boundaries."""

import os
import re
import sys

TEXT = r"E:\CST\408\work\text"

QRE = re.compile(r"(?m)^\s*(\d{1,2})\s*[.．、]\s*")


def load(year):
    for fn in os.listdir(TEXT):
        if fn.startswith(str(year)) and fn.endswith(".txt") and not fn.endswith(".ocr.txt"):
            return open(os.path.join(TEXT, fn), encoding="utf-8").read()
    return None


def split_questions(txt):
    body = re.sub(r"(?s)^#.*?\n\n", "", txt)
    body = re.sub(r"<<<PAGE \d+>>>", "\n", body)
    body = re.sub(r"\d{4}\s*年计算机408统考真题\s*第\s*\d+\s*页[^\n]*", "", body)
    marks = [(m.start(), int(m.group(1))) for m in QRE.finditer(body)]
    out = {}
    for idx, (pos, num) in enumerate(marks):
        if num in out:
            continue
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(body)
        seg = body[pos:end].strip()
        if len(seg) > 15:
            out.setdefault(num, seg)
    return out


KEY = {
    "DS": ["链表", "栈", "队列", "二叉树", "树", "图", "排序", "查找", "散列", "哈希", "哈夫曼",
           "复杂度", "归并", "堆", "邻接", "拓扑", "关键路径", "B树", "KMP", "模式串", "遍历",
           "线索", "并查集", "AVL", "平衡", "折半", "冒泡", "希尔", "基数", "生成树", "最短路径",
           "数组", "矩阵", "串", "叶子", "结点", "顶点", "度数", "败者树"],
    "CO": ["补码", "IEEE", "浮点", "Cache", "cache", "页表", "TLB", "指令", "流水线", "总线",
           "DMA", "中断", "寄存器", "ALU", "CPU", "主存", "芯片", "字节", "整数", "溢出",
           "CPI", "MIPS", "程序计数器", "地址", "数据通路", "控制器", "微程序", "寻址",
           "Cache", "虚存", "虚拟存储", "磁盘", "SSD", "小端", "大端", "对齐", "汇编"],
    "OS": ["进程", "线程", "信号量", "PV", "死锁", "页面置换", "inode", "索引节点", "磁盘调度",
           "SPOOLing", "缓冲", "管程", "调度", "临界区", "互斥", "同步", "文件", "目录",
           "页框", "抖动", "工作集", "系统调用", "内核", "用户态", "就绪", "阻塞", "时间片",
           "银行家", "虚拟地址空间", "分页", "分段", "内存映射"],
    "NET": ["TCP", "UDP", "IP", "子网", "路由", "DNS", "HTTP", "CSMA", "以太网", "以太",
            "报文", "帧", "信道", "带宽", "时延", "香农", "奈奎斯特", "拥塞", "滑动窗口",
            "ARP", "DHCP", "ICMP", "BGP", "OSPF", "RIP", "交换机", "集线器", "VLAN",
            "域名", "端口", "三次握手", "拥塞窗口", "发送窗口", "比特", "调制", "编码",
            "OSI", "协议", "路由器"],
}


def guess(seg):
    sc = {k: 0 for k in KEY}
    for k, words in KEY.items():
        for w in words:
            sc[k] += seg.count(w)
    # tie-break order by paper layout
    return max(sc.items(), key=lambda kv: kv[1])


def main():
    years = [int(y) for y in sys.argv[1:]] or list(range(2009, 2027))
    for yr in years:
        txt = load(yr)
        if not txt:
            print(f"{yr}: no text")
            continue
        qs = split_questions(txt)
        nums = sorted(qs)
        print(f"\n{'='*90}\n{yr}  found {len(nums)} questions: {nums[:3]}...{nums[-3:]}")
        row = []
        for n in nums:
            if n <= 40:
                subj, _ = guess(qs[n])
                row.append(f"{n}:{subj}")
        print("  " + " ".join(row))


if __name__ == "__main__":
    main()
