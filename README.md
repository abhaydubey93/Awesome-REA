# Awesome Reverse Engineering Anything

A collection of **tools, projects, integrations, and references** for reverse engineering websites, games, apps, native binaries, and firmware.

**[Website](https://awesomerea.org) · [Full repository index](https://awesomerea.org/?view=source-index) · [GitHub](https://github.com/reacher-z/Awesome-REA) · [简体中文](README.zh-CN.md)**

[![Collection checks](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml/badge.svg)](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<a href="https://awesomerea.org"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, projects, integrations, and collections" width="760"></a>

## Contents

- [Website](#website)
- [Game](#game)
- [App](#app)
- [Native Binary](#native-binary)
- [Firmware and Hardware](#firmware)
- [Agents and MCP](#agents-and-mcp)
- [Related Collections](#related-collections)
- [References and Learning](#references-and-learning)
- [Full Repository Index](#full-repository-index)
- [Contributing](#contributing)

<a id="resource-catalog"></a>
## Resources

Each entry appears once under its main purpose. The collection includes independent projects as well as resources for [REA](https://github.com/morluto/rea); inclusion does not imply REA integration.

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website

- [webcrack](https://github.com/j4k0xb/webcrack) — Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles. **[Tool]**
- [WABT](https://github.com/WebAssembly/wabt) — WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation. **[Tool · WebAssembly]**
- [wasm-tools](https://github.com/bytecodealliance/wasm-tools) — Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces. **[Tool · WebAssembly]**
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) — Connect an agent to Chrome for live page inspection, network debugging, and performance traces. **[Integration · Independent MCP]**
- [mitmproxy](https://github.com/mitmproxy/mitmproxy) — Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools. **[Tool]**
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) — Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior. **[Integration · Independent MCP]**

<a id="game"></a>
### Game

- [DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/) — Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match. **[Case study · REA]**
- [TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/) — Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks. **[Case study · REA]**
- [RenderDoc](https://github.com/baldurk/renderdoc) — Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application. **[Tool]**
- [AssetRipper](https://github.com/AssetRipper/AssetRipper) — Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats. **[Tool]**
- [Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) — Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress. **[Tool]**
- [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) — Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored. **[Tool]**
- [RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp) — Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection. **[Integration · Independent MCP]**

<a id="app"></a>
### App

- [Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/) — An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence. **[Case study · REA]**
- [Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/) — Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit. **[Case study · REA]**
- [JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp) — JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context. **[Integration · Independent MCP]**
- [frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp) — Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation. **[Integration · Independent MCP]**
- [Super Trouper](https://github.com/crissyfield/super-trouper) — Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts. **[Integration · Independent MCP]**
- [Frida](https://github.com/frida/frida) — Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes. **[Tool]**
- [JADX](https://github.com/skylot/jadx) — Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages. **[Tool · Android]**
- [Apktool](https://github.com/iBotPeaches/Apktool) — Decodes Android resources and smali into a project-like tree and can rebuild modified packages. **[Tool · Android]**
- [Androguard](https://github.com/androguard/androguard) — Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP. **[Tool · Android]**
- [ILSpy](https://github.com/icsharpcode/ILSpy) — .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend. **[Tool · .NET]**
- [dnSpyEx](https://github.com/dnSpyEx/dnSpy) — Community continuation of dnSpy for debugging and editing .NET assemblies without the original source. **[Tool · .NET]**
- [@electron/asar](https://github.com/electron/asar) — Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected. **[Tool]**

<a id="native-binary"></a>
### Native Binary

- [DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/) — An official educational challenge investigation connects binary checks to equations and records an original-program validation. **[Case study · REA]**
- [Ghidra](https://github.com/NationalSecurityAgency/ghidra) — Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats. **[Tool]**
- [radare2](https://github.com/radareorg/radare2) — Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures. **[Tool]**
- [Cutter](https://github.com/rizinorg/cutter) — Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration. **[Tool]**
- [Qiling](https://github.com/qilingframework/qiling) — Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis. **[Tool]**
- [Unicorn Engine](https://github.com/unicorn-engine/unicorn) — Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control. **[Tool · Library]**
- [angr](https://github.com/angr/angr) — Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation. **[Tool · Library]**
- [LIEF](https://github.com/lief-project/LIEF) — Library for structured parsing and modification of executable formats including ELF, PE and Mach-O. **[Tool · Library]**
- [Capstone](https://github.com/capstone-engine/capstone) — Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines. **[Tool · Library]**
- [ImHex](https://github.com/WerWolv/ImHex) — Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats. **[Tool]**
- [x64dbg](https://github.com/x64dbg/x64dbg) — Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code. **[Tool]**
- [GDB](https://sourceware.org/gdb/) — Native and remote debugger for controlling execution and inspecting live or crashed program state. **[Tool]**
- [rr](https://github.com/rr-debugger/rr) — Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution. **[Tool]**
- [Diaphora](https://github.com/joxeankoret/diaphora) — IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions. **[Tool]**
- [BinDiff](https://github.com/google/bindiff) — Compares disassembled binaries to find matching functions and changed code across versions. **[Tool]**
- [Detect It Easy](https://github.com/horsicq/Detect-It-Easy) — Format-aware file identification and static inspection using parsers, signatures and programmable heuristics. **[Tool]**

<a id="firmware"></a>
### Firmware and Hardware

- [PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint) — The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer. **[Case study · Mixed workflow]**
- [Binwalk](https://github.com/ReFirmLabs/binwalk) — Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage. **[Tool]**
- [unblob](https://github.com/onekey-sec/unblob) — Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions. **[Tool]**
- [Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils) — Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images. **[Tool]**

<a id="agents-and-mcp"></a>
### Agents and MCP

- [REA — Reverse Engineer Anything](https://github.com/morluto/rea) — The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior. **[Project · REA]**
- [Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything) — Target routing, connection recovery and evidence practices for agents using REA. **[Integration · REA]**
- [dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea) — A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI. **[Integration · REA]**
- [rea-jev](https://github.com/juan-viox/rea-jev) — A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration. **[Integration · REA]**
- [rea-casebook](https://github.com/pablodiazjorge/rea-casebook) — A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs. **[Integration · REA]**
- [Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp) — Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration. **[Integration · Independent MCP]**
- [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) — Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes. **[Integration · Independent MCP]**
- [Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html) — Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents. **[Integration · Independent MCP]**
- [Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp) — Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries. **[Integration · Independent MCP]**
- [IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp) — Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server. **[Integration · Independent MCP]**
- [Radare2 MCP Server](https://github.com/radareorg/radare2-mcp) — Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access. **[Integration · Independent MCP]**
- [r2ai](https://github.com/radareorg/r2ai) — AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models. **[Integration · Independent agent]**
- [DAILA](https://github.com/mahaloz/DAILA) — Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management. **[Integration · Independent agent]**
- [RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra) — Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation. **[Integration · Independent agent]**
- [LLDB MCP](https://lldb.llvm.org/use/mcp.html) — LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping. **[Integration · Independent MCP]**
- [Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill) — Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers. **[Integration · Independent agent]**
- [SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering) — Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices. **[Integration · Independent agent]**

<a id="related-collections"></a>
### Related Collections

- [Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering) — A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations. **[Collection]**
- [Awesome REA Cases](https://github.com/songshikang0111/awesome-REA-cases) — A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes. **[Collection]**

<a id="references-and-learning"></a>
### References and Learning

- [Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md) — Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks. **[Documentation · REA]**
- [CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md) — CLI workflows for saving Evidence and projecting smaller views from completed analysis. **[Documentation · REA]**
- [MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog) — Canonical tool contracts, provider discovery and Evidence semantics for integration authors. **[Documentation · REA]**
- [Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md) — Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider. **[Documentation · REA]**
- [Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md) — Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits. **[Documentation · REA]**
- [Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md) — Inspect Android package identity, classes, methods and references through REA's JADX integration. **[Documentation · REA]**
- [Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md) — Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly. **[Documentation · REA]**
- [Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md) — Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started. **[Documentation · REA]**
- [Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md) — Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity. **[Documentation · REA]**
- [Browser observation guide](https://rea.tools/guides/browser/) — Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result. **[Documentation · REA]**
- [JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/) — A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence. **[Documentation · REA]**
- [rea-playbook](https://github.com/jinshi666888/rea-playbook) — An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis. **[Learning resource]**
- [rea-lab](https://github.com/pablodiazjorge/rea-lab) — A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations. **[Research]**
- [OpenSecurityTraining2](https://ost2.fyi/) — Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations. **[Learning resource]**
- [pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/) — Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises. **[Learning resource]**
- [Reverse Engineering for Beginners](https://beginners.re/) — Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages. **[Learning resource]**
- [The Official Radare2 Book](https://book.rada.re/) — Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins. **[Learning resource]**
<!-- END GENERATED CATALOG -->

<a id="search-the-catalog"></a>
## Full Repository Index

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
**1,600** repository READMEs scanned; **1,589** entries available to browse. The 11 clearly out-of-scope entries remain in the scan data. This automatically discovered index is separate from the curated resources above and has not been individually execution-tested.

[Browse by category on GitHub](docs/repositories/README.md) · [Search website](https://awesomerea.org/?view=source-index&lang=en) · [Full bilingual index JSON](https://awesomerea.org/source-index.json) · [Curated catalog JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

The resource list above is curated from primary sources. Detailed requirements, original evidence, and review dates are available in the [catalog data](data/README.md).

## Contributing

New tools, projects, case studies, and collections are welcome. Suggest a resource or improve an existing entry through the [contribution guide](CONTRIBUTING.md). Use a project link, a concise description, and an accurate resource type.

## About

This is an independent community collection. Original descriptions and code are [MIT licensed](LICENSE); linked projects retain their own licenses.

[Supporting documentation](data/README.md) · [Repository scanning method](docs/source-scan.md)
