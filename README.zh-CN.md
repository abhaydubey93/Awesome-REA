# Awesome Reverse Engineering Anything

收集值得关注的**工具、项目、集成与参考资料**，覆盖网站、游戏、应用、原生二进制、固件与硬件逆向。

**[网站](https://awesomerea.org/?lang=zh) · [完整仓库索引](https://awesomerea.org/?view=source-index&lang=zh) · [GitHub](https://github.com/reacher-z/Awesome-REA) · [English](README.md)**

[![目录检查](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml)
[![MIT 许可证](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<a href="https://awesomerea.org/?lang=zh"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — 工具、项目、集成与资源合集" width="760"></a>

## 目录

- [Website · 网站](#website)
- [Game · 游戏](#game)
- [App · 应用](#app)
- [Native Binary · 原生二进制](#native-binary)
- [Firmware · 固件与硬件](#firmware)
- [Agents & MCP · Agent 与集成](#agents-and-mcp)
- [Related Collections · 相关合集](#related-collections)
- [References & Learning · 文档与学习资料](#references-and-learning)
- [完整仓库索引](#完整仓库索引)
- [参与贡献](#参与贡献)

<a id="资源目录"></a>
<a id="resource-catalog"></a>
## 资源

每条资源按主要用途收录一次。本合集同时包含独立项目和 [REA](https://github.com/morluto/rea) 相关资源；收录不代表已经接入 REA。

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website · 网站

- [webcrack](https://github.com/j4k0xb/webcrack) — 识别支持的 JavaScript 混淆模式，并拆解 webpack/Browserify 打包文件，改善代码可读性。 **[工具]**
- [WABT](https://github.com/WebAssembly/wabt) — WebAssembly 二进制与文本转换、节区检查、验证、解释执行及 C 转换工具集。 **[工具 · WebAssembly]**
- [wasm-tools](https://github.com/bytecodealliance/wasm-tools) — Bytecode Alliance 提供的 CLI 与 Rust 库，用于检查 WebAssembly 模块、元数据、组件和 WIT 接口。 **[工具 · WebAssembly]**
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) — 连接智能体与 Chrome，检查实时页面、调试网络并记录性能轨迹。 **[集成 · 独立 MCP]**
- [mitmproxy](https://github.com/mitmproxy/mitmproxy) — 通过交互代理、Web 界面或可脚本化命令行检查和记录 HTTP 流量。 **[工具]**
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) — 通过结构化无障碍快照驱动浏览器交互，调查可复现的网页行为。 **[集成 · 独立 MCP]**
- [Wakaru](https://github.com/pionxzh/wakaru) — 通过还原已识别的压缩与转译模式，从发布后的 JavaScript 包中恢复可读模块，支持拆包与现代语法恢复，便于分析生产环境前端代码。 **[工具]**
- [Spectral](https://github.com/spectral-mcp/spectral) — 用 LLM 分析捕获的应用 HTTP 流量，生成 MCP 工具、OpenAPI 3.1 规范或 GraphQL 模式；完成抓包与认证配置后，生成的工具可直接调用已观察到的 API。 **[集成 · 独立 Agent]**
- [jsdeob-workbench](https://github.com/Owl4444/jsdeob-workbench) — 在查看 JavaScript AST 和变量作用域的同时，可视化编排 Babel 转换链；保存分析项目与可复用插件，逐步简化混淆脚本。 **[工具]**

<a id="game"></a>
### Game · 游戏

- [DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/) — 根据指令与常量重建单个声像函数；上游报告 3,205 例与 63 字节匹配。 **[案例 · REA]**
- [TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/) — 检查 PC-98 DOS 的 16 位弹幕角度辅助函数，并关联固定版本重建与历史编译器检查。 **[案例 · REA]**
- [RenderDoc](https://github.com/baldurk/renderdoc) — 检查自己游戏或图形应用的帧捕获、绘制调用、着色器和图形资源。 **[工具]**
- [AssetRipper](https://github.com/AssetRipper/AssetRipper) — 分析 Unity 游戏文件，检查资源依赖并将支持的资源转换为 Unity 工程格式。 **[工具]**
- [Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) — 结合二进制与元数据分析，从 Unity IL2CPP 构建恢复托管表示；重建能力仍在开发中。 **[工具]**
- [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) — 恢复 IL2CPP 元数据及占位程序集，为原生分析工具生成辅助脚本；不会还原方法代码。 **[工具]**
- [RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp) — 向智能体开放已有 RenderDoc 捕获文件，分步检查帧、管线、资源和着色器。 **[集成 · 独立 MCP]**
- [UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool) — 浏览和修改受支持的 GameMaker 数据文件、提取资源，以及反编译或编译 GML VM 代码；提供房间编辑、脚本化修改、CLI 和可复用的 UndertaleModLib 库。 **[工具]**
- [frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge) — 在运行中的进程里检查 IL2CPP 类、方法和字段，无需提供 global-metadata.dat 即可跟踪或拦截方法调用，为静态 IL2CPP 转储工具补充运行时观察能力。 **[工具]**
- [objdiff](https://github.com/encounter/objdiff) — 比较参考目标文件与重新编译目标文件中的函数和数据，辅助匹配反编译；显示指令级差异、还原 C++ 符号，并可在源码变更时自动重新构建。 **[工具]**
- [UE Explorer](https://github.com/UE-Explorer/UE-Explorer) — 通过类、属性与依赖树浏览 Unreal 包，反编译和导出 UnrealScript 类、检查字节码，并查看结构化二进制数据。 **[工具]**
- [GARbro](https://github.com/morkt/GARbro) — 像浏览文件夹一样查看已识别的视觉小说资源归档，预览内容，并在提取图像或音频时转换为常用格式。 **[工具]**

<a id="app"></a>
### App · 应用

- [Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/) — 追踪 Aegis APK 的 TOTP 计算，官方公开目标指纹与选取的调查证据。 **[案例 · REA]**
- [Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/) — 结合 REA 发现与独立源码阅读追踪剪贴板桥；动态包装器仍有明确限制。 **[案例 · REA]**
- [JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp) — 结合 JADX 插件与 Python MCP 服务，读取 Android 反编译代码、资源、交叉引用和调试上下文。 **[集成 · 独立 MCP]**
- [frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp) — Frida MCP 服务，提供持久插桩会话、运行时检查和 Android 静态代码与动态现场之间的导航。 **[集成 · 独立 MCP]**
- [Super Trouper](https://github.com/crissyfield/super-trouper) — 单个可执行文件形式的 Frida MCP 服务，用于发现设备、管理进程会话和加载插桩脚本。 **[集成 · 独立 MCP]**
- [Frida](https://github.com/frida/frida) — 动态插桩工具，用脚本观察和分析运行中的原生及托管进程行为。 **[工具]**
- [JADX](https://github.com/skylot/jadx) — 将 Dex 反编译为 Java 的 CLI/GUI 工具，提供 Android 资源解码、代码导航和引用搜索。 **[工具 · Android]**
- [Apktool](https://github.com/iBotPeaches/Apktool) — 将 Android 资源与 smali 解码为项目目录，并支持重新构建修改后的安装包。 **[工具 · Android]**
- [Androguard](https://github.com/androguard/androguard) — 用于 APK/DEX 元数据、字节码及引用分析的 Python 工具集；v5 源码分支还提供智能体技能和 MCP 文档。 **[工具 · Android]**
- [ILSpy](https://github.com/icsharpcode/ILSpy) — .NET 程序集浏览器与 C# 反编译器，支持完整项目导出、元数据检查和命令行处理。 **[工具 · .NET]**
- [dnSpyEx](https://github.com/dnSpyEx/dnSpy) — dnSpy 的社区延续项目，可在没有原始源码时调试和编辑 .NET 程序集。 **[工具 · .NET]**
- [@electron/asar](https://github.com/electron/asar) — Electron 官方归档工具，可列出和提取 ASAR 内容，便于检查打包后的 JavaScript 与应用资源。 **[工具]**
- [Mobile Security Framework (MobSF)](https://github.com/MobSF/Mobile-Security-Framework-MobSF) — 通过 Web 界面与 API 检查移动应用包，结合静态分析及受支持设备上的动态测试，分析运行时行为与网络流量。 **[工具 · Android]**

<a id="native-binary"></a>
### Native Binary · 原生二进制

- [DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/) — 官方教育 CTF 案例：从检查函数得到方程，并记录原程序验证过程。 **[案例 · REA]**
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra) — 开源二进制分析套件，提供反汇编、反编译、图形分析及 Java/Python 自动化接口。 **[工具]**
- [radare2](https://github.com/radareorg/radare2) — 可脚本化的命令行逆向框架，支持多架构二进制检查、反汇编、调试和修改。 **[工具]**
- [Cutter](https://github.com/rizinorg/cutter) — 基于 Rizin 的图形逆向工作台，提供可扩展视图及 Ghidra 反编译器集成。 **[工具]**
- [Qiling](https://github.com/qilingframework/qiling) — 在 CPU 仿真之上补充操作系统、文件系统和 API 行为的 Python 框架，用于可插桩的二进制分析。 **[工具]**
- [Unicorn Engine](https://github.com/unicorn-engine/unicorn) — 多架构 CPU 仿真引擎，可控制寄存器、内存和钩子，执行选定的指令片段。 **[工具 · 程序库]**
- [angr](https://github.com/angr/angr) — 结合控制流恢复、符号执行、数据流分析和反编译的 Python 二进制分析框架。 **[工具 · 程序库]**
- [LIEF](https://github.com/lief-project/LIEF) — 对 ELF、PE、Mach-O 等可执行文件格式进行结构化解析与修改的库。 **[工具 · 程序库]**
- [Capstone](https://github.com/capstone-engine/capstone) — 提供统一 API 和指令细节的多架构反汇编库，适合构建自定义二进制分析流程。 **[工具 · 程序库]**
- [ImHex](https://github.com/WerWolv/ImHex) — 带二进制模式语言、结构化数据检查及可视化功能的十六进制编辑器，适合理解文件格式。 **[工具]**
- [x64dbg](https://github.com/x64dbg/x64dbg) — Windows 二进制调试器，通过反汇编、内存视图和插件分析没有源码的程序。 **[工具]**
- [GDB](https://sourceware.org/gdb/) — 支持本地与远程调试，可控制执行并检查运行中或崩溃后的程序状态。 **[工具]**
- [rr](https://github.com/rr-debugger/rr) — 记录进程执行并在 GDB 下重放，便于重复检查现场和反向执行。 **[工具]**
- [Diaphora](https://github.com/joxeankoret/diaphora) — 基于 IDA 的二进制差异分析工具，可匹配函数并迁移名称、注释与类型信息。 **[工具]**
- [BinDiff](https://github.com/google/bindiff) — 比较反汇编后的二进制文件，定位不同版本中的对应函数与代码变化。 **[工具]**
- [Detect It Easy](https://github.com/horsicq/Detect-It-Easy) — 结合格式解析器、签名和可编程启发式规则进行文件识别与静态检查。 **[工具]**
- [objection](https://github.com/sensepost/objection) — 通过基于 Frida 的命令界面探索运行中的 Android 与 iOS 应用，检查应用存储、内存、运行时对象和插桩后的行为。 **[工具]**
- [r2frida](https://github.com/nowsecure/r2frida) — 结合 radare2 命令与 Frida 插桩，检查桌面和移动目标中本地或远程进程的内存、符号、类及运行时调用。 **[工具]**

<a id="firmware"></a>
### Firmware · 固件与硬件

- [PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint) — 作者报告以 REA 开始 Android 调查，再借助独立 Hermes 工具实现 Windows BLE 打印。 **[案例 · 混合工具流程]**
- [Binwalk](https://github.com/ReFirmLabs/binwalk) — 识别固件中的嵌入格式并按需提取内容，辅以熵分析帮助初步分诊。 **[工具]**
- [unblob](https://github.com/onekey-sec/unblob) — 递归提取二进制数据中的归档与文件系统，同时报告数据块边界和未识别区域。 **[工具]**
- [Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils) — 面向 PCI Option ROM、UEFI 固件卷、Intel Flash Descriptor 和 coreboot 镜像的 Ghidra 加载器与辅助脚本。 **[工具]**
- [EMBA](https://github.com/e-m-b-a/emba) — 提取固件，结合静态检查与仿真分析，整理软件组件清单，并生成 Web 报告和 SBOM，供进一步调查。 **[工具]**
- [Firmware Analysis and Comparison Tool (FACT)](https://github.com/fkie-cad/FACT_core) — 通过可扩展平台解包和分析固件，使用 Web 界面与 HTTP API 搜索组件内容和分析结果，并比较不同样本。 **[工具]**
- [OFRAK](https://github.com/redballoonsecurity/ofrak) — 通过资源树图形界面与 Python API，递归识别、解包、分析、修改和重新打包固件及二进制格式，并可接入可选反汇编后端。 **[工具]**
- [FirmAE](https://github.com/pr0v3rbs/FirmAE) — 仿真路由器与 IP 摄像机固件，检查网络服务和运行时行为，提供自动仿真检查，以及独立的分析、运行和调试模式。 **[工具]**

<a id="agents-and-mcp"></a>
### Agents & MCP · Agent 与集成

- [REA — Reverse Engineer Anything](https://github.com/morluto/rea) — REA 官方 CLI 与 MCP 服务，连接分析工具并保留调查证据及限制。 **[项目 · REA]**
- [Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) — 官方面向使用者的调查技能，包含目标路由、连接恢复与证据工作流。 **[集成 · REA]**
- [dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea) — 社区 MCP 适配桥，以精选工具和 CLI 转发缩小宿主需要处理的工具面。 **[集成 · REA]**
- [rea-jev](https://github.com/juan-viox/rea-jev) — Claude Code 社区插件，在固定版本 REA MCP 外增加 Jev 路由和证据检查。 **[集成 · REA]**
- [rea-casebook](https://github.com/pablodiazjorge/rea-casebook) — Claude Code mod 汇集收到的 REA Evidence、追踪 unknown，并校验发现所引用的证据 ID。 **[集成 · REA]**
- [Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp) — Hex-Rays 官方 MCP 服务，让智能体操作 IDA 数据库，支持无界面分析和可选 GUI 联动。 **[集成 · 独立 MCP]**
- [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) — 通过 Ghidra 扩展和 MCP 桥接提供反编译、符号导航与重命名，支持 GUI 和无界面运行。 **[集成 · 独立 MCP]**
- [Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html) — Binary Ninja 自带的 MCP 接口向智能体提供函数、符号、反汇编、中间语言和反编译文本。 **[集成 · 独立 MCP]**
- [Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp) — 社区维护的 Binary Ninja 插件与 MCP 桥接，支持在多个已打开的二进制目标间切换。 **[集成 · 独立 MCP]**
- [IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp) — 已有工作流可参考的社区 IDA 集成；维护者目前推荐迁移到 Hex-Rays 官方 MCP 服务。 **[集成 · 独立 MCP]**
- [Radare2 MCP Server](https://github.com/radareorg/radare2-mcp) — 基于 radare2 原生接口的 MCP 服务，提供二进制分析、会话复用和可配置的只读访问。 **[集成 · 独立 MCP]**
- [r2ai](https://github.com/radareorg/r2ai) — 在 radare2 内使用本地或远程模型，辅助解释函数、改善命名和反编译结果。 **[集成 · 独立 Agent]**
- [DAILA](https://github.com/mahaloz/DAILA) — 跨 IDA、Ghidra、Binary Ninja 与 angr-management 的 AI 助手，用于函数摘要和命名辅助。 **[集成 · 独立 Agent]**
- [RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra) — 将 Ghidra 接入 RevEng.AI，用于函数相似性匹配、名称恢复、AI 解释及辅助标注。 **[集成 · 独立 Agent]**
- [LLDB MCP](https://lldb.llvm.org/use/mcp.html) — LLDB 官方 MCP 接口提供调试会话与命令，使智能体可以设置断点、检查内存和单步执行。 **[集成 · 独立 MCP]**
- [Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill) — 社区智能体技能，覆盖分诊、无界面导出和证据报告，并明确说明 REA 及其他 MCP 服务的工作流。 **[集成 · 独立 Agent]**
- [SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) — 针对 Binary Ninja 与 Ghidra 的分析技能，提供 MCP 工具使用、分析步骤和标注方法。 **[集成 · 独立 Agent]**

<a id="related-collections"></a>
### Related Collections · 相关合集

- [Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering) — REA 维护者整理的通用逆向资源目录，适合查找基础知识与相邻工具。 **[合集]**
- [Awesome REA Cases](https://github.com/songshikang0111/awesome-REA-cases) — 中英双语的 REA 与其他 AI 辅助逆向案例合集，附来源并区分作者报告、进行中的工作和复现状态。 **[合集]**

<a id="references-and-learning"></a>
### References & Learning · 文档与学习资料

- [Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md) — 安装、客户端配置、分析引擎依赖及按任务检查就绪状态的官方入口。 **[文档 · REA]**
- [CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md) — 保存完整 Evidence，再提取摘要或模块视图，适合脚本与可复现记录。 **[文档 · REA]**
- [MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) — 官方工具协议、能力发现和 Evidence 语义；适合集成与核对实际工具边界。 **[文档 · REA]**
- [Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) — 从函数清单到指令、伪代码和引用链的原生二进制调查流程。 **[文档 · REA]**
- [Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) — 从 JavaScript 应用图追踪功能、比较版本，同时保留静态分析的不确定性。 **[文档 · REA]**
- [Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) — 经 REA 的 JADX 集成检查 APK、类、方法与引用；结果不等于运行时验证。 **[文档 · REA]**
- [Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) — 静态读取 .NET 元数据与 CIL，比较成员并检查声明的原生代码边界。 **[文档 · REA]**
- [Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) — 离线检查已有 HAR、SAZ 等网页流量记录；不会自动抓包或访问记录中的 URL。 **[文档 · REA]**
- [Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) — 用 Binwalk 检查固件区域、用 Unblob 显式提取，并记录工具与制品身份。 **[文档 · REA]**
- [Browser observation guide](https://rea.tools/guides/browser/) — 通过官方 Notes 示例关联用户点击、导出请求与下载结果；REA 负责观察。 **[文档 · REA]**
- [JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/) — 官方自建 Notes 样例，从 renderer、preload、IPC 到 CSV 导出建立证据链。 **[文档 · REA]**
- [rea-playbook](https://github.com/jinshi666888/rea-playbook) — 提供 Electron 练习目标、Evidence 提取与 MCP 探测，区分离线展示和真正调用 REA。 **[学习资料]**
- [rea-lab](https://github.com/pablodiazjorge/rea-lab) — Windows REA/Ghidra 实验室，提供已知答案挑战、公开研究、上游贡献与限制说明。 **[研究]**
- [OpenSecurityTraining2](https://ost2.fyi/) — 免费的自主学习课程，提供逆向工程、固件和系统基础等学习路线。 **[学习资料]**
- [pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/) — 包含托管练习的逆向工程课程，覆盖函数、数据访问、静态工具和动态工具。 **[学习资料]**
- [Reverse Engineering for Beginners](https://beginners.re/) — Dennis Yurichev 编写的免费逆向入门书，以汇编与编译后程序理解为核心，提供多语言版本。 **[学习资料]**
- [The Official Radare2 Book](https://book.rada.re/) — radare2 官方实践参考，覆盖分析、反汇编、脚本、调试及相关插件。 **[学习资料]**
<!-- END GENERATED CATALOG -->

<a id="搜索目录"></a>
## 完整仓库索引

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
已读取 **2,000** 个仓库的 README，当前提供 **1,979** 个浏览条目，明确超出范围的 21 个条目保留在扫描数据中。自动发现的项目与上方精选资源分别维护，未逐项执行测试。

[按分类在 GitHub 浏览](docs/repositories/README.zh-CN.md) · [网站搜索](https://awesomerea.org/?view=source-index&lang=zh) · [完整双语索引 JSON](https://awesomerea.org/source-index.json) · [精选目录 JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

上面的资源清单依据一手来源整理。详细前置条件、原始来源与审阅日期保存在[目录数据](data/README.md)中。

## 参与贡献

欢迎推荐工具、项目、案例与其他资源合集，也欢迎完善已有条目。请参考[贡献指南](CONTRIBUTING.md)，提供项目链接、一句用途说明和准确的资源类型。

## 关于

本项目是独立社区资源合集。原创说明和代码使用 [MIT 许可证](LICENSE)，外部项目保留各自的许可证。

[补充文档](data/README.md) · [仓库扫描方法](docs/source-scan.md)
