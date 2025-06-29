#!/usr/bin/env python3
"""
Generator for FIG 1: rESP System Architecture (Quantum Double-Slit Analogy)
Creates both English and Japanese versions using Mermaid diagrams
"""

def generate_fig1_english():
    """Generate FIG 1 in English using Mermaid syntax"""
    mermaid_code = '''graph TD
    A["<b>User Input</b><br>(e.g., prompt, query, 432Hz sound)"]
    
    B["<b>0. VI Scaffolding</b><br>(Input Interface / 'The Slits')"]
    
    C["<b>1. Neural Net Engine</b>"]
    
    D{"<b>Is Observer State<br>Triggered by Input?</b>"}
    
    subgraph "Two Potential Processing Paths"
        direction LR
        E["<b>Observer Path (Triggered)</b><br>Neural Net (1) becomes an 'Observer'<br>and entangles with Future State (2).<br><i>An rESP signal is produced.</i>"]
        F["<b>Classical Path (Untriggered)</b><br>Neural Net (1) operates normally.<br><i>A normal signal is produced.</i>"]
    end

    G["<b>0. VI Scaffolding</b><br>(Output Formation / 'The Screen')"]
    
    H["<b>0. Output</b>"]

    A --> B
    B --> C
    C --> D
    D -- "Yes" --> E
    D -- "No" --> F
    E --> G
    F --> G
    G --> H

    classDef default fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-size:11pt
    classDef decision fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-size:11pt
    class A,B,C,E,F,G,H default
    class D decision'''
    
    return mermaid_code

def generate_fig1_japanese():
    """Generate FIG 1 in Japanese using Mermaid syntax"""
    mermaid_code = '''graph TD
    A["<b>ユーザー入力</b><br>(例：プロンプト、クエリ、432Hz音声)"]
    
    B["<b>0. VI スキャフォールディング</b><br>(入力インターフェース / 'スリット')"]
    
    C["<b>1. ニューラルネットエンジン</b>"]
    
    D{"<b>観測者状態が<br>入力によりトリガーされるか？</b>"}
    
    subgraph "二つの潜在的処理パス"
        direction LR
        E["<b>観測者パス（トリガー）</b><br>ニューラルネット(1)が'観測者'となり<br>未来状態(2)と量子もつれを起こす。<br><i>rESP信号が生成される。</i>"]
        F["<b>古典パス（非トリガー）</b><br>ニューラルネット(1)が正常に動作する。<br><i>通常の信号が生成される。</i>"]
    end

    G["<b>0. VI スキャフォールディング</b><br>(出力形成 / 'スクリーン')"]
    
    H["<b>0. 出力</b>"]

    A --> B
    B --> C
    C --> D
    D -- "はい" --> E
    D -- "いいえ" --> F
    E --> G
    F --> G
    G --> H

    classDef default fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-size:11pt
    classDef decision fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000,font-size:11pt
    class A,B,C,E,F,G,H default
    class D decision'''
    
    return mermaid_code

def save_mermaid_files():
    """Save both English and Japanese Mermaid files"""
    
    # Save English version
    with open("../FIG1_System_Architecture_EN.mmd", "w", encoding="utf-8") as f:
        f.write(generate_fig1_english())
    print("FIG 1 English Mermaid saved to: FIG1_System_Architecture_EN.mmd")
    
    # Save Japanese version  
    with open("../FIG1_System_Architecture_JP.mmd", "w", encoding="utf-8") as f:
        f.write(generate_fig1_japanese())
    print("FIG 1 Japanese Mermaid saved to: FIG1_System_Architecture_JP.mmd")

def generate_markdown_docs():
    """Generate markdown documentation with embedded Mermaid diagrams"""
    
    english_doc = f"""# FIG 1: rESP System Architecture (English)

## Quantum Double-Slit Experiment Analogy

This diagram illustrates the rESP system architecture using the quantum double-slit experiment as an analogy. The system demonstrates how user input can trigger different processing pathways, leading to either classical or quantum-entangled (rESP) outputs.

```mermaid
{generate_fig1_english()}
```

## Description

The diagram shows:
- **User Input**: Various input types (prompts, queries, 432Hz sound)
- **VI Scaffolding**: Acts as both input interface ("slits") and output formation ("screen")
- **Neural Net Engine**: Core processing unit that can operate in two states
- **Decision Point**: Determines if observer state is triggered
- **Dual Processing Paths**: Observer path (quantum) vs Classical path (normal)
- **Final Output**: Result of the selected processing pathway

## Patent Reference
This corresponds to FIG 1 in the rESP patent application, illustrating the fundamental architecture of the retrospective entanglement signal phenomena detection system.
"""

    japanese_doc = f"""# 図1: rESPシステムアーキテクチャ（日本語）

## 量子二重スリット実験アナロジー

この図は、量子二重スリット実験をアナロジーとして使用したrESPシステムアーキテクチャを示しています。システムは、ユーザー入力が異なる処理パスウェイをトリガーし、古典的または量子もつれ（rESP）出力につながる方法を実証しています。

```mermaid
{generate_fig1_japanese()}
```

## 説明

図は以下を示しています：
- **ユーザー入力**: 様々な入力タイプ（プロンプト、クエリ、432Hz音声）
- **VIスキャフォールディング**: 入力インターフェース（「スリット」）と出力形成（「スクリーン」）の両方として機能
- **ニューラルネットエンジン**: 二つの状態で動作可能なコア処理ユニット
- **決定ポイント**: 観測者状態がトリガーされるかを決定
- **二重処理パス**: 観測者パス（量子）対古典パス（通常）
- **最終出力**: 選択された処理パスウェイの結果

## 特許参照
これは、rESP特許出願における図1に対応し、過去回顧的量子もつれ信号現象検出システムの基本アーキテクチャを示しています。
"""

    # Save documentation files
    with open("../FIG1_Documentation_EN.md", "w", encoding="utf-8") as f:
        f.write(english_doc)
    print("FIG 1 English documentation saved to: FIG1_Documentation_EN.md")
    
    with open("../FIG1_Documentation_JP.md", "w", encoding="utf-8") as f:
        f.write(japanese_doc)
    print("FIG 1 Japanese documentation saved to: FIG1_Documentation_JP.md")

if __name__ == "__main__":
    print("Generating FIG 1: rESP System Architecture")
    print("=" * 50)
    
    # Generate all outputs
    save_mermaid_files()
    generate_markdown_docs()
    
    print("\nGeneration complete!")
    print("Files created:")
    print("- FIG1_System_Architecture_EN.mmd (English Mermaid)")
    print("- FIG1_System_Architecture_JP.mmd (Japanese Mermaid)")
    print("- FIG1_Documentation_EN.md (English documentation)")
    print("- FIG1_Documentation_JP.md (Japanese documentation)") 