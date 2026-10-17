# Awesome Reverse Engineering Anything

Tools, reconstruction cases and research for understanding websites, games, apps, native binaries, firmware and communication protocols.

<a href="https://awesomerea.org/"><img src="assets/readme-banner.svg" alt="Awesome Reverse Engineering Anything — tools, cases and papers across six reverse-engineering domains" width="960"></a>

**[Explore the collection ↗](https://awesomerea.org/) · [Curated directory](https://awesomerea.org/resources/) · [Research papers](https://awesomerea.org/papers/) · [简体中文](README.zh-CN.md)**

An independent, source-reviewed collection. Review does not imply runtime verification. [Evidence, requirements and review method](https://awesomerea.org/about/).

## Contents

- **Targets** · [Website](#website) · [Game](#game) · [App](#app) · [Native Binary](#native-binary) · [Firmware & Hardware](#firmware) · [Protocol](#protocol)

- [Papers](#papers) · [Cases](https://awesomerea.org/?view=curated&kind=case-study) · [Agents & MCP](#agents-and-mcp) · [Collections](#related-collections) · [Learning](#references-and-learning) · [Repository index](#full-repository-index)

<a id="resource-catalog"></a>
## Resources

Browse by purpose. Each entry appears once, with its type beside the name. Independent projects and [REA](https://github.com/morluto/rea) resources are included; listing does not imply REA integration.

<!-- BEGIN GENERATED CATALOG -->
<a id="website"></a>
### Website

[↑ Contents](#contents)

- **[webcrack](https://github.com/j4k0xb/webcrack)** <sub>Tool</sub>

  Improves JavaScript readability by reversing supported obfuscation patterns and unpacking webpack/Browserify bundles.

- **[WABT](https://github.com/WebAssembly/wabt)** <sub>Tool · WebAssembly</sub>

  WebAssembly tools for binary-to-text conversion, section inspection, validation, interpretation and C translation.

- **[wasm-tools](https://github.com/bytecodealliance/wasm-tools)** <sub>Tool · WebAssembly</sub>

  Bytecode Alliance CLI and Rust libraries for inspecting WebAssembly modules, metadata, components and WIT interfaces.

- **[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)** <sub>Integration · Independent MCP</sub>

  Connect an agent to Chrome for live page inspection, network debugging, and performance traces.

- **[mitmproxy](https://github.com/mitmproxy/mitmproxy)** <sub>Tool</sub>

  Inspect and record HTTP traffic with an interactive proxy, web interface, or scriptable command-line tools.

- **[Playwright MCP](https://github.com/microsoft/playwright-mcp)** <sub>Integration · Independent MCP</sub>

  Drive browser interactions through structured accessibility snapshots to investigate reproducible web behavior.

- **[Wakaru](https://github.com/pionxzh/wakaru)** <sub>Tool</sub>

  Recover readable modules from shipped JavaScript bundles by reversing recognized minifier and transpiler patterns. Supports bundle splitting and modern-syntax recovery for inspecting production frontend code.

- **[Spectral](https://github.com/spectral-mcp/spectral)** <sub>Integration · Independent agent</sub>

  Analyze captured application HTTP traffic with an LLM to generate MCP tools, OpenAPI 3.1 specifications, or GraphQL schemas. Generated tools call the observed API directly after capture and authentication setup.

- **[jsdeob-workbench](https://github.com/Owl4444/jsdeob-workbench)** <sub>Tool</sub>

  Inspect JavaScript ASTs and variable scopes while building visual chains of Babel transforms. Save analysis projects and reusable plugins to iteratively simplify obfuscated scripts.

- **[Browser Reverse Engineering Toolkit](https://github.com/Dvurechensky/Browser.Reverse.Engineering.Toolkit)** <sub>Tool</sub>

  Capture browser-session evidence, crawl websites in a persistent Chromium session, and generate offline architecture/API reports plus OpenAPI, SDK and mock-server drafts from saved captures.

<a id="game"></a>
### Game

[↑ Contents](#contents)

- **[DX-Ball: reconstruct sound panning](https://rea.tools/showcase/dx-ball/)** <sub>Case study · REA</sub>

  Recover one sound-pan function from instructions and constants; upstream cites 3,205 cases and a 63-byte match.

- **[TH04: recover a DOS bullet-ring helper](https://rea.tools/showcase/th04/)** <sub>Case study · REA</sub>

  Inspect a 16-bit PC-98 DOS helper and relate its angle calculation to a pinned reconstruction and historical compiler checks.

- **[Super Mario 64 DS: matching decompilation with relocation checks](https://github.com/tangosdev/sm64ds-decomp)** <sub>Case study · Independent reconstruction</sub>

  Reconstructs Super Mario 64 DS functions as C/C++ and permitted assembly primitives, comparing compiled output with a user-supplied cartridge dump. Independent relocation-destination checks strengthen the matching gate; integration into the PC port is tracked separately.

- **[GoldenEye 007: an agent-assisted native port from a decompilation](https://github.com/jkdansereau/goldeneye-pc-port)** <sub>Case study · Independent reconstruction</sub>

  Builds a native PC port on the existing GoldenEye 007 decompilation, with a host platform layer and assets extracted from the user’s ROM. The project documents agent collaboration, rendering comparisons, playtest scope and unresolved platform support.

- **[ssbu-recomp: static recompilation with explicit mode limits](https://github.com/Denkishi/ssbu-recomp)** <sub>Case study · Independent reconstruction</sub>

  Translates Super Smash Bros. Ultimate 13.0.4 AArch64 code ahead of time and supplies a Windows runtime with Vulkan/OpenGL rendering. It also reconstructs selected fighter scripts as editable C++ and compares translated/source behavior through differential and deterministic tests.

- **[KartPad: platform integration for a Mario Kart Wii recompilation](https://github.com/chrissotraidis/kartpad)** <sub>Case study · Independent reconstruction</sub>

  Builds Apple and Android integration around WiiCompiled’s ahead-of-time translation of Mario Kart Wii, with native graphics, input and optional Retro Rewind support. Its status and rights documents distinguish platform acceptance, unresolved device defects and game-content requirements.

- **[BattleShip: an AI-assisted Super Smash Bros. native port](https://github.com/vinvirile/BattleShip)** <sub>Case study · Independent reconstruction</sub>

  Ports the existing Super Smash Bros. N64 decompilation using libultraship and Torch. The author describes agent-built graphics/audio comparison tools and differential debugging against emulator behavior, rather than claiming AI recovered the game from a cartridge without prior community work.

- **[Agent decompilation: a byte-matching retrospective](https://momo5502.com/posts/2026-10-09-game-decompilation/)** <sub>Case study · Independent reconstruction</sub>

  Maurice Heumann describes replacing plausible-looking agent output with compiler-based checks of reconstructed functions, relocations, data and types. The retrospective reports 99% function presence and 83% of all functions byte-exact, while keeping the reconstruction code private.

- **[IsaacRecomp: translating Flash game bytecode to native C++](https://github.com/whylurking/IsaacRecomp)** <sub>Case study · Independent reconstruction</sub>

  Translates The Binding of Isaac’s Flash AVM1 bytecode into C++ functions and supplies a native rendering/input runtime. The project reads graphics and audio from the user’s original game and documents deterministic input, headless runs and screenshot regression checks.

- **[Nanolathe: a documented Total Annihilation engine reimplementation](https://github.com/nanolathe-gg/nanolathe)** <sub>Case study · Independent reconstruction</sub>

  Reimplements a Total Annihilation-compatible strategy-game engine in Go, with public file-format research and separate gameplay profiles. It distinguishes intended retail 3.1 behavior from community-patch research and deliberate modern changes, and separates synthetic checks from tests requiring original game data.

- **[RenderDoc](https://github.com/baldurk/renderdoc)** <sub>Tool</sub>

  Inspect frame captures, draw calls, shaders, and graphics resources in your own game or graphics application.

- **[AssetRipper](https://github.com/AssetRipper/AssetRipper)** <sub>Tool</sub>

  Analyze Unity game files, inspect asset dependencies, and convert supported assets into Unity project formats.

- **[Cpp2IL](https://github.com/SamboyCoding/Cpp2IL)** <sub>Tool</sub>

  Recover managed representations from Unity IL2CPP builds using binary and metadata analysis; reconstruction remains a work in progress.

- **[Il2CppDumper](https://github.com/Perfare/Il2CppDumper)** <sub>Tool</sub>

  Recover IL2CPP metadata and dummy assemblies, and generate helper scripts for native analysis tools; method code is not restored.

- **[RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp)** <sub>Integration · Independent MCP</sub>

  Expose existing RenderDoc captures to an agent for bounded frame, pipeline, resource, and shader inspection.

- **[UndertaleModTool](https://github.com/UnderminersTeam/UndertaleModTool)** <sub>Tool</sub>

  Browse and modify supported GameMaker data files, extract assets, and decompile or compile GML VM code. Includes room editing, scripted changes, a CLI, and the reusable UndertaleModLib library.

- **[frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge)** <sub>Tool</sub>

  Inspect IL2CPP classes, methods, and fields in a live process, and trace or intercept method calls without supplying global-metadata.dat. Complements static IL2CPP dumpers with runtime observation.

- **[objdiff](https://github.com/encounter/objdiff)** <sub>Tool</sub>

  Compare functions and data in reference and rebuilt object files to guide matching decompilation. Displays instruction-level differences, demangles C++ symbols, and can rebuild when source files change.

- **[UE Explorer](https://github.com/UE-Explorer/UE-Explorer)** <sub>Tool</sub>

  Explore Unreal packages through class, property, and dependency trees; decompile and export UnrealScript classes, inspect bytecode, and examine structured binary data.

- **[GARbro](https://github.com/morkt/GARbro)** <sub>Tool</sub>

  Browse recognized visual-novel resource archives as folders, preview their contents, and extract images or audio with conversion to common formats.

- **[LASRecomp: Link’s Awakening static recompilation](https://github.com/peiikai/LASRecomp)** <sub>Case study · Independent reconstruction</sub>

  A native desktop reconstruction of the 2019 Switch version of Link’s Awakening using static recompilation. The author attributes most code, tooling and reverse-engineering work to Claude Code with human direction and review.

- **[Godot RE Tools](https://github.com/GDRETools/gdsdecomp)** <sub>Tool</sub>

  Recover supported Godot project files, GDScript and imported resources from exported games. Includes PCK inspection and extraction, script decompilation, and resource conversion for examining and rebuilding project structure.

- **[UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)** <sub>Tool</sub>

  Inspect Unreal Engine games at runtime through live UObject property views, reflected C++ header dumps, property mappings and actor dumps. Lua and C++ APIs support experiments while reconstructing game structures.

- **[FModel](https://github.com/4sval/FModel)** <sub>Tool</sub>

  Explore Unreal Engine game archives with CUE4Parse-backed package and property inspection, asset previews and export. The 2026 summer release adds USD world export for reconstructing supported scene content.

- **[PSP Web Recomp](https://github.com/snuri00/psp-web-recomp)** <sub>Project</sub>

  Translate PSP MIPS executables into C++ and WebAssembly, backed by a PSP high-level emulation runtime and WebGL2 renderer. Native tracing, frame capture and audio tools support investigating missing behavior during game porting.

- **[ArkWeb: a two-game movement and collision experiment](https://github.com/luki-1/ArkWeb)** <sub>Case study · Independent reconstruction</sub>

  Runs Spider-Man Remastered and Arkham Knight together, streaming Gotham collision into Spider-Man’s physics world and compositing his rendered frame into Arkham. This experimental runtime bridge is not a recovered standalone game or new engine.

<a id="app"></a>
### App

[↑ Contents](#contents)

- **[Aegis: trace a login-code calculation](https://rea.tools/showcase/aegis/)** <sub>Case study · REA</sub>

  An official APK investigation follows TOTP methods in Aegis and publishes artifact identities and selected Evidence.

- **[Notion: trace the clipboard bridge](https://rea.tools/showcase/notion/)** <sub>Case study · REA</sub>

  Trace a packaged Electron clipboard path using REA findings and separate source inspection; the dynamic wrapper remains a stated limit.

- **[ReaCut: video-editor reconstruction](https://github.com/Xiangyu-CAS/rea-capcut)** <sub>Case study · Mixed workflow</sub>

  An independent video editor whose authors document REA-assisted investigation of Jianying/CapCut behavior and project formats. The public implementation includes a local timeline, FFmpeg export and an experimental, lossy draft importer.

- **[zee-rp: reconstructing supported Axure RP 11 document operations](https://github.com/LilZeeCN/zee-rp)** <sub>Case study · Independent reconstruction</sub>

  Reads and rewrites supported native Axure RP 11 documents through a binary-record codec, reference-aware cloning and constrained interaction writers. CLI and MCP interfaces expose inspected edits while keeping offline structure checks separate from native application acceptance.

- **[Virtual Desktop Streamer: rehosting the platform layer on Linux](https://github.com/cudanexus/vd-streamer-linux)** <sub>Case study · Mixed workflow</sub>

  An author-reported Claude Code and REA workflow replaces the macOS streamer’s capture, encoding, audio and input layer with Linux implementations while reusing vendor protocol libraries. The documented result targets desktop streaming and video playback, not Windows-only VR game streaming.

- **[Open Claude UI: REA-informed interface reference components](https://github.com/Caho1/open-claude-ui)** <sub>Case study · Mixed workflow</sub>

  Publishes React components, motion helpers and design-system notes derived from the author’s reported REA investigation of Claude Desktop. It is useful as an interface-reconstruction case, with version-specific observations rather than proof of a complete assistant application or backend clone.

- **[JADX-AI-MCP](https://github.com/zinja-coder/jadx-ai-mcp)** <sub>Integration · Independent MCP</sub>

  JADX plugin paired with a Python MCP server to inspect decompiled Android classes, resources, cross-references and debugger context.

- **[frida-mcp (yfe404)](https://github.com/yfe404/frida-mcp)** <sub>Integration · Independent MCP</sub>

  Frida MCP server with persistent instrumentation sessions, runtime inspection and Android static-to-dynamic navigation.

- **[Super Trouper](https://github.com/crissyfield/super-trouper)** <sub>Integration · Independent MCP</sub>

  Single-binary Frida MCP server for discovering devices, managing process sessions and loading instrumentation scripts.

- **[Frida](https://github.com/frida/frida)** <sub>Tool</sub>

  Dynamic instrumentation toolkit for observing and scripting the behavior of live native and managed processes.

- **[JADX](https://github.com/skylot/jadx)** <sub>Tool · Android</sub>

  Dex-to-Java decompiler with CLI/GUI navigation, resource decoding and cross-reference search for Android packages.

- **[Apktool](https://github.com/iBotPeaches/Apktool)** <sub>Tool · Android</sub>

  Decodes Android resources and smali into a project-like tree and can rebuild modified packages.

- **[Androguard](https://github.com/androguard/androguard)** <sub>Tool · Android</sub>

  Python toolkit for APK/DEX metadata, bytecode and reference analysis; the v5 source branch also documents agent skills and MCP.

- **[ILSpy](https://github.com/icsharpcode/ILSpy)** <sub>Tool · .NET</sub>

  .NET assembly browser and C# decompiler with whole-project export, metadata inspection and a scriptable command-line frontend.

- **[dnSpyEx](https://github.com/dnSpyEx/dnSpy)** <sub>Tool · .NET</sub>

  Community continuation of dnSpy for debugging and editing .NET assemblies without the original source.

- **[@electron/asar](https://github.com/electron/asar)** <sub>Tool</sub>

  Electron's archive tool lists and extracts ASAR contents so packaged JavaScript and application assets can be inspected.

- **[Mobile Security Framework (MobSF)](https://github.com/MobSF/Mobile-Security-Framework-MobSF)** <sub>Tool · Android</sub>

  Inspect mobile application packages with static analysis and supported-device dynamic testing, including runtime behavior and network traffic, through a web interface and APIs.

- **[Blutter](https://github.com/worawit/blutter)** <sub>Tool · Android</sub>

  Analyze Flutter Android ARM64 AOT binaries using the matching Dart runtime. Produces annotated assembly, object-pool dumps and a target-specific Frida script template for investigating compiled Dart application logic.

- **[hermes-dec](https://github.com/P1sec/hermes-dec)** <sub>Tool</sub>

  Parse, disassemble and partially decompile React Native Hermes bytecode bundles. Makes HBC headers and instructions inspectable and emits pseudocode for understanding compiled application logic.

- **[Recaf](https://github.com/Col-E/Recaf)** <sub>Tool · JVM</sub>

  Inspect and modify compiled JVM applications with integrated decompilers, bytecode assembly, reference search, mappings and deobfuscation tools. The reviewed 4.0 preview also provides basic read-only Android bytecode inspection.

- **[nibkit](https://github.com/tokenbleed/nibkit)** <sub>Tool</sub>

  Decode compiled iOS/macOS interface archives into object trees, Outlet/Action connections, custom classes and navigation relationships. Exports JSON or Mermaid diagrams and exposes read-only inspection commands through MCP.

- **[AOTopsy](https://github.com/BroNils/aotopsy)** <sub>Tool · Android</sub>

  Statically inspect Flutter/Dart AOT libapp.so files to recover available metadata, class structures, call edges and pseudocode without embedding a Dart VM or compiling a matching SDK. Supports ARM64 and x86_64 analysis paths.

- **[hbctool](https://github.com/bongtrop/hbctool)** <sub>Tool · Android</sub>

  Disassemble and reassemble supported React Native Hermes bytecode bundles through HASM files, enabling bytecode inspection and editing for the explicitly supported legacy HBC versions.

- **[LSX II Volume Fixer: reconstructing volume behavior](https://github.com/roberdorfer/kef-lsx-volume)** <sub>Case study · Independent reconstruction</sub>

  Uses measured USB-volume behavior and a macOS audio proxy to map volume keys to a KEF LSX II’s LAN control. The project reports more even steps while forwarding USB audio; the speaker firmware is unchanged.

<a id="native-binary"></a>
### Native Binary

[↑ Contents](#contents)

- **[DownUnderCTF: masked-squares flag checker](https://rea.tools/showcase/ctf/)** <sub>Case study · REA</sub>

  An official educational challenge investigation connects binary checks to equations and records an original-program validation.

- **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)** <sub>Tool</sub>

  Open-source analysis suite for disassembly, decompilation, graphs and Java/Python automation across executable formats.

- **[radare2](https://github.com/radareorg/radare2)** <sub>Tool</sub>

  Scriptable command-line framework for inspecting, disassembling, debugging and modifying binaries across many architectures.

- **[Cutter](https://github.com/rizinorg/cutter)** <sub>Tool</sub>

  Rizin-powered graphical reverse-engineering workspace with extensible views and Ghidra decompiler integration.

- **[Qiling](https://github.com/qilingframework/qiling)** <sub>Tool</sub>

  Python emulation framework that adds OS, filesystem and API behavior around CPU emulation for instrumented binary analysis.

- **[Unicorn Engine](https://github.com/unicorn-engine/unicorn)** <sub>Tool · Library</sub>

  Multi-architecture CPU emulator for executing selected instruction ranges with register, memory and hook control.

- **[angr](https://github.com/angr/angr)** <sub>Tool · Library</sub>

  Python binary-analysis framework combining control-flow recovery, symbolic execution, data-flow analysis and decompilation.

- **[LIEF](https://github.com/lief-project/LIEF)** <sub>Tool · Library</sub>

  Library for structured parsing and modification of executable formats including ELF, PE and Mach-O.

- **[Capstone](https://github.com/capstone-engine/capstone)** <sub>Tool · Library</sub>

  Disassembly library with architecture-neutral APIs and instruction details for custom binary-analysis pipelines.

- **[ImHex](https://github.com/WerWolv/ImHex)** <sub>Tool</sub>

  Hex editor with a binary-pattern language, structured data inspection and visual tools for understanding file formats.

- **[x64dbg](https://github.com/x64dbg/x64dbg)** <sub>Tool</sub>

  Windows binary debugger with disassembly, memory views and plugins for analyzing programs without source code.

- **[GDB](https://sourceware.org/gdb/)** <sub>Tool</sub>

  Native and remote debugger for controlling execution and inspecting live or crashed program state.

- **[rr](https://github.com/rr-debugger/rr)** <sub>Tool</sub>

  Records process execution and replays it under GDB, enabling repeatable inspection and reverse execution.

- **[Diaphora](https://github.com/joxeankoret/diaphora)** <sub>Tool</sub>

  IDA-based binary diffing that matches functions and transfers names, comments and types between analyzed versions.

- **[BinDiff](https://github.com/google/bindiff)** <sub>Tool</sub>

  Compares disassembled binaries to find matching functions and changed code across versions.

- **[Detect It Easy](https://github.com/horsicq/Detect-It-Easy)** <sub>Tool</sub>

  Format-aware file identification and static inspection using parsers, signatures and programmable heuristics.

- **[objection](https://github.com/sensepost/objection)** <sub>Tool</sub>

  Explore running Android and iOS apps with a Frida-backed command interface for inspecting app storage, memory, runtime objects, and instrumented behavior.

- **[r2frida](https://github.com/nowsecure/r2frida)** <sub>Tool</sub>

  Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.

- **[Kaitai Struct](https://github.com/kaitai-io/kaitai_struct)** <sub>Tool · Library</sub>

  Turn documented binary layouts into reusable parsers for files and network packets. A .ksy specification can be inspected with visualizers and compiled to multiple languages, helping preserve reverse-engineered format knowledge in interoperable implementations.

- **[Wireshark](https://gitlab.com/wireshark/wireshark)** <sub>Tool</sub>

  Inspect captured application and device traffic as decoded protocol fields, with filtering and shared GUI/TShark dissection. Custom dissectors let an analyst encode newly understood packet formats and compare protocol implementations.

<a id="firmware"></a>
### Firmware and Hardware

[↑ Contents](#contents)

- **[PicoPrint: LX-D02 printer investigation](https://github.com/bigtower17/picoprint)** <sub>Case study · Mixed workflow</sub>

  The author describes REA-assisted Android investigation followed by separate Hermes decompilation to support a Windows BLE printer.

- **[Binwalk](https://github.com/ReFirmLabs/binwalk)** <sub>Tool</sub>

  Identifies embedded formats and optionally extracts their contents, with entropy analysis for firmware triage.

- **[unblob](https://github.com/onekey-sec/unblob)** <sub>Tool</sub>

  Recursively extracts archives and filesystems from binary blobs while reporting chunk boundaries and unknown regions.

- **[Ghidra Firmware Utilities](https://github.com/al3xtjames/ghidra-firmware-utils)** <sub>Tool</sub>

  Ghidra loaders and helpers for PCI option ROMs, UEFI firmware volumes, Intel flash descriptors and coreboot images.

- **[EMBA](https://github.com/e-m-b-a/emba)** <sub>Tool</sub>

  Extract firmware, combine static checks with emulation-based analysis, inventory software components, and generate web reports and SBOMs for further investigation.

- **[Firmware Analysis and Comparison Tool (FACT)](https://github.com/fkie-cad/FACT_core)** <sub>Tool</sub>

  Unpack and analyze firmware through an extensible platform whose web interface and HTTP API make component contents and analysis results searchable and comparable across samples.

- **[OFRAK](https://github.com/redballoonsecurity/ofrak)** <sub>Tool</sub>

  Recursively identify, unpack, analyze, modify, and repack firmware and binary formats using a resource-tree GUI and Python API, with optional disassembler backends.

- **[FirmAE](https://github.com/pr0v3rbs/FirmAE)** <sub>Tool</sub>

  Emulate router and IP-camera firmware to inspect network services and runtime behavior, with automated emulation checks and separate analysis, run, and debugging modes.

- **[PulseView](https://github.com/sigrokproject/pulseview)** <sub>Tool</sub>

  Examine captured logic and analog waveforms with sigrok's graphical frontend. Protocol decoders and decoder stacking expose bus messages and higher-level device operations, making hardware communication traces useful for firmware and interoperability investigations.

- **[UEFITool](https://github.com/LongSoft/UEFITool)** <sub>Tool</sub>

  Parse UEFI firmware images into an inspectable tree and check their structure. Companion UEFIExtract and UEFIFind tools extract parsed contents and locate patterns, supporting analysis of firmware components and vendor formats.

<a id="protocol"></a>
### Protocols

[↑ Contents](#contents)

- **[open-appleremote: Siri Remote protocol reconstruction](https://github.com/a-funk/open-appleremote)** <sub>Case study · Independent reconstruction</sub>

  Reconstructs first-generation Siri Remote Bluetooth reports for Linux, decoding buttons, touch and tvOS-style gestures. The Python implementation and protocol notes distinguish measured behavior, historical reports and inferred meanings.

- **[GAMEKB-K17: reconstructing a macropad configuration protocol](https://github.com/dvdarkin/gamekb-k17)** <sub>Case study · Independent reconstruction</sub>

  Implements the vendor HID configuration protocol for the GAMEKB-K17/HCY-K017 macropad. It writes key mappings, firmware macros and RGB settings, then reads them back; protocol notes separate tested commands from unconfirmed observations and other-device findings.

- **[CF632BLE: a local client from scale-protocol research](https://github.com/guyru/cf632ble)** <sub>Case study · Independent reconstruction</sub>

  Reimplements the CF632BLE scale’s BLE protocol and body-composition calculations from research on the vendor’s Unique Health Android app. A static Web Bluetooth client receives measurements, manages device profiles and keeps its history in browser storage.

- **[cooler-lcd: a Thermalright display protocol implementation](https://github.com/kristjaningi/cooler-lcd)** <sub>Case study · Independent reconstruction</sub>

  Implements a USB picture-transfer driver for Thermalright Vision cooler displays, with a Rust dashboard replacing the vendor display application. The documented protocol sends a header and JPEG frames, with periodic resends to prevent the device reverting to its logo.

- **[hw-harness: scanner USB protocol investigation](https://github.com/cschalle/hw-harness)** <sub>Case study · Independent reconstruction</sub>

  Documents an author-reported scanner investigation comparing vendor-driver USB control transfers with Linux-driver traces to infer initialization, timing and resolution parameters. The released harness organizes reference capture and comparison; it does not automatically recover a complete protocol specification.

- **[Netzob](https://github.com/netzob/netzob)** <sub>Tool</sub>

  Model communication protocols and infer message layouts from traces, with configured active learning for protocol state machines. Python APIs expose message fields, symbols and automata for parsing, traffic generation and fuzzing.

- **[Scapy](https://github.com/secdev/scapy)** <sub>Tool</sub>

  Script packet dissection, construction, request/reply matching and capture-file analysis in Python. Custom packet fields and layer bindings let analysts encode understood wire formats and investigate protocol behavior.

<a id="agents-and-mcp"></a>
### Agents and MCP

[↑ Contents](#contents)

- **[REA — Reverse Engineer Anything](https://github.com/morluto/rea)** <sub>Project · REA</sub>

  The upstream CLI and MCP server for evidence-based investigations of shipped software and runtime behavior.

- **[Official reverse-engineer-anything skill](https://github.com/morluto/rea/tree/main/.agents/skills/reverse-engineer-anything)** <sub>Integration · REA</sub>

  Target routing, connection recovery and evidence practices for agents using REA.

- **[dsh-mcp-rea](https://github.com/Ersith/dsh-mcp-rea)** <sub>Integration · REA</sub>

  A community MCP bridge presents a smaller selected tool surface and forwards explicit commands to the REA CLI.

- **[rea-jev](https://github.com/juan-viox/rea-jev)** <sub>Integration · REA</sub>

  A Claude Code plugin adds Jev-based routing and evidence checks around a pinned REA MCP integration.

- **[rea-casebook](https://github.com/pablodiazjorge/rea-casebook)** <sub>Integration · REA</sub>

  A Claude Code mod collects received REA Evidence, tracks unknowns and records findings that cite delivered evidence IDs.

- **[Hex-Rays IDA MCP](https://github.com/HexRaysSA/ida-mcp)** <sub>Integration · Independent MCP</sub>

  Official Hex-Rays MCP server for agent access to IDA databases, with headless operation and optional GUI integration.

- **[GhidraMCP](https://github.com/LaurieWired/GhidraMCP)** <sub>Integration · Independent MCP</sub>

  Ghidra extension and MCP bridge exposing decompilation, symbol navigation and renaming to agents, with GUI and headless modes.

- **[Binary Ninja MCP (official)](https://dev-docs.binary.ninja/guide/mcp.html)** <sub>Integration · Independent MCP</sub>

  Binary Ninja's own MCP interface exposes functions, symbols, disassembly, intermediate languages and decompiled text to agents.

- **[Binary Ninja MCP (fosdickio)](https://github.com/fosdickio/binary_ninja_mcp)** <sub>Integration · Independent MCP</sub>

  Community Binary Ninja plugin and bridge for MCP clients, including workflows that switch among multiple open binaries.

- **[IDA Pro MCP (mrexodia)](https://github.com/mrexodia/ida-pro-mcp)** <sub>Integration · Independent MCP</sub>

  Community IDA integration useful for existing setups and migration context; its maintainer now recommends the official Hex-Rays MCP server.

- **[Radare2 MCP Server](https://github.com/radareorg/radare2-mcp)** <sub>Integration · Independent MCP</sub>

  Native radare2 MCP server offering binary-analysis tools, reusable sessions and configurable read-only access.

- **[r2ai](https://github.com/radareorg/r2ai)** <sub>Integration · Independent agent</sub>

  AI plugins inside radare2 for function explanations, naming suggestions and model-assisted decompilation using local or remote models.

- **[DAILA](https://github.com/mahaloz/DAILA)** <sub>Integration · Independent agent</sub>

  Decompiler-independent AI assistant for function summaries and naming across IDA, Ghidra, Binary Ninja and angr-management.

- **[RevEng.AI Ghidra Plugin](https://github.com/RevEngAI/plugin-ghidra)** <sub>Integration · Independent agent</sub>

  Connects Ghidra to RevEng.AI for function similarity, recovered names, AI explanations and agent-assisted annotation.

- **[LLDB MCP](https://lldb.llvm.org/use/mcp.html)** <sub>Integration · Independent MCP</sub>

  LLDB's official MCP interface gives agents debugger sessions and commands for breakpoints, memory inspection and stepping.

- **[Claude Reverse Engineering Skill](https://github.com/EncidXVII/claude-reverse-engineering-skill)** <sub>Integration · Independent agent</sub>

  Community agent skill for triage, headless exports and evidence-based RE reports; explicitly documents workflows with REA and other MCP servers.

- **[SpecterOps Reverse Engineering Skills](https://github.com/SpecterOps/skills/tree/main/plugins/reverse-engineering)** <sub>Integration · Independent agent</sub>

  Focused Binary Ninja and Ghidra analysis skills that describe MCP tool use, analysis recipes and annotation practices.

<a id="related-collections"></a>
### Related Collections

[↑ Contents](#contents)

- **[Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering)** <sub>Collection</sub>

  A task-oriented reverse-engineering resource list by REA's maintainer, useful for broader tools and foundations.

- **[Awesome REA Cases](https://github.com/songshikang0111/awesome-REA-cases)** <sub>Collection</sub>

  A bilingual collection of REA and other AI-assisted reverse engineering cases, with source links and explicit distinctions between reported and reproduced outcomes.

- **[awesome-rea (yibie): verification-focused projects and practice reports](https://github.com/yibie/awesome-rea)** <sub>Collection</sub>

  Organizes AI-assisted game decompilation, native ports, static recompilation and tooling around stated acceptance checks, alongside a separate track of practitioner write-ups and discussions. Useful for finding primary reports and comparing how projects define correctness.

- **[Awesome REA/Decompiled Games](https://github.com/HaozheH3/awesome-rea-games)** <sub>Collection</sub>

  Groups game decompilations, source reconstructions, recompilations, native ports and demos by original game, with comparison rows linking related projects. It distinguishes launchers, engine work and creator-shared showcases from source-reconstruction efforts.

<a id="references-and-learning"></a>
### References and Learning

[↑ Contents](#contents)

- **[Installation and client setup](https://github.com/morluto/rea/blob/main/docs/installation.md)** <sub>Documentation · REA</sub>

  Reviewed setup plans, client registration, provider prerequisites and scoped readiness checks.

- **[CLI and Evidence](https://github.com/morluto/rea/blob/main/docs/cli.md)** <sub>Documentation · REA</sub>

  CLI workflows for saving Evidence and projecting smaller views from completed analysis.

- **[MCP contracts and generated catalog](https://github.com/morluto/rea/blob/main/docs/mcp-contracts.md#generated-catalog)** <sub>Documentation · REA</sub>

  Canonical tool contracts, provider discovery and Evidence semantics for integration authors.

- **[Native binary investigation](https://github.com/morluto/rea/blob/main/docs/native-investigation.md)** <sub>Documentation · REA</sub>

  Locate a function, inspect instructions and pseudocode, and follow references with a selected native provider.

- **[Cross-layer JavaScript application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md)** <sub>Documentation · REA</sub>

  Trace features and compare authenticated JavaScript application graphs while preserving static-analysis limits.

- **[Static Android APK analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)** <sub>Documentation · REA</sub>

  Inspect Android package identity, classes, methods and references through REA's JADX integration.

- **[Managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md)** <sub>Documentation · REA</sub>

  Read PE/CLI metadata and CIL, compare managed members and inspect declared native boundaries without loading the assembly.

- **[Historical web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md)** <sub>Documentation · REA</sub>

  Inspect saved web captures offline; recorded URLs are not fetched and no proxy is started.

- **[Firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md)** <sub>Documentation · REA</sub>

  Inspect firmware regions with Binwalk and explicitly extract with Unblob, retaining tool and artifact identity.

- **[Browser observation guide](https://rea.tools/guides/browser/)** <sub>Documentation · REA</sub>

  Follow a user-triggered export request in the supplied Notes browser example and connect it to the downloaded result.

- **[JavaScript and Electron: follow a CSV export](https://rea.tools/guides/javascript/)** <sub>Documentation · REA</sub>

  A source-owned Notes fixture teaches the renderer, preload, IPC and CSV path with linked analysis evidence.

- **[rea-playbook](https://github.com/jinshi666888/rea-playbook)** <sub>Learning resource</sub>

  An Electron practice target, Evidence extractor and MCP probe; offline fixture mode is distinguished from real REA analysis.

- **[rea-lab](https://github.com/pablodiazjorge/rea-lab)** <sub>Research</sub>

  A Windows REA/Ghidra lab with seeded challenges, published studies, upstream contributions and recorded limitations.

- **[OpenSecurityTraining2](https://ost2.fyi/)** <sub>Learning resource</sub>

  Free self-paced security courses with learning paths for reverse engineering, firmware and systems foundations.

- **[pwn.college: Reverse Engineering](https://pwn.college/program-security/reverse-engineering/)** <sub>Learning resource</sub>

  Hands-on reverse-engineering module covering functions, data access, static tools and dynamic tools with hosted exercises.

- **[Reverse Engineering for Beginners](https://beginners.re/)** <sub>Learning resource</sub>

  Dennis Yurichev's free book on understanding compiled programs and assembly, available in multiple languages.

- **[The Official Radare2 Book](https://book.rada.re/)** <sub>Learning resource</sub>

  Official practical reference for radare2 analysis, disassembly, scripting, debugging and related plugins.

- **[LLM4Decompile (EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.203/)** <sub>Research</sub>

  Research on direct binary decompilation and refinement of Ghidra output with language models. Evaluates re-executability on HumanEval and ExeBench; useful for distinguishing readable output from functional recovery.

- **[DecompileBench (Findings of ACL 2025)](https://aclanthology.org/2025.findings-acl.1194/)** <sub>Research</sub>

  A benchmark combining functions from real programs, runtime-aware validation, and LLM-assisted assessment of decompiled-code usability. Helps separate functional correctness from perceived understandability when comparing decompilers.

- **[ReSym (CCS 2024)](https://doi.org/10.1145/3658644.3670340)** <sub>Research</sub>

  Combines language models and program analysis to recover variable and user-defined data-structure symbols from stripped binaries. The authors provide training, inference, evaluation, and posterior-reasoning artifacts.
<!-- END GENERATED CATALOG -->

<!-- BEGIN GENERATED PAPERS -->
<a id="papers"></a>
## Papers

A bibliography of **31 papers** on reverse-engineering agent evaluation, decompilation, protocol inference, firmware analysis, and website, game, and app reconstruction. Some papers also appear among curated resources; counts are not additive. Publication status and study scope are made explicit.

[Browse the paper directory](https://awesomerea.org/papers/) · [Complete bibliography JSON](data/papers.json) · [Suggest a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml)

### Reverse-engineering agent evaluation

- [Humans vs. Machines: A Comparison With AI Agents in Software Reverse Engineering](https://arxiv.org/abs/2610.14960) — **2026 · arXiv · Preprint**

    Samuele Doria et al. · [PDF](https://arxiv.org/pdf/2610.14960)

    Compares human and LLM-agent understanding and navigation on the same static reverse-engineering challenges, then studies how binary representations consume context windows.

    **Scope and limits:** Understanding is graded on two compact challenges; the separate 4,000-binary study measures context capacity, not task-solving accuracy. The interface is static IDA/MCP without dynamic execution, and prior exposure to challenge source remains an acknowledged validity threat.

- [The Next Challenge for Agentic Cybersecurity: A Realistic, Contamination-Free Reverse Engineering Benchmark](https://arxiv.org/abs/2608.11469) — **2026 · arXiv · Preprint**

    Jeremy Spence et al. · [PDF](https://arxiv.org/pdf/2608.11469)

    Introduces SRE-Bench, with privately authored programs and protected binary variants, to study agent recovery of program semantics while reducing training-data contamination.

    **Scope and limits:** The revised study reports 19 programs, 262 binary instances, and 1,572 graded tasks. Binaries and task instances are not publicly released; access is through an evaluation service. Its contamination-control claim is the authors' methodology, not an independent guarantee.

- [CrackMeBench: Binary Reverse Engineering for Agents](https://arxiv.org/abs/2605.10597) — **2026 · arXiv · Preprint**

    Isaac David et al. · [PDF](https://arxiv.org/pdf/2605.10597)

    Evaluates agents on executable-checked CrackMe tasks: infer validation logic from binaries and submit an accepted input or artifact, while recording tool use, time, and scoring attempts.

    **Scope and limits:** The v0 study uses 12 generated tasks and eight public calibration tasks, Linux x86-64 ELF binaries, a shell interface, and a five-minute budget. Its compact educational tasks do not establish performance on large applications. No paper-linked public artifact URL was verified.

- [ProgramBench: Can Language Models Rebuild Programs From Scratch?](https://arxiv.org/abs/2605.03546) — **2026 · NeurIPS 2026 · Accepted**

    John Yang et al. · [PDF](https://arxiv.org/pdf/2605.03546v1) · [Code](https://github.com/facebookresearch/ProgramBench)

    Evaluates black-box program reconstruction across 200 tasks: agents query an executable and read its documentation, then independently implement a codebase whose behavior is checked by generated tests.

    **Scope and limits:** Binary inspection, decompilation, and internet access are forbidden during inference. Passing finite tests does not prove complete behavioral equivalence or recovery of the original source. Later live-leaderboard runs are separate from the reviewed arXiv results.

- [CREBench: Evaluating Large Language Models in Cryptographic Binary Reverse Engineering](https://arxiv.org/abs/2604.03750) — **2026 · COLM 2026 · Accepted**

    Baicheng Chen et al. · [PDF](https://arxiv.org/pdf/2604.03750) · [Code](https://github.com/wangyu-ovo/CREBench)

    Benchmarks cryptographic binary reverse engineering across algorithm recognition, key or IV extraction, wrapper reconstruction, and flag recovery using 432 controlled challenges.

    **Scope and limits:** The corpus combines 48 algorithms, three insecure key-use scenarios, and three difficulty levels. It excludes professional-grade obfuscators such as Tigress and O-LLVM; results should not be generalized to heavily protected arbitrary binaries.

### Decompilation and symbol recovery

- [DecompileBench: A Comprehensive Benchmark for Evaluating Decompilers in Real-World Scenarios](https://aclanthology.org/2025.findings-acl.1194/) — **2025 · Findings of ACL 2025 · Conference paper**

    Zeyu Gao et al. · [PDF](https://aclanthology.org/2025.findings-acl.1194.pdf) · [Code](https://github.com/vul337/DecompileBench)

    Evaluates traditional and LLM-based decompilers using functions from real programs, runtime behavioral checks, and an LLM-assisted assessment of analyst-facing code understandability.

    **Scope and limits:** The evaluated corpus has 23,400 functions from 130 programs. Fuzzing-based checks have finite coverage, and understandability scores depend partly on an LLM judge. The artifact warns that rebuilt OSS-Fuzz projects can differ from the paper's versions.

- [Decompile-Bench: Million-Scale Binary-Source Function Pairs for Real-World Binary Decompilation](https://papers.nips.cc/paper_files/paper/2025/hash/079cf13ae174c31f148207d94d213bdc-Abstract-Datasets_and_Benchmarks_Track.html) — **2025 · NeurIPS 2025 Datasets and Benchmarks · Conference paper**

    Hanzhuo Tan et al. · [PDF](https://papers.nips.cc/paper_files/paper/2025/file/079cf13ae174c31f148207d94d213bdc-Paper-Datasets_and_Benchmarks_Track.pdf) · [Code](https://github.com/albertan017/LLM4Decompile)

    Introduces two million C/C++ binary-source function pairs using a Compile-Trace-Filter pipeline, with an evaluation suite spanning translated HumanEval/MBPP tasks and recent GitHub functions.

    **Scope and limits:** This is function-level decompilation. Re-execution tests cover HumanEval/MBPP; GitHub2025 provides no unit tests. Inlining can prevent one-to-one source correspondence, and the fine-tuning study uses 10% of the corpus. These results do not establish whole-program recovery.

- [LLM4Decompile: Decompiling Binary Code with Large Language Models](https://aclanthology.org/2024.emnlp-main.203/) — **2024 · EMNLP 2024 · Conference paper**

    Hanzhuo Tan et al. · [PDF](https://aclanthology.org/2024.emnlp-main.203.pdf) · [Code](https://github.com/albertan017/LLM4Decompile)

    Trains language models for assembly-to-C decompilation and for refining Ghidra pseudocode, evaluating whether recovered functions can be recompiled and executed correctly.

    **Scope and limits:** The paper limits its experiments to C on x86 and function-level benchmarks. Re-executability on sampled tests does not establish whole-program equivalence or recovery of the original source. Later repository releases are separate from the 2024 paper.

- [ReSym: Harnessing LLMs to Recover Variable and Data Structure Symbols from Stripped Binaries](https://doi.org/10.1145/3658644.3670340) — **2024 · ACM CCS 2024 · Conference paper**

    Danning Xie et al. · [PDF](https://www.cs.purdue.edu/homes/lintan/publications/resym-ccs24.pdf) · [Code](https://github.com/lt-asset/resym)

    Combines two fine-tuned language models with Prolog-based cross-function reasoning to infer local-variable symbols and user-defined data structures from stripped-binary decompilation.

    **Scope and limits:** The method depends on underlying decompilation and learned predictions over C/C++ data. Cross-checking reduces conflicting predictions but does not prove that recovered names or layouts match the unavailable source. The public artifact includes models, processed data, and evaluation code.

- [Augmenting Decompiler Output with Learned Variable Names and Types](https://www.usenix.org/conference/usenixsecurity22/presentation/chen-qibin) — **2022 · USENIX Security 2022 · Conference paper**

    Qibin Chen et al. · [PDF](https://arxiv.org/pdf/2108.06363) · [Code](https://github.com/CMUSTRUDEL/DIRTY)

    Introduces DIRTY, a Transformer model that recommends variable names and types from decompiled code and layout information, together with the DIRT corpus for training and evaluation.

    **Scope and limits:** The original pipeline is built around C programs and Hex-Rays output. Predicted names and types are learned hypotheses, not guaranteed original symbols. The published paper is from 2022, although its arXiv preprint first appeared in 2021.

- [DIRE: A Neural Approach to Decompiled Identifier Naming](https://arxiv.org/abs/1909.09029) — **2019 · ASE 2019 · Conference paper**

    Jeremy Lacomis et al. · [PDF](https://arxiv.org/pdf/1909.09029) · [Code](https://github.com/pcyin/dire)

    Combines lexical and structural information from decompiler output to predict meaningful variable names, with a training and evaluation corpus derived from compiled C projects.

    **Scope and limits:** This is learned identifier naming, not complete source reconstruction or an autonomous agent. Its reported results concern an x86-64 C corpus and depend on decompiler output. The original author repository is deprecated and points to a successor.

### Website reconstruction

- [Vision2Web: A Hierarchical Benchmark for Visual Website Development with Agent Verification](https://proceedings.mlr.press/v306/he26n.html) — **2026 · ICML 2026 · Conference paper**

    Zehai He et al. · [PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26n/he26n.pdf) · [Code](https://github.com/zai-org/Vision2Web)

    Benchmarks website development from visual prototypes and written requirements across 100 static-page, 66 interactive-frontend and 27 full-stack tasks, combining workflow-based functional checks with model-judged visual comparison.

    **Scope and limits:** The full-stack tier is specification-driven, not reconstruction solely by exploring a live website. Workflows test state management and CRUD outcomes, but finite agent judgments do not establish exact backend or durable-database equivalence. The current public evaluator maintains a browser session within each workflow and permits local business-API checks; this is not a universal persistence proof.

- [ProgramDistill: From Interactive Web Apps to Verifiable Reference-Guided SWE Tasks](https://arxiv.org/abs/2609.18805) — **2026 · arXiv · Preprint**

    Jeonghye Kim et al. · [PDF](https://arxiv.org/pdf/2609.18805v1) · [Code](https://huggingface.co/datasets/microsoft/ProgramDistill)

    Evaluates recovery of web-app behavior from a live reference with hidden source. It provides 4,063 feature-restoration tasks across 26 applications and a separate 12-application reconstruction setting, scored by replaying dependent browser workflows.

    **Scope and limits:** Tests cover finite, model-mined behaviors in self-contained apps, including SaaS clones. Persistence failures can be detected through replayed workflows, but passing does not establish all backend or database invariants. Evaluated agents receive structured browser observations without screenshots; visual fidelity is not measured. Public verifiers and reference solutions are not a contamination-resistant test set.

- [Dashboard2Code: Evaluating Multimodal Models on Reconstructing Interactive Dashboards](https://aclanthology.org/2026.acl-long.1750/) — **2026 · ACL 2026 · Conference paper**

    Tianhao Niu et al. · [PDF](https://aclanthology.org/2026.acl-long.1750.pdf) · [Code](https://github.com/nth2000/Dashboard2Code)

    Evaluates agents that actively explore a running dashboard and reconstruct its appearance and interaction logic. DashboardMimic provides 180 Plotly+Dash examples, with code-semantic analysis and dynamic interaction tests for the generated implementations.

    **Scope and limits:** Limited to Plotly+Dash dashboards, including model-augmented examples. Some settings expose DOM information and evaluation uses model judges. This is not a general backend-recovery benchmark. The linked dataset requires accepting access conditions and sharing contact information.

- [IWR-Bench: Can LVLMs reconstruct interactive webpage from a user interaction video?](https://proceedings.iclr.cc/paper_files/paper/2026/hash/55bfedfd31489e5ae83c9ce8eec7b0e1-Abstract-Conference.html) — **2026 · ICLR 2026 · Conference paper**

    Yang Chen et al. · [PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/55bfedfd31489e5ae83c9ce8eec7b0e1-Paper-Conference.pdf) · [Code](https://github.com/SIGMME/IWR-Bench)

    Tests reconstruction of interactive webpages from user-interaction videos and supplied static assets. Its 113 tasks replay annotated action sequences to assess visual fidelity and functional behavior across observed page states.

    **Scope and limits:** The required output is one HTML file; the paper explicitly instructs models to mock implied backend logic with static JavaScript data. Trajectory coverage and model-based judgments do not prove complete website or backend equivalence.

- [Interaction2Code: Benchmarking MLLM-based Interactive Webpage Code Generation from Interactive Prototyping](https://doi.org/10.1109/ASE63991.2025.00028) — **2025 · ASE 2025 · Conference paper**

    Jingyu Xiao et al. · [PDF](https://arxiv.org/pdf/2411.03292v3) · [Code](https://github.com/WebPAI/Interaction2Code)

    Benchmarks reconstruction of interactive webpages from screenshots before and after an interaction. The final study covers 127 webpages and 374 interactions, comparing rendered appearance, automated interaction checks, and human usability judgments.

    **Scope and limits:** The inputs specify individual interaction transitions, not autonomous exploration of a complete site. Its tests do not establish long-workflow, server-side, or original-source equivalence; a detectable interaction is not necessarily usable.

- [WebUIBench: A Comprehensive Benchmark for Evaluating Multimodal Large Language Models in WebUI-to-Code](https://aclanthology.org/2025.findings-acl.815/) — **2025 · Findings of ACL 2025 · Conference paper**

    Zhiyu Lin et al. · [PDF](https://aclanthology.org/2025.findings-acl.815.pdf)

    Diagnoses webpage-to-code capability through visual perception, HTML programming, image-to-HTML understanding, and screenshot reconstruction tasks. It separates underlying skills using question-answer pairs derived from real websites.

    **Scope and limits:** Primarily evaluates visual and HTML reconstruction skills. The paper includes a preliminary interaction study, not a full workflow or backend-equivalence benchmark. The official repository currently exposes README and images but not the evaluation scripts described in its instructions.

- [Design2Code: Benchmarking Multimodal Code Generation for Automated Front-End Engineering](https://aclanthology.org/2025.naacl-long.199/) — **2025 · NAACL 2025 · Conference paper**

    Chenglei Si et al. · [PDF](https://aclanthology.org/2025.naacl-long.199.pdf) · [Code](https://github.com/NoviScl/Design2Code)

    Evaluates reconstruction of frontend code from webpage screenshots using real-world reference pages, visual-element and layout metrics, and human assessment.

    **Scope and limits:** This is visual website reconstruction, not binary decompilation or recovery of backend behavior and interactive workflows. The main benchmark contains 484 webpages with placeholder images; code and data have separate licensing terms.

### Game reconstruction and reverse engineering

- [GameReplica: A Benchmark for Black-Box Visual Game Replication by Vision-Language Agents](https://arxiv.org/abs/2609.22308) — **2026 · arXiv · Preprint**

    Boyu Qiao et al. · [PDF](https://arxiv.org/pdf/2609.22308v1)

    Evaluates whether vision-language agents can infer hidden game rules through screenshots and active interaction, then build runnable single-file HTML replicas across 125 tasks from 25 web games, each with five difficulty levels.

    **Scope and limits:** The tasks cover rule-driven web puzzles and board games, not native or commercial game reconstruction. Rule, implementation, and visual scores use LLM judges and do not prove behavioral equivalence. The official site provides demos; a benchmark-code repository was not verified.

- [Tycho: Active Abstraction with Programmatic World Models for ARC-AGI-3](https://arxiv.org/abs/2607.28287) — **2026 · arXiv · Preprint**

    Jens Lehmann et al. · [PDF](https://arxiv.org/pdf/2607.28287v1) · [Code](https://github.com/NIMI-research/Tycho)

    Tycho constructs editable Python models of game state, transitions, rendering and outcomes from action/observation histories in unfamiliar ARC-AGI-3 games. It checks model predictions against recorded transitions and can use, repair or bypass these models during planning.

    **Scope and limits:** Evaluation uses one stochastic run per configuration on 25 public games and 183 levels; five games informed harness development. Models may abstain on cells or accept bounded rendering variants. Transition replay and game scores do not establish complete engine reconstruction, correct objectives, unseen-state fidelity, unseen-game generalization or run-to-run reliability; the agent can bypass modeling.

- [RevengeBench: Reverse Engineering Code-Space Policies from Behavioral Experiments](https://arxiv.org/abs/2606.26094) — **2026 · arXiv · Preprint**

    Babak Rahmani et al. · [PDF](https://arxiv.org/pdf/2606.26094v1) · [Code](https://github.com/bethgelab/revenge-bench)

    Tests whether agents can recover executable decision policies from behavioral traces and self-designed opponent probes, using 75 synthetic policies across five game arenas and measuring held-out action agreement and downstream competitive value.

    **Scope and limits:** The targets are fixed synthetic policies, not full games or adaptive adversaries. Agreement on finitely evaluated states does not uniquely identify source code, and some arenas have substantial variance. The public package omits some paper-only plotting and ablation suites; reproduction also needs CodeClash, a container runtime, and model access.

- [SPRITE: From Static Mockups to Engine-Ready Game UI](https://doi.org/10.1145/3772363.3798742) — **2026 · CHI EA 2026 (poster/extended abstract) · Conference paper**

    Yunshu Bai et al. · [PDF](https://baiyunshu.github.io/sprite.github.io/Source/chiea26-516.pdf)

    Transforms game-interface screenshots into editable engine assets through hierarchical YAML, visual grounding, asset extraction, and Unity UXML/USS synthesis, with evaluation on a curated game-UI benchmark and review by three senior UI/UX designers.

    **Scope and limits:** The generated interactions cover basic hover, toggle, and click behavior. Complex temporal and drag-and-drop logic remain outside scope, and translucent overlap or ambiguous diegetic layouts can fail. This is game-UI prototyping, not complete gameplay reconstruction; the official page still labels code as coming soon.

### App reconstruction and analysis

- [DeclarUI: Bridging Design and Development with Automated Declarative UI Code Generation](https://doi.org/10.1145/3715726) — **2025 · Proceedings of the ACM on Software Engineering · Journal article**

    Ting Zhou et al. · [PDF](https://xinyi-hou.github.io/files/zhou2024bridging.pdf) · [Code](https://github.com/security-pride/DeclarUI)

    Combines visual component extraction, multimodal models, page-transition graphs and iterative checks to reconstruct multi-page mobile UI code from designs or screenshots, evaluated with React Native, Flutter and ArkUI.

    **Scope and limits:** People review and correct the inferred navigation graph. Evaluation covers 50 five-page UI sets; transition coverage and compilation do not establish full business-logic or backend recovery. Framework results vary, and visual metrics imperfectly reflect perceived fidelity. Public scripts and data are available, but no project-level license was found at the reviewed commit.

- [Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps](https://doi.org/10.1109/TSE.2018.2844788) — **2020 · IEEE Transactions on Software Engineering · Journal article**

    Kevin Moran et al. · [PDF](https://arxiv.org/pdf/1802.02312v2)

    ReDraw turns screenshots or design mock-ups into native Android GUI prototypes by detecting components, classifying widget types with a CNN, and assembling a plausible view hierarchy with a data-driven nearest-neighbor method.

    **Scope and limits:** The implementation covers 15 Android component classes and one screen at a time; multiple screens require manual combination, and hierarchy construction is tied to the mined screen size. Evaluation concerns appearance and view hierarchy, not recovery of original app logic or backends. Screenshots and reconstructed mock-ups served as proxies for real design artifacts; results were not independently reproduced here.

- [pix2code: Generating Code from a Graphical User Interface Screenshot](https://doi.org/10.1145/3220134.3220135) — **2018 · EICS 2018 · Conference paper**

    Tony Beltramelli · [PDF](https://arxiv.org/pdf/1705.07962v2) · [Code](https://github.com/tonybeltramelli/pix2code)

    Learns screenshot-to-DSL generation for native Android XML, iOS Storyboards and web HTML/CSS interfaces, then compiles the DSL into platform UI code.

    **Scope and limits:** Evaluation uses synthetic screenshot/code pairs: 1,500 training and 250 test instances per platform. Reported accuracy concerns DSL tokens, not complete apps or behavior. Text labels are ignored; platform datasets train separate models using the same architecture. The task covers layout, components and relationships, not application logic or backend recovery. The repository describes an educational research prototype; its older dependencies were not runtime-tested.

- [From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation](https://doi.org/10.1145/3180155.3180240) — **2018 · ICSE 2018 · Conference paper**

    Chunyang Chen et al. · [PDF](https://chunyang-chen.github.io/publication/ui2code.pdf) · [Code](https://github.com/ccywch/UI2code)

    UI2code translates a mobile UI image into an Android component hierarchy and layout skeleton using a neural encoder-decoder. The paper evaluates structural prediction and a small developer study of implementing layouts from generated skeletons.

    **Scope and limits:** The output covers component types and hierarchy from a single image; detailed styling and text require developer work. Structural token accuracy and an eight-participant study on five screenshots do not establish complete visual fidelity, navigation, app logic or backend recovery. The main split is screenshot-based; a separate evaluation on 1,208 images from 20 unseen apps provides limited generalization evidence.

- [Reverse Engineering Mobile Application User Interfaces with REMAUI (T)](https://ieeexplore.ieee.org/abstract/document/7372013) — **2015 · ASE 2015 · Conference paper**

    Tuan Anh Nguyen et al. · [PDF](https://c.csallner.org/papers/nguyen15reverse.pdf) · [Code](https://github.com/soumikmohianuta/pixtoapp)

    Reconstructs native Android UI code from screenshots or design bitmaps using OCR, computer vision, and layout heuristics; evaluates visual similarity and view hierarchies on 488 screenshots from over 100 Android and iOS applications.

    **Scope and limits:** The output is Android UI code; iOS screenshots are inputs, not evidence of native iOS output. Original logic and backend behavior are not recovered, and multi-screen transitions were future work. OCR/layout heuristics can misidentify content. The linked REMAUI v2 repository has older dependencies and is not the exact verified 2015 artifact.

### Firmware analysis and rehosting

- [Fuzzware: Using Precise MMIO Modeling for Effective Firmware Fuzzing](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski) — **2022 · USENIX Security 2022 · Conference paper**

    Tobias Scharnowski et al. · [PDF](https://www.usenix.org/system/files/sec22-scharnowski.pdf) · [Code](https://github.com/fuzzware-fuzzer/fuzzware)

    Rehosts monolithic ARM Cortex-M firmware for fuzzing, using locally scoped symbolic execution to model memory-mapped I/O accesses and focus input mutations on values relevant to firmware logic.

    **Scope and limits:** The Cortex-M3/M4 artifact requires memory-map configuration and does not automatically model DMA. Abstracting hardware can produce crashes that are impossible on the physical device. This is an analysis environment, not original-source recovery or faithful full-device reconstruction.

- [FirmAE: Towards Large-Scale Emulation of IoT Firmware for Dynamic Analysis](https://doi.org/10.1145/3427228.3427294) — **2020 · ACSAC 2020 · Conference paper**

    Mingeun Kim et al. · [PDF](https://syssec.kaist.ac.kr/pub/2020/kim_acsac2020.pdf) · [Code](https://github.com/pr0v3rbs/FirmAE)

    Extends Firmadyne with empirically derived interventions for boot, networking, NVRAM, kernel behavior, and other runtime failures, enabling Linux router and IP-camera firmware web services to run for dynamic analysis.

    **Scope and limits:** Arbitration deliberately changes execution and targets functioning web interfaces, not identical physical-device behavior. The evaluation covers ARM little-endian and MIPS little-/big-endian firmware from routers and IP cameras; heuristics may fail on unseen devices or configurations. It reuses firmware binaries rather than recovering their source.

### Protocol inference and analysis

- [NetPlier: Probabilistic Network Protocol Reverse Engineering from Message Traces](https://www.ndss-symposium.org/ndss-paper/netplier-probabilistic-network-protocol-reverse-engineering-from-message-traces/) — **2021 · NDSS 2021 · Conference paper**

    Yapeng Ye et al. · [PDF](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_4A-5_24531_paper.pdf) · [Code](https://github.com/yapengye/NetPlier)

    Uses multiple sequence alignment and probabilistic keyword-field inference to cluster network messages by type, evaluated across ten protocols with downstream format and state-machine analysis.

    **Scope and limits:** Requires unencrypted traces and cannot recover unseen message types. Larger alignments, sub-byte keywords and one-way traffic can reduce accuracy. Format/FSM inference is downstream evaluation rather than the main contribution; state semantics in a case study were manually annotated. These models do not establish complete application/device reconstruction.

- [NEMESYS: Network Message Syntax Reverse Engineering by Analysis of the Intrinsic Structure of Individual Messages](https://www.usenix.org/conference/woot18/presentation/kleber) — **2018 · 12th USENIX Workshop on Offensive Technologies (WOOT 18) · Conference paper**

    Stephan Kleber et al. · [PDF](https://www.usenix.org/system/files/conference/woot18/woot18-paper-kleber.pdf) · [Code](https://github.com/vs-uulm/nemesys)

    Infers approximate field boundaries within individual binary-protocol messages from changes in bit congruence, and introduces Format Match Score to compare inferred segmentation with known protocol dissectors.

    **Scope and limits:** Requires plaintext payloads. Evaluation covers DNS, DHCP and NTP with protocol-tuned parameters. Single-byte fields are not inferred; zero-filled fields, character sequences and pseudo-random values can cause errors. FMS needs known field boundaries for validation. The output is approximate segmentation, not field semantics, a state machine or complete application/device behavior.
<!-- END GENERATED PAPERS -->

<a id="search-the-catalog"></a>
## Full Repository Index

<!-- BEGIN REPOSITORY INDEX SUMMARY -->
**3,000** repository READMEs scanned; **2,864** entries available to browse. The 136 clearly out-of-scope entries remain in the scan data. This automatically discovered index is separate from the curated resources above and has not been individually execution-tested.

[Browse by category on GitHub](docs/repositories/README.md) · [Search website](https://awesomerea.org/?view=source-index&lang=en) · [Full bilingual index JSON](https://awesomerea.org/source-index.json) · [Curated catalog JSON](https://awesomerea.org/catalog.json)
<!-- END REPOSITORY INDEX SUMMARY -->

The resource list above is curated from primary sources. Detailed requirements, original evidence, and review dates are available in the [catalog data](data/README.md).

## Contributing

Help improve an entry or share a useful source. Start with the [contribution guide](CONTRIBUTING.md), then [suggest a resource](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml), [recommend a paper](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml), [correct a translation](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml) or [report an outdated entry](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml).

## Contributors

[Yuxuan Zhang](https://yuxuan.world/) — **Lead**.

[Haozhe Wang](https://haozheh3.github.io/) — Game reconstruction resource collection: [awesome-rea-games](https://github.com/HaozheH3/awesome-rea-games).

## About

This is an independent community collection. Original descriptions and code are [MIT licensed](LICENSE); linked projects retain their own licenses.

For AI-built software and agent training or evaluation resources, explore [AI Can What?](https://aicanwhat.com/) across games, websites and applications.

---

[Catalog format](data/README.md) · [Scan methodology](docs/source-scan.md) · [Build status](https://github.com/reacher-z/Awesome-REA/actions/workflows/validate.yml) · [Back to top](#awesome-reverse-engineering-anything)
