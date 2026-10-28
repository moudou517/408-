# 408 真题复习中心

把 **2009–2026 共 18 套 408 统考真题**按 **2025 考纲的 127 个叶子知识点**重新整理，
做成一个可以直接刷的离线网页：**知识体系 → 按考点刷题 → 看解析**，一条线走完。

> **830 道题** · **686 道选择题带官方答案** · **119 道综合题带参考答案与思路** · **437 张题目插图**

纯静态站点，不需要后端、不需要联网、不需要装任何东西——双击 `index.html` 就能用。

---

## 在线访问

打开 GitHub Pages（首次需在仓库 `Settings → Pages` 里把 Source 设为 `main / (root)`）：

**<https://moudou517.github.io/408-/>**

## 本地打开（三种都行）

| 方式 | 做法 | 适合 |
|---|---|---|
| **最简单** | 双击 `out/index.html` | 任何人，零依赖 |
| 带图标 | 双击 `快捷方式\打开复习中心.bat` | 自己电脑（图标可重建） |
| 平板 / 手机 | `python tools\serve.py 8000`，同一 Wi-Fi 下访问 `电脑IP:8000` | 局域网多设备 |

`快捷方式\启动局域网服务_平板用.bat` 会打印全部可用地址并生成二维码；
连不上就先跑 `允许平板访问_加防火墙规则.bat`（管理员）。

## 六个页面

| 页面 | 是什么 |
|---|---|
| `out/index.html` | 总入口：知识体系 / 题库 / 刷题 三个门 |
| `out/map.html` | **知识框架**：4 科 → 25 章 → 116 个考点，标【必考】【高频】，每个考点一键跳题库 |
| `out/browse.html` | **题库全集**：830 道真题，按科目/章/考点检索，逐题可展开解析 |
| `out/quiz.html` | **选择题刷题**：686 道，8 种题库 × 2 种出题顺序 × 2 种判分方式 |
| `out/bigq.html` | **综合题刷题**：119 道，先自己写思路 → 按「显示参考答案与思路」→ 自评会/不会 |
| `out/report.html` | **完整分析报告**：18 年分类统计 + 120 分复习方案 + 思维导图/流程图 |

另有打印版 `out/408_题库索引.pdf`（66 页，PDF 内部可跳转）与 `out/408_图表集.pdf`（32 页）。

### 刷题的分类不是只有「随机」

- **选择题**：全部 / 10 个专题包（树与图、协议细节、CPU与IO、Cache、内存文件、数据表示、排序查找、子网、PV、流水线）/ 按科目 / 按章节 / **按知识点** / 按年份 / **按考频**（必考 ≥14 年、高频、常考、低频）/ 错题本
- **格式**：乱序或按年份顺序；**即时判分**（边做边看解析）或 **交卷判分**（整套做完再对答案）
- **综合题**：按科目/章节/知识点/年份筛选，`空格` 显示答案、`1` 会了、`2` 不会

## 目录结构

```
408/
├─ index.html            # GitHub Pages 入口（跳转到 out/）
├─ out/                  # 成品站点（唯一需要发给别人的东西）
│  ├─ index.html map.html browse.html quiz.html bigq.html report.html
│  ├─ qimg/              # 437 张题目插图
│  ├─ fig/               # 31 张报告图表（思维导图、流程图）
│  ├─ data/              # 结构化数据（quiz.json / bigq.json / 分类 CSV）
│  └─ 408_题库索引.pdf  408_图表集.pdf
├─ tools/                # 全套生成管线（见下）
├─ 快捷方式/             # .bat 入口（相对路径，可整体搬移）
├─ 分享/                 # 离线分享包（被 .gitignore 忽略，可自行生成）
└─ .pylibs/ work/        # 依赖与中间产物（不上传）
```

## 重新生成

原始真题 PDF / 解析 PDF 需自行放到仓库根目录（版权原因未上传）。

```powershell
$env:PYTHONPATH = "$PWD\.pylibs"

# 1. 抽取 → 切题 → 分类
python tools\extract.py              # PDF 文字层（扫描页走 OCR）
python tools\ocr_parallel.py         # 扫描页 OCR（RapidOCR）
python tools\analyze.py              # 切题 + 按考纲归类

# 2. 答案与解析
python tools\parse_answers.py        # 选择题答案（文字层表格）
python tools\ocr_answer_grid.py      # 表格被拆散时按坐标重建（部分年份）
python tools\extract_bigq.py         # 综合题题干 + 参考答案与思路

# 3. 插图
python tools\extract_figures.py      # 有图形对象的年份：精确裁切
python tools\extract_figures_scan.py # 整页扫描的年份：裁原卷切片

# 4. 统计与图表
python tools\build_stats.py
python tools\make_figures.py
python tools\make_mindmaps.py        # 四科思维导图
python tools\make_flows.py           # 流程分析图

# 5. 出页面
python tools\make_quiz.py            # quiz.html
python tools\make_bigq.py            # bigq.html
python tools\make_map.py             # map.html
python tools\make_browse.py          # browse.html
python tools\report_gen.py           # report.html
python tools\make_index.py           # index.html
python tools\make_pdf.py             # 两个 PDF

# 6. 打包/分发
python tools\make_bats.py            # 重写「快捷方式」里的 bat
python tools\make_share.py           # 离线分享包 + zip
```

依赖：`PyMuPDF pypdf rapidocr-onnxruntime reportlab qrcode Pillow numpy opencv-python`。
`tools\` 里还有若干 `debug_*` / `probe_*` 脚本，是排查切题、答案表格、插图定位时用的，可忽略。

## 数据口径与已知局限

- **题号即科目**：选择题 Q1–11 数据结构 / 12–22 组成原理 / 23–32 操作系统 / 33–40 网络；综合题 Q41–47 **按内容判科**（个别年份不按科目排序，如 2014 年 Q42 实为图论题）。
- **分类覆盖** 830/846 ≈ 98.1%；26 道题选项为图片、无法文字化，未进刷题器。
- **选择题答案** 720/720 全部还原（部分年份的答案表格在 PDF 文字层里被打散，用 OCR + 坐标重建，并用选项分布 A150/B177/C187/D172 的均匀性做交叉验证）。
- **综合题解析** 116/119；2025 年 43、46、47 三题的解析 PDF 使用符号字体，题号被抽成乱码，无法定位。
- **插图分两类**：能定位图形对象的年份按题精确裁切；整页扫描的年份（2009/2010/2013/2015/2016/2018/2020/2023）改为裁「该题整段原卷」并标注。
- 做题记录（错题本、统计）存在浏览器 `localStorage`，**按设备各存一份**，不跨设备同步。

## 版权声明

真题与解析的著作权归原命题机构及出版方所有。本仓库仅用于个人学习交流，
**不含**原始 PDF，题目文字与插图为学习整理之用。如涉版权问题请开 issue，会立即处理。

## 相关文档

- `out/README.md` —— 完整交付说明（页面细节、平板连接、代码排版与插图做法）
- `out/408_真题分类与120分复习方案.md` —— 文字版复习方案
