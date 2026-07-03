# CSswitch 自定义第三方API支持 - SPEC.md

## 目标
在CSswitch中添加 `custom_anthropic` 和 `custom_openai` 两种provider支持，
让用户可以填入任意第三方Anthropic兼容或OpenAI兼容的API端点。

## 修改范围

### 1. proxy/csswitch_proxy.py
在PROVIDERS注册表中添加两个新provider：

#### custom_anthropic
- `mode`: "anthropic"（原生Anthropic协议透传）
- `url`: 从环境变量 `CUSTOM_ANTHROPIC_URL` 读取，默认为空（启动时必填）
- `key_env`: "CUSTOM_ANTHROPIC_API_KEY"
- `models`: 用户自定义模型列表（通过环境变量 `CUSTOM_ANTHROPIC_MODELS` 传入，JSON格式）
- `model_map`: 通过环境变量 `CUSTOM_ANTHROPIC_MODEL_MAP` 传入（JSON格式）
- `model_caps`: 通过环境变量 `CUSTOM_ANTHROPIC_MODEL_CAPS` 传入（JSON格式）
- `default_cap`: 8192
- `default_model`: 从models中取第一个

#### custom_openai
- `mode`: "openai"（走Anthropic↔OpenAI翻译路径）
- `url`: 从环境变量 `CUSTOM_OPENAI_URL` 读取，默认为空（启动时必填）
- `key_env`: "CUSTOM_OPENAI_API_KEY"
- `models`: 用户自定义模型列表
- `model_map`: 用户自定义映射
- `model_caps`: 用户自定义上限
- `default_cap`: 8192
- `default_model`: 从models中取第一个

启动参数新增：
- `--custom-url`: 自定义上游URL（覆盖provider配置中的url）
- `--custom-models`: JSON格式的模型列表
- `--custom-model-map`: JSON格式的模型映射

### 2. desktop/src-tauri/src/config.rs
扩展 `ProviderCfg`：
```rust
pub struct ProviderCfg {
    pub key: String,
    #[serde(default)]
    pub url: String,          // 自定义API endpoint URL
    #[serde(default)]
    pub models: String,       // JSON格式的模型列表
    #[serde(default)]
    pub model_map: String,    // JSON格式的模型映射
    #[serde(default)]
    pub model_caps: String,   // JSON格式的模型上限
}
```

### 3. desktop/src-tauri/src/lib.rs
- `key_env()`: 新增 custom_anthropic → "CUSTOM_ANTHROPIC_API_KEY", custom_openai → "CUSTOM_OPENAI_API_KEY"
- `upstream_host()`: 从配置的url中解析host
- `get_config()`: 返回 custom_anthropic 和 custom_openai 的 masked key 和 url
- `set_config()`: 验证 provider 支持 custom_anthropic / custom_openai
- `ensure_proxy()`: 将自定义URL、模型等通过环境变量注入proxy子进程
- 新增 `save_provider_url(provider, url)` command

### 4. desktop/src/index.html
在provider select中添加：
```html
<option value="custom_anthropic">自定义 Anthropic 兼容端点</option>
<option value="custom_openai">自定义 OpenAI 兼容端点</option>
```

选择自定义provider时显示额外输入框：
- API Endpoint URL输入框
- 模型ID输入框（支持填入模型名，如 claude-3-opus, gpt-4 等）
- （可选）模型显示名

### 5. desktop/src/main.js
- 根据provider选择动态显示/隐藏自定义URL和模型输入
- 保存时同时保存url和key
- 加载时恢复url和模型设置

### 6. proxy/qwen_proxy.py
不需要修改（custom_openai直接复用csswitch_proxy.py中的_handle_openai路径）

## 数据流

1. 用户在面板选择"自定义Anthropic兼容端点"
2. 填写：API URL、API Key、模型ID
3. 保存 → Rust后端写入config.json
4. 点击"一键开始" → ensure_proxy读取配置
5. Rust启动proxy子进程，注入环境变量：
   - CUSTOM_ANTHROPIC_API_KEY=用户key
   - CSSWITCH_CUSTOM_URL=用户URL
   - CSSWITCH_CUSTOM_MODELS=模型列表JSON
6. proxy读取环境变量构建PROVIDER配置
7. 后续请求走对应mode的处理路径

## 打包

### macOS
Tauri原生支持：
```bash
cd desktop && npm run tauri build -- --target universal-apple-darwin
```

### Linux
Tauri支持Linux构建（在Linux环境下）：
```bash
cd desktop && npm run tauri build -- --target x86_64-unknown-linux-gnu
```
产物：AppImage 和 .deb

注意：由于当前环境可能不是Linux桌面环境，打包Linux版本可能需要：
1. 安装Tauri Linux依赖
2. 使用github actions打包
3. 提供打包脚本
