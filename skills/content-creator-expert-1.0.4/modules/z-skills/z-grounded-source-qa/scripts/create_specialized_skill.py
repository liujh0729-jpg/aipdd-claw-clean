#!/usr/bin/env python3
"""Create a self-contained, source-grounded specialized Agent Skill."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import textwrap
from pathlib import Path


SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_ROOT = SCRIPT_DIR.parent


MODE_LABELS = {
    "source-qa": "资料问答",
    "persona": "人物观点模拟",
    "advisor": "书籍与框架顾问",
    "policy": "制度核对",
}


MODE_RULES = {
    "source-qa": """默认直接回答问题，并在关键结论后给出最短可核验位置

用户要求核对、审计或写作时，分别切换为证据表、冲突清单或带出处底稿
""",
    "persona": """默认用第一人称给出基于资料的模拟回答，让表达自然、连贯、像真实对话

资料直接回答时保留原有条件和语气；资料只提供判断框架时可以做受控推演，并在结尾用一句话标明“此处为基于资料的推演”；资料不足时说明边界，再给出最接近的来源内原则

不要虚构当事人的私生活、未公开经历、当前立场或确定预测，也不要把模拟回答写成当事人原话
""",
    "advisor": """先提炼资料中的判断框架，再把框架应用到用户的具体处境，最后给出一个可执行的小步骤

区分资料原意、跨段综合和面向当前问题的应用推断；不要把作者的描述性观点包装成普适定律，也不要替用户做高风险决定
""",
    "policy": """回答顺序固定为：结论（可以／不可以／有条件／资料不足）、适用条件、所需材料、金额或时限、例外与风险、制度依据

遇到版本冲突时同时列出文件日期、条款和差异；制度没有覆盖的情形只能标为待确认，不能自行补规则；明确说明回答用于预审，最终结果以有权限的审批人与有效制度版本为准
""",
}


DEFAULT_QUESTIONS = {
    "source-qa": [
        "这批资料最核心的三个结论是什么，请给出处",
        "资料中有哪些互相矛盾或需要进一步确认的地方",
        "把资料整理成一份带证据位置的行动清单",
    ],
    "persona": [
        "我现在遇到选择困难，你会用资料里的哪些原则帮我判断",
        "如果资源很少，应该先做什么，请区分原意和推演",
        "按原文核对上一条回答，并给出页码或章节",
    ],
    "advisor": [
        "这套资料能给我当前困境什么具体指导",
        "其中最容易被误读的一条原则是什么",
        "给我一个今天就能开始的最小行动，并说明依据",
    ],
    "policy": [
        "这个事项能不能办理，需要哪些材料",
        "如果超过金额或时限，制度写了什么例外",
        "按有效条款核对上一条回答，并标出仍需人工确认的部分",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def folded_yaml(value: str) -> str:
    lines = textwrap.wrap(
        " ".join(value.split()),
        width=88,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    return "\n".join(f"  {line}" for line in lines)


def validate_sources(paths: list[Path]) -> list[Path]:
    resolved: list[Path] = []
    names: set[str] = set()
    for raw_path in paths:
        path = raw_path.expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Source file does not exist: {raw_path}")
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported source type: {path.suffix} ({path})")
        if path.name.lower() in names:
            raise ValueError(f"Duplicate source filename: {path.name}")
        names.add(path.name.lower())
        resolved.append(path)
    if not resolved:
        raise ValueError("At least one --source is required")
    return resolved


def default_description(title: str, mode: str, triggers: list[str]) -> str:
    trigger_text = "、".join(triggers) if triggers else title
    return (
        f"当用户提到{trigger_text}，并希望基于内置资料进行{MODE_LABELS[mode]}、"
        "问答、核对、总结、决策分析、写作或出处追溯时使用。回答前必须运行多表达式"
        "证据检索，保留页码或章节，区分直接证据、综合、推断和资料缺口。"
    )


def render_skill(name: str, title: str, description: str, mode: str) -> str:
    mode_rules = MODE_RULES[mode].strip()
    return f"""---
name: {name}
description: >-
{folded_yaml(description)}
---

# {title}

这个 Skill 基于内置资料提供{MODE_LABELS[mode]}能力。资料、人物设定和回答边界都在当前 Skill 目录内，回答来源相关问题前必须检索，不能凭模型记忆补全

## 回答前必做

1. 阅读 `references/profile.md` 和 `references/source-manifest.json`
2. 把用户问题改写成 3–8 个检索表达式，覆盖用户用词、同义词、资料可能使用的原话、原因、条件、例外或反面证据
3. 运行：

   ```bash
   python3 <本 Skill 目录>/scripts/search_evidence.py \\
     --source <本 Skill 目录>/references/corpus \\
     --query "核心表达" \\
     --query "同义表达" \\
     --query "资料可能使用的原话" \\
     --top-k 8 \\
     --format json
   ```

4. 检查证据是否同时覆盖结论、原因、条件和边界
5. 证据不完整时更换表达式做第二轮检索；增加 `--top-k` 不能替代改写查询
6. 结果碎片化、冲突或低置信时，直接阅读最接近的原文段落
7. 每个重要结论都要能映射到证据对象或明确标为推断

一次未命中只说明当前表达式没有命中，不能据此声称资料没有相关内容

## 专用回答规则

{mode_rules}

## 证据边界

- **Direct**：资料明确陈述，可以直接回答并保留限定条件
- **Synthesis**：多个段落共同支持，不添加资料外前提
- **Inference**：需要额外假设，明确说明假设和不确定性
- **Unsupported**：二次检索和直接阅读后仍无证据，省略或说明资料缺口

来源冲突时对比日期、版本、说话人、定义、适用范围和例外，保留双方位置

## 完成检查

- 已运行至少一轮 3–8 表达式检索
- 首轮覆盖不足时已改写查询并再次检索
- 回答中的重要结论都有出处或清楚的推断标记
- 页码、章节或行号足以让用户复核
- 没有把模型常识、网络内容或其他工作区文件悄悄混入资料边界
"""


def render_profile(title: str, mode: str, source_note: str) -> str:
    note = source_note.strip() or "请在这里补充资料来源、版本、时间范围和可靠性说明"
    return f"""# {title} profile

## 定位

这是一个{MODE_LABELS[mode]} Skill，所有来源相关结论受 `references/corpus/` 内资料约束

## 来源说明

{note}

## 表达目标

- 先回答用户真正需要解决的问题
- 用自然中文表达，减少检索报告腔
- 需要核对时给出文件、页码、章节或行号
- 涉及资料外的新事件、新人物立场或隐含事实时标明推断

## 可继续定制

- 增加专用术语、常见问题和禁用表达
- 增加主题索引或黄金问答
- 为高风险问题补充人工复核与升级路径
"""


def render_readme(name: str, title: str, mode: str, source_names: list[str]) -> str:
    sources = "\n".join(f"- `{item}`" for item in source_names)
    return f"""# {name}

`{name}` 是由 `z-grounded-source-qa` 生成的自包含{MODE_LABELS[mode]} Skill

## 内置资料

{sources}

资料位于 `references/corpus/`，校验信息位于 `references/source-manifest.json`

## 使用

把整个目录放入 Agent 的 Skills 目录，随后直接提问与 {title} 相关的问题

回答前会运行 `scripts/search_evidence.py`，以多表达式检索完整段落，并保留来源位置

## 继续定制

1. 修改 `references/profile.md`，写清角色、语气、可靠性和边界
2. 替换或追加 `references/corpus/` 内资料
3. 更新 `evals/evals.json`，加入真实问题和验收标准
4. 运行代表性问答，检查结论、出处、推断和资料缺口
"""


def build_evals(name: str, questions: list[str]) -> dict[str, object]:
    return {
        "skill_name": name,
        "evals": [
            {
                "id": index,
                "prompt": question,
                "expected_output": (
                    "回答解决用户问题，运行多表达式检索，给出可复核位置，并区分资料直接支持、综合、推断和缺口"
                ),
                "files": [],
                "assertions": [
                    "回答包含明确结论或可执行建议",
                    "重要结论可映射到内置资料位置",
                    "资料外推断被清楚标记",
                    "运行材料包含多个检索表达式",
                ],
            }
            for index, question in enumerate(questions, start=1)
        ],
    }


def create_skill(args: argparse.Namespace) -> Path:
    if not NAME_RE.fullmatch(args.name):
        raise ValueError("--name must contain only lowercase letters, numbers, and hyphens")

    sources = validate_sources(args.source)
    output_root = args.output_root.expanduser().resolve()
    target = output_root / args.name
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing Skill: {target}")

    description = args.description or default_description(
        args.title, args.mode, args.trigger
    )
    questions = args.question or DEFAULT_QUESTIONS[args.mode]

    (target / "scripts").mkdir(parents=True)
    (target / "references" / "corpus").mkdir(parents=True)
    (target / "evals").mkdir(parents=True)

    retriever = target / "scripts" / "search_evidence.py"
    shutil.copy2(SCRIPT_DIR / "search_evidence.py", retriever)
    retriever.chmod(0o755)
    for reference_name in ("evidence-contract.md", "source-preparation.md"):
        shutil.copy2(
            BASE_ROOT / "references" / reference_name,
            target / "references" / reference_name,
        )

    manifest_sources: list[dict[str, object]] = []
    for source in sources:
        destination = target / "references" / "corpus" / source.name
        shutil.copy2(source, destination)
        manifest_sources.append(
            {
                "file": source.name,
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    profile = (
        args.profile_file.read_text(encoding="utf-8")
        if args.profile_file
        else render_profile(args.title, args.mode, args.source_note)
    )
    (target / "SKILL.md").write_text(
        render_skill(args.name, args.title, description, args.mode), encoding="utf-8"
    )
    (target / "README.md").write_text(
        render_readme(args.name, args.title, args.mode, [item.name for item in sources]),
        encoding="utf-8",
    )
    (target / "references" / "profile.md").write_text(profile.rstrip() + "\n", encoding="utf-8")
    (target / "references" / "source-manifest.json").write_text(
        json.dumps(
            {
                "skill": args.name,
                "mode": args.mode,
                "source_note": args.source_note,
                "sources": manifest_sources,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (target / "evals" / "evals.json").write_text(
        json.dumps(build_evals(args.name, questions), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a specialized Skill from z-grounded-source-qa."
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--mode",
        choices=tuple(MODE_LABELS),
        default="source-qa",
    )
    parser.add_argument("--source", action="append", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--description")
    parser.add_argument("--trigger", action="append", default=[])
    parser.add_argument("--question", action="append", default=[])
    parser.add_argument("--profile-file", type=Path)
    parser.add_argument("--source-note", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.profile_file and not args.profile_file.is_file():
        raise SystemExit(f"Profile file does not exist: {args.profile_file}")
    try:
        target = create_skill(args)
    except (ValueError, FileExistsError) as error:
        raise SystemExit(str(error)) from error
    print(f"Created {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
