# PPTtoVideo Skill

将PPT演示文稿转换为带语音讲解的视频的 AI Agent 技能。

## 功能特点

### 核心功能

| 功能 | 说明 | 技术实现 |
|------|------|----------|
| **PPT解析** | 支持 .pptx 格式，提取每页文本内容 | python-pptx（纯Python） |
| **语音合成** | 将文本转换为自然流畅的语音 | EDGE TTS（默认）或远程TTS API |
| **AI优化** | 使用LLM优化讲稿内容，更自然流畅 | OpenAI API（可选） |
| **视频合成** | 将PPT图片和语音合并为视频 | moviepy + FFmpeg |

### 语音合成能力

**两种模式可选：**

| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| **EDGE TTS**（默认） | Microsoft Edge 在线语音服务 | 免费、无需API密钥、高质量Neural语音 | 需要联网 |
| **远程 TTS API** | 自定义TTS服务 | 灵活可控、支持任意TTS服务 | 需要API密钥 |

**EDGE TTS 支持的语言：**
- 中文（普通话）- 6个发音人
- 英语（美式/英式）- 4个发音人
- 日语、韩语、法语、德语、西班牙语等

### 其他特点

- ⚡ **快速预览** - 支持只转换前3页，快速验证效果
- ⚙️ **配置引导** - 首次安装自动引导配置
- 🔌 **跨平台** - 支持 Windows/Linux/macOS

## 安装方式

### 通过 Hermes Agent CLI 安装

```bash
# 打包技能
cd PPTtoVideo_Skill
zip -r ppt2video_skill.zip .

# 安装到 Hermes Agent
hermes skill install ppt2video_skill.zip

# 验证安装
hermes skill list
```

### 查看已安装的技能

```bash
hermes skill list
```

### 卸载技能

```bash
hermes skill uninstall com.trae.ppt2video
```

### 手动安装依赖

```bash
cd PPTtoVideo_Skill
pip install -r requirements.txt
```

**主要依赖说明：**
- `edge-tts` - Microsoft EDGE 语音合成（无需API密钥）
- `python-pptx` - PPT文件解析
- `moviepy` - 视频合成
- `openai` - LLM调用（AI优化功能）
- `PyYAML` - 配置文件解析

## Hermes Agent 使用指南

### 1. 首次配置

#### 获取配置引导

```bash
hermes skill call ppt2video --action wizard
```

**响应示例：**

```json
{
  "status": "wizard",
  "message": "请完成配置（带 * 的为必填项）",
  "steps": [
    {
      "step": 1,
      "title": "语音合成配置 *",
      "description": "配置语音合成服务，用于生成讲解音频（必须配置发音人，API密钥可选，不配置则使用EDGE TTS）",
      "is_required": true,
      "fields": [
        {"name": "default_voice", "label": "默认发音人", "type": "select", "required": true, "options": [
          {"value": "zh-CN-XiaoxiaoNeural", "label": "晓晓 (中文女声)"},
          {"value": "zh-CN-YunyangNeural", "label": "云扬 (中文男声)"},
          {"value": "zh-CN-XiaoyiNeural", "label": "晓伊 (中文女声)"},
          {"value": "zh-CN-YunxiNeural", "label": "云希 (中文男声)"},
          {"value": "en-US-JennyNeural", "label": "Jenny (英语女声)"},
          {"value": "longanyang", "label": "优雅知性女 (兼容)"}
        ]},
        {"name": "default_speed", "label": "默认语速", "type": "number", "default": 1.0},
        {"name": "tts_api_key", "label": "TTS API密钥（可选）", "type": "password", "required": false, "description": "不配置则使用EDGE TTS（无需密钥）"},
        {"name": "tts_api_url", "label": "TTS API地址（可选）", "type": "text", "required": false}
      ]
    },
    {
      "step": 2,
      "title": "AI优化配置",
      "description": "配置AI服务优化讲稿（可选，不影响基础功能）",
      "is_required": false,
      "fields": [
        {"name": "enable_llm", "label": "启用AI优化", "type": "boolean", "default": false},
        {"name": "llm_api_key", "label": "LLM API密钥", "type": "password", "required": false},
        {"name": "llm_api_url", "label": "LLM API地址", "type": "text", "required": false},
        {"name": "llm_model", "label": "AI模型", "type": "text", "required": false}
      ]
    }
  ]
}
```

#### 提交配置

```bash
# 基础配置（至少配置发音人）
hermes skill call ppt2video --action setup --config '{
  "default_voice": "zh-CN-XiaoxiaoNeural",
  "default_speed": 1.0
}'

# 完整配置（包含AI优化）
hermes skill call ppt2video --action setup --config '{
  "default_voice": "zh-CN-XiaoxiaoNeural",
  "default_speed": 1.0,
  "enable_llm": true,
  "llm_api_key": "your_llm_api_key",
  "llm_api_url": "your_llm_api_url",
  "llm_model": "your_llm_model"
}'
```

### 2. 转换PPT为视频

#### 基本转换

```bash
# 转换PPT（使用默认配置）
hermes skill call ppt2video --action convert --ppt_file "/path/to/presentation.pptx"

# 指定输出路径
hermes skill call ppt2video --action convert \
  --ppt_file "/path/to/presentation.pptx" \
  --output_path "/path/to/output.mp4"
```

#### 完整参数转换

```bash
hermes skill call ppt2video --action convert \
  --ppt_file "/path/to/presentation.pptx" \
  --mode full \
  --voice longanyun \
  --speed 1.2 \
  --use_llm true
```

#### 快速预览模式（只转换前3页）

```bash
hermes skill call ppt2video --action convert \
  --ppt_file "/path/to/presentation.pptx" \
  --mode preview_3
```

### 3. 配置管理

#### 查看当前配置

```bash
hermes skill call ppt2video --action get_config
```

**响应示例：**

```json
{
  "status": "success",
  "message": "获取配置成功",
  "config": {
    "tts": {
      "api_url": "your_llm_api_url",
      "api_key": "******",
      "default_voice": "longanyang",
      "default_speed": 1.0
    },
    "llm": {
      "enabled": false,
      "api_url": "",
      "api_key": "******",
      "default_model": ""
    },
    "video": {
      "ffmpeg_path": "",
      "preset": "normal",
      "crf": 23,
      "width": 1920,
      "height": 1080
    }
  }
}
```

#### 检查配置状态

```bash
hermes skill call ppt2video --action check_config
```

**响应示例：**

```json
{
  "status": "success",
  "message": "配置状态检查完成",
  "config_status": {
    "configured": true,
    "has_config_file": true,
    "default_voice": "longanyang",
    "default_speed": 1.0,
    "tts_api_configured": false,
    "llm_enabled": false,
    "llm_api_configured": false
  }
}
```

#### 直接更新配置

```bash
# 更新发音人
hermes skill call ppt2video --action configure --config '{
  "tts": {
    "default_voice": "longanyun"
  }
}'

# 启用AI优化
hermes skill call ppt2video --action configure --config '{
  "llm": {
    "enabled": true,
    "api_key": "your_key"
  }
}'
```

### 4. 发音人管理

#### 获取发音人列表

```bash
hermes skill call ppt2video --action list_voices
```

**响应示例：**

```json
{
  "status": "success",
  "message": "获取发音人列表成功",
  "voices": [
    {"id": "longanyang", "name": "优雅知性女"},
    {"id": "longanyun", "name": "居家暖男"},
    {"id": "longhuhu", "name": "天真烂漫女童"},
    {"id": "loongdonna_v2", "name": "美式英文女"}
  ],
  "current_voice": "longanyang"
}
```

### 5. 连通性验证

```bash
hermes skill call ppt2video --action validate
```

**响应示例：**

```json
{
  "status": "success",
  "message": "连通性测试完成",
  "details": {
    "tts": {
      "status": "info",
      "message": "未配置TTS API，将使用内置发音"
    },
    "llm": {
      "status": "info",
      "message": "LLM功能未启用"
    }
  }
}
```

### 6. Python API 调用

```python
from hermes_agent import Agent

# 初始化Agent
agent = Agent()

# 首次配置
agent.call_skill(
    skill_id="com.trae.ppt2video",
    inputs={
        "action": "setup",
        "config": {
            "default_voice": "longanyang"
        }
    }
)

# 转换PPT
result = agent.call_skill(
    skill_id="com.trae.ppt2video",
    inputs={
        "action": "convert",
        "ppt_file": "/path/to/presentation.pptx",
        "mode": "full",
        "voice": "longanyang",
        "speed": 1.0,
        "use_llm": False
    }
)

# 检查结果
if result["status"] == "success":
    print(f"视频生成成功: {result['video_file']}")
else:
    print(f"转换失败: {result['message']}")
```

## 操作类型汇总

| 操作 | Hermes命令 | 说明 |
|------|-----------|------|
| `convert` | `hermes skill call ppt2video --action convert` | 转换PPT为视频 |
| `wizard` | `hermes skill call ppt2video --action wizard` | 获取配置引导 |
| `setup` | `hermes skill call ppt2video --action setup` | 提交配置 |
| `check_config` | `hermes skill call ppt2video --action check_config` | 检查配置状态 |
| `list_voices` | `hermes skill call ppt2video --action list_voices` | 获取发音人列表 |
| `configure` | `hermes skill call ppt2video --action configure` | 直接更新配置 |
| `validate` | `hermes skill call ppt2video --action validate` | 验证连通性 |
| `get_config` | `hermes skill call ppt2video --action get_config` | 获取当前配置 |

## 参数说明

### 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| ppt_file | string | 是 | - | PPT文件路径（绝对路径） |
| output_path | string | 否 | 自动生成 | 输出视频路径 |
| mode | string | 否 | full | 转换模式：preview_3/full |
| voice | string | 否 | 配置默认值 | 发音人 |
| speed | number | 否 | 1.0 | 语速(0.8-1.5) |
| use_llm | boolean | 否 | 配置默认值 | 是否使用AI优化 |
| action | string | 否 | convert | 操作类型 |
| config | object | 否 | - | 配置参数（用于setup/configure） |

### 输出参数

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 状态：success/error/needs_config/partial/wizard |
| message | string | 结果消息 |
| video_file | string | 生成的视频文件路径 |
| stats | object | 统计信息（幻灯片数、时长等） |
| config | object | 当前配置（get_config返回） |
| config_status | object | 配置状态（check_config返回） |
| voices | array | 发音人列表（list_voices返回） |
| steps | array | 配置步骤（wizard返回） |

### 支持的发音人

#### EDGE TTS 发音人（推荐，无需API密钥）

| ID | 名称 | 语言 | 说明 |
|----|------|------|------|
| zh-CN-XiaoxiaoNeural | 晓晓 | 中文(普通话) | 默认，女声，清晰自然 |
| zh-CN-YunyangNeural | 云扬 | 中文(普通话) | 男声，沉稳有力 |
| zh-CN-XiaoyiNeural | 晓伊 | 中文(普通话) | 女声，活泼亲切 |
| zh-CN-YunxiNeural | 云希 | 中文(普通话) | 男声，年轻活力 |
| zh-CN-YunjianNeural | 云健 | 中文(普通话) | 男声，成熟稳重 |
| zh-CN-XiaohanNeural | 晓涵 | 中文(普通话) | 女声，温柔甜美 |
| en-US-JennyNeural | Jenny | 英语(美式) | 女声，自然流畅 |
| en-US-AriaNeural | Aria | 英语(美式) | 女声，优雅知性 |
| en-US-GuyNeural | Guy | 英语(美式) | 男声，清晰专业 |
| en-GB-SoniaNeural | Sonia | 英语(英式) | 女声，标准英音 |
| ja-JP-NanamiNeural | Nanami | 日语 | 女声，自然亲切 |
| ja-JP-KeitaNeural | Keita | 日语 | 男声，温和有礼 |
| ko-KR-SunHiNeural | SunHi | 韩语 | 女声，甜美可爱 |
| ko-KR-InJoonNeural | InJoon | 韩语 | 男声，沉稳有力 |
| fr-FR-DeniseNeural | Denise | 法语 | 女声，优雅浪漫 |
| fr-FR-HenriNeural | Henri | 法语 | 男声，绅士风度 |
| de-DE-KatjaNeural | Katja | 德语 | 女声，清晰准确 |
| de-DE-ConradNeural | Conrad | 德语 | 男声，稳重可靠 |
| es-ES-ElviraNeural | Elvira | 西班牙语 | 女声，热情奔放 |
| es-ES-AlvaroNeural | Alvaro | 西班牙语 | 男声，阳光开朗 |

#### 兼容性发音人（自动映射到EDGE TTS）

| ID | 名称 | 映射到 |
|----|------|--------|
| longanyang | 优雅知性女 | zh-CN-XiaoxiaoNeural |
| longanyun | 居家暖男 | zh-CN-YunyangNeural |
| longhuhu | 天真烂漫女童 | zh-CN-XiaoyiNeural |
| loongdonna_v2 | 美式英文女 | en-US-JennyNeural |

### TTS模式说明

技能支持两种语音合成模式：

| 模式 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| **远程API** | 使用配置的TTS API | 发音质量高，支持多种发音人 | 需要API密钥 |
| **EDGE TTS** | 使用Microsoft Edge TTS服务 | 无需配置，开箱即用，微软高质量语音 | 需要联网 |

**自动切换逻辑：**
- 优先检查发音人：以 `zh-`、`en-` 等开头的发音人使用 EDGE TTS
- 如果配置了 `tts_api_key`，使用远程API
- 如果未配置API密钥，默认使用 EDGE TTS
- 远程API失败时，自动降级到 EDGE TTS

### EDGE TTS 特点

- **免费使用：** 不需要API密钥，完全免费
- **高质量语音：** 使用微软Neural TTS技术，发音自然流畅
- **多语言支持：** 支持中文、英语、日语、韩语、法语、德语、西班牙语等
- **语速调节：** 支持 0.8-1.5 倍速调节
- **跨平台：** Windows、Linux、Mac 都可以使用

## 技能目录结构

```
PPTtoVideo_Skill/
├── main.py                 # 技能主入口
├── skill.yaml              # 技能配置文件
├── manifest.json           # 技能清单
├── requirements.txt        # 依赖清单
├── README.md               # 技能说明
├── icon.png                # 技能图标
└── modules/                # 功能模块
    ├── config.py           # 配置管理器
    ├── config_wizard.py    # 配置引导助手
    ├── converter.py        # 转换协调器
    ├── ppt_processor.py    # PPT解析器
    ├── tts_processor.py    # 语音合成器
    ├── llm_processor.py    # LLM处理器
    └── video_composer.py   # 视频合成器
```

## 技术栈

- Python 3.10+
- python-pptx - PPT解析（纯Python）
- moviepy - 视频合成
- openai - LLM调用
- requests - HTTP请求
- PyYAML - 配置文件解析
- edge-tts - Microsoft Edge语音合成

## 注意事项

1. 需要安装 FFmpeg 并添加到系统 PATH
2. EDGE TTS 无需API密钥，开箱即用；远程TTS API需要配置密钥（可选）
3. 首次使用需要先配置发音人
4. AI优化为可选功能，不影响基础转换
5. 支持 Windows/Linux/macOS
6. EDGE TTS 需要联网（使用微软在线服务）

## 许可证

MIT License