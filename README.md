# Evidence Path

**从开源证据，走到适合当前项目的实现。**

[English](README.en.md) · [Skill 入口](SKILL.md) · [改造依据](docs/design.md) · [MIT](LICENSE)

[![Validate](https://github.com/Silas-1995/evidence-path/actions/workflows/validate.yml/badge.svg)](https://github.com/Silas-1995/evidence-path/actions/workflows/validate.yml)

Evidence Path 是一套面向编码智能体的工程排错与开源方案研究 skill。它先读取本地代码、实际依赖版本和约束，再检查 upstream issue、PR、源码、测试及发布记录；确认方案适用后，按你的要求交付建议，或继续完成改动与验证。

## 用在什么地方

- **排错**：依赖升级、运行时报错、构建失败、框架或 SDK 集成卡点。
- **实现**：找到适用的 API 用法、配置模式和边界测试，再映射到本地架构。
- **选型**：比较真正满足运行环境和接口要求的开源库，说明适配成本与限制。

普通文案修改、已有明确答案的小改动不需要启动研究。你要求只调研，就交付建议；你要求修复，就继续实施。禁止联网时，保留本地分析并明确证据边界。

## 这版优化了什么

| 关注点 | Evidence Path 的处理 |
| --- | --- |
| 入口负担 | 主入口 54 行，详细流程按需读取；移除重复说明和常规搜索流水账 |
| 搜索效率 | 小范围查询 → 精读 → 必要时改写查询；证据足够或结果重复时停止 |
| 版本判断 | 区分 issue 关闭、PR 合并、包已发布，以及本地真正可用 |
| 选型标准 | 先检查运行环境、接口和许可等硬条件，再比较证据与适配成本 |
| 交付范围 | 保留用户选择的技术栈，尊重只调研或继续实施的请求 |
| 可验证性 | 可选 JSON 交接格式与离线校验器；未执行测试不能申报已验证 |

主入口按空白分词统计为原版的约 43%，仅代表文本体积变化，不代表模型 token、速度或成功率的实测提升。完整比较见 [改造说明](docs/design.md)。

## 安装

这是一个独立 skill 目录，不需要启动服务，也不包含 GitHub 凭证。研究时可使用智能体已有的 GitHub connector、GitHub CLI 或浏览能力。Python 仅用于可选报告校验；维护仓库时另需 PyYAML。

复制给智能体：

```text
请从 https://github.com/Silas-1995/evidence-path 安装 Evidence Path skill。
先读取 README.md 和 SKILL.md，再安装到当前环境已启用的个人 skills 目录，目录名为 evidence-path。
若目标目录已有内容，保留本地改动并检查现有版本后更新；不要覆盖其他 skill。
安装后检查元数据与相对引用，并确认当前环境能够发现 evidence-path。
```

### Codex 本地安装示例

当前官方文档列出的个人目录为 `~/.agents/skills`。已有环境可能使用其他 active skills 路径；按实际配置选择一个目录安装，避免重复注册。[官方说明](https://learn.chatgpt.com/docs/build-skills)

Bash：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Silas-1995/evidence-path.git "$HOME/.agents/skills/evidence-path"
```

Windows PowerShell：

```powershell
$skillRoot = Join-Path $HOME '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
git clone https://github.com/Silas-1995/evidence-path.git (Join-Path $skillRoot 'evidence-path')
```

更新前先查看安装目录内的改动，再执行 `git pull --ff-only`。需要固定版本时，在干净的新安装中执行 `git checkout v1.0.0`。固定到 tag 后不要直接 pull；切回 `main` 才能继续跟随分支更新。

其他支持 `SKILL.md` 的运行环境，可将整个目录放入其受支持的 skills 路径。具体发现机制和调用方式以对应环境文档为准；不承诺所有智能体已完成兼容测试。

## 调用示例

```text
用 $evidence-path 排查这个依赖升级后的构建错误。
先确认 lockfile 的实际版本，找匹配的 upstream 修复，完成本地修改并跑相关检查。
```

```text
用 $evidence-path 比较适合我们 Python 3.11 项目的开源 PDF 解析库。
需要本地运行和表格提取。只调研，给出适配成本、许可和验证方法，先不要改代码。
```

```text
用 $evidence-path 检查这个已合并 PR 的修复是否进入了我们能安装的版本。
如果尚未发布，明确指出，不要把 merge 当成 release。
```

主入口为英文以便跨项目复用，要求智能体按用户语言回答；中文触发词也包含在描述中。支持自动匹配，也可显式调用。

## 可选结构化交接

普通任务直接给出结论、关键证据和实际验证结果即可。需要结构化记录时，使用 [格式说明](references/report-format.md) 与 [合成示例](examples/report.json)：

```sh
python scripts/validate_report.py examples/report.json
```

校验器会检查引用一致性、已发布版本的证据要求，以及验证状态是否自相矛盾。它不联网、不执行报告内的命令，也不会证明来源真实或自动扫描全部敏感信息。示例中的项目、URL 和结论都是合成数据。

## 维护与验证

Python 3.10+：

```sh
python -m pip install -r requirements-dev.txt
python scripts/check_repo.py
python -m unittest discover -s tests -v
```

[GitHub Actions](https://github.com/Silas-1995/evidence-path/actions/workflows/validate.yml) 在 Windows 和 Linux 上运行结构、相对链接、示例及单元测试。[行为场景](evals/scenarios.md) 用于人工或另行授权的 agent 评测；它们不等同于自动测试通过，也没有宣称跨模型效果提升。

## 许可

MIT。详见 [LICENSE](LICENSE)。
