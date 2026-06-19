# AI 读书/听书应用方案 v2

## 项目定位

做一个 Web 端的家庭读书/听书应用，支持多人登录、共享公共书库、独立保存每个用户的阅读和朗读进度，并把上传的电子书自动解析、清洗、断句、朗读。

这个项目同时作为 AI 技术栈练习项目，不只是做一个能播放音频的网站，而是完整练习：

- 文本解析与清洗
- 中文断句
- TTS 模型接入
- 模型服务化
- 异步任务
- 音频缓存
- 质量评估
- 前后端完整产品闭环

核心目标：

1. 断句正确
2. 朗读自然，偏故事讲述风格
3. 阅读和播放进度稳定保存
4. 尽量本地部署，优先免费
5. 后续逐步接入本地 AI 模型

## 已确定技术栈

### 后端

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL

### 前端

- React
- TypeScript
- Vite 或 Next.js 后续再定，第一版偏向 Vite + React，简单直接

### 数据库

直接使用 PostgreSQL。

当前电脑已经检测到：

```text
PostgreSQL service: postgresql-x64-18
Status: Running
psql version: PostgreSQL 18.3
psql path: C:\Program Files\PostgreSQL\18\bin\psql.exe
```

后续需要创建本项目专用数据库和用户，例如：

```text
database: listen_book
user: listen_book_app
```

### 文件存储

第一版使用本地目录保存：

- 原始电子书
- 解析后的文本
- 封面
- 生成的音频缓存

建议目录：

```text
storage/
  uploads/
  parsed/
  audio/
```

## 推荐项目结构

```text
listen_book/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      workers/
    alembic/
    tests/
  frontend/
    src/
  storage/
    uploads/
    parsed/
    audio/
  docs/
  docker-compose.yml
  README.md
```

## 产品结构

这个应用分成三层：

1. 书库层：上传、管理、检索、标签、元数据
2. 阅读层：章节目录、正文展示、阅读进度、书签
3. 朗读层：断句、TTS、播放控制、当前句高亮、音频缓存

工程上建议拆成两个核心系统：

1. 书籍处理系统
   - 上传
   - 文件解析
   - 文本清洗
   - 分章
   - 分段
   - 断句
   - 入库

2. 阅读/朗读系统
   - 展示章节和正文
   - 保存阅读进度
   - 播放句子音频
   - 高亮当前句
   - 自动滚动
   - 管理音频缓存

不要一开始把解析、阅读、朗读写成一个大流程。书籍处理应该是后台任务，阅读页面只消费已经结构化的数据。

## 句子级设计

“句子级”不是只在前端临时断句，而是把断句结果作为长期数据结构保存到数据库。

推荐层级：

```text
Book
  Chapter
    Paragraph
      Sentence
```

示例：

```text
sentence_id: 12345
chapter_id: 8
paragraph_index: 12
sentence_index: 3
text: "他推开门，屋里一片漆黑。"
audio_path: "storage/audio/..."
```

这样做的好处：

- 朗读可以一句一句播放
- 当前句可以高亮
- 暂停后可以从具体句子恢复
- 音频可以按句缓存
- 支持上一句、下一句、自动滚动
- 后续更换 TTS 模型不影响阅读器结构

“断句”是处理动作；“句子级”是数据设计。

## 数据库核心表

第一版建议先保留这些核心表：

- `users`
- `books`
- `book_files`
- `chapters`
- `paragraphs`
- `sentences`
- `reading_progress`
- `audio_assets`
- `jobs`

后续再加：

- `bookmarks`
- `tags`
- `collections`
- `playback_history`
- `tts_models`
- `tts_voices`
- `user_settings`

## 进度保存

不要保存“第几页”，因为 TXT、EPUB、PDF 和网页布局的页概念都不稳定。

建议保存：

- 用户 ID
- 书籍 ID
- 当前章节 ID
- 当前段落 ID
- 当前句子 ID
- 当前音频播放位置
- 更新时间

## 书籍格式开发顺序

最终目标支持：

- TXT
- EPUB
- PDF

开发顺序建议：

1. TXT
2. EPUB
3. 文本型 PDF
4. 扫描 PDF + OCR

第一版建议先做 TXT + EPUB。PDF 风险高，容易拖慢主线。

## 断句与文本清洗路线

第一版不要直接依赖大模型断句。建议分层处理：

1. 规则断句
   - 中文句号、问号、叹号
   - 引号
   - 括号
   - 省略号
   - 对话换行
   - 章节标题

2. NLP 辅助
   - 合并错误换行
   - 修复 PDF/EPUB 提取后的脏文本
   - 检测异常短句或异常长句

3. LLM 增强
   - 后续用于断句修复
   - 对白识别
   - 旁白/角色区分
   - 语气标签

原则：

- 先规则，后 AI
- 先可控，后智能
- 不要每次打开书都重新断句
- 断句结果要入库，可复查、可迭代

## TTS 路线

第一版允许使用联网 TTS。原因是第一阶段目标是跑通产品和工程闭环，而不是一开始证明完全离线。

推荐阶段：

1. 系统 TTS 或 Edge TTS
   - 先跑通上传、解析、断句、播放、高亮、进度、缓存

2. 轻量本地 TTS
   - 例如 Piper
   - 练习本地模型部署和服务化

3. 中文自然朗读模型
   - 例如 ChatTTS
   - 练习更自然的中文故事朗读、停顿和语气

4. 声音克隆/微调
   - 例如 GPT-SoVITS
   - 只使用自己或明确授权的声音

5. 研究型 TTS 工具链
   - 例如 Coqui TTS
   - 用于理解 Text2Speech、speaker encoder、vocoder、多说话人训练等结构

## TTS 抽象接口

不要把某个 TTS 模型写死在业务代码里。

建议抽象为统一接口：

```text
tts.generate(text, voice, speed, options) -> audio_file
```

后端可以支持多个 provider：

```text
TTSProvider
  EdgeTTSProvider
  SystemTTSProvider
  PiperProvider
  ChatTTSProvider
  GPTSoVITSProvider
```

这样后续换模型，不需要重写阅读器、缓存和进度系统。

## 音频缓存设计

建议按“句子级 + 参数 hash”缓存。

缓存 key 包含：

```text
sentence_id
voice
speed
model_name
model_version
text_hash
```

这样同一句话在不同音色、语速、模型版本下不会互相覆盖。

音频生成状态：

```text
pending -> generating -> ready -> failed
```

## 后台任务设计

上传书和生成音频都不应该让用户在网页里干等。

书籍解析状态：

```text
uploaded -> parsing -> ready -> failed
```

推荐流程：

```text
上传文件
-> 创建书籍记录
-> 创建解析任务
-> 前端显示处理中
-> 解析完成后可阅读
```

音频生成流程：

```text
用户点击播放
-> 检查当前句音频缓存
-> 没有则生成当前句
-> 同时预生成后面几句
-> 播放时继续后台生成
```

## 账号系统第一版范围

家庭应用第一版保持简单：

- 一个管理员账号
- 多个普通用户账号
- 所有人共享同一个书库
- 每个人独立保存阅读进度、书签、播放记录

第一版不做：

- 私有书库
- 复杂权限
- 家庭组
- 邀请链接
- 社交评论

## 前端第一版重点

体验核心是阅读页，不是首页。

阅读页优先做好：

- 左侧章节目录
- 中间正文
- 底部播放控制条
- 当前句高亮
- 播放/暂停
- 上一句/下一句
- 自动滚动到当前句
- 保存进度
- 手机端可用

书库页第一版可以朴素，但阅读页要稳定、清晰、好用。

## MVP 范围

第一版建议只做：

1. 用户登录
2. 上传 TXT/EPUB
3. 自动解析章节、段落、句子
4. 书库列表
5. 书籍详情页
6. 阅读页
7. 当前用户保存进度
8. 按句朗读
9. 当前句高亮
10. 音频缓存
11. 局域网访问

第一版暂不做：

- PDF OCR
- 多角色对白朗读
- 高级情绪控制
- 声音克隆
- 外网访问
- PWA
- App

## 模型下载原则

可以下载模型，但要有边界。

适合下载：

- 官方 GitHub 或 Hugging Face 发布的模型
- 有明确 license 的模型
- 文档清楚、社区活跃的项目
- 能本地运行、能离线缓存的模型

不建议下载：

- 来路不明的整合包
- 没有 license 的语音克隆模型
- 要运行奇怪脚本的一键包
- 打包了不明 `.exe`、`.bat`、`.ps1` 的模型工具
- 声称可以无限制克隆任意人声音的资源

声音克隆只使用自己或明确授权的声音。

## 后续 AI 技术栈练习点

这个项目可以逐步练习：

- FastAPI 模型服务
- PostgreSQL 数据建模
- Alembic 数据库迁移
- 文本解析 pipeline
- 中文断句算法
- TTS provider 抽象
- 本地模型部署
- GPU/CPU 推理差异
- 异步任务队列
- 音频缓存
- 模型版本管理
- 生成质量评估
- LLM 辅助文本清洗
- OCR
- 声音克隆和微调

真正值得练的不是“下载一个最强模型”，而是把 AI 能力工程化。

## 网络和部署路线

第一阶段：

- 本机运行服务
- 家里局域网访问
- 手机/平板通过 `http://电脑内网IP:端口` 使用

第二阶段：

- 加登录保护
- 功能稳定后再考虑外网访问

第三阶段：

- 使用 Cloudflare Tunnel
- 给家人一个固定 HTTPS 地址

不建议一开始做公网暴露或 App。

## 当前已定决策

- 使用 Python FastAPI + React
- 数据库直接使用 PostgreSQL
- 第一版允许联网 TTS
- 第一版优先 TXT + EPUB
- PDF 后置
- TTS 模型后续可替换
- 句子级数据结构必须从第一版开始设计
- 先完成工程闭环，再追求高级 AI 效果

## 下一步建议

1. 初始化项目结构
2. 创建 FastAPI 后端
3. 创建 React 前端
4. 配置 PostgreSQL 连接
5. 设计第一版数据库模型
6. 实现用户登录
7. 实现书籍上传
8. 实现 TXT 解析和断句
9. 做阅读页
10. 接入第一版 TTS 和音频缓存
