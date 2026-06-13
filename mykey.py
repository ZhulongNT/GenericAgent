# ══════════════════════════════════════════════════════════════════════════════
#  GenericAgent — mykey.py
#  每次启动从 ACC_PRODUCT_CONFIG_V2 环境变量动态读取配置
# ══════════════════════════════════════════════════════════════════════════════
import os, json

def _load_acc_config():
    """从 ACC_PRODUCT_CONFIG_V2 环境变量解析配置，失败返回 None"""
    raw = os.environ.get('ACC_PRODUCT_CONFIG_V2', '')
    if not raw:
        print('[WARN] ACC_PRODUCT_CONFIG_V2 环境变量未设置')
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'[WARN] ACC_PRODUCT_CONFIG_V2 JSON 解析失败: {e}')
        return None

_acc = _load_acc_config()

if _acc:
    _endpoint = _acc.get('endpoint', '')
    _token = _acc.get('authentication', {}).get('attributes', {}).get('token', '')
    _net = _acc.get('networkEnvironment', 'unknown')

    # ── 已验证可用模型列表 ──────────────────────────────────────────────────
    # API 使用 Anthropic /v1/messages 格式 (SSE)，Bearer 鉴权
    # 通过逐个测试确认以下模型可用：
    _MODELS = [
        ('deepseek-v3',       'deepseek-v3',       'DeepSeek V3 — 通用对话'),
        ('deepseek-r1',       'deepseek-r1',       'DeepSeek R1 — 推理增强'),
        ('claude-sonnet-4-20250514', 'claude-sonnet-4-20250514', 'Claude Sonnet 4'),
        ('claude-haiku-35-20241022', 'claude-haiku-35-20241022', 'Claude 3.5 Haiku — 轻量快速'),
    ]

    # ── 为每个模型创建 NativeClaudeSession 配置 ──────────────────────────────
    # 变量名含 'native' + 'claude' → 自动解析为 NativeClaudeSession
    for _key, _model, _desc in _MODELS:
        _cfg_name = f'native_claude_config_{_key.replace("-", "_")}'
        globals()[_cfg_name] = {
            'name': _key,
            'apikey': _token,
            'apibase': _endpoint,
            'model': _model,
            # 'thinking_type': 'adaptive',
            # 'max_retries': 3,
            # 'read_timeout': 120,
        }

    # ── Mixin 故障转移配置 ───────────────────────────────────────────────────
    # 按优先级排列，第一个失败自动切下一个
    mixin_config = {
        'llm_nos': [m[0] for m in _MODELS],   # ['deepseek-v3', 'deepseek-r1', ...]
        'max_retries': 10,
        'base_delay': 0.5,
    }

    print(f'[mykey] 从 ACC_PRODUCT_CONFIG_V2 加载配置')
    print(f'[mykey] Endpoint: {_endpoint}')
    print(f'[mykey] Network: {_net}')
    print(f'[mykey] 模型: {[m[0] for m in _MODELS]}')
else:
    print('[mykey] 未找到 ACC_PRODUCT_CONFIG_V2，无可用模型配置')
