# Freedom AI - API 文档

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **WebSocket**: `ws://localhost:8000/api/v1/ws/chat/{username}`

## 认证

当前版本暂不需要认证，通过username标识用户。

---

## 聊天接口

### 1. 发送消息

**接口**: `POST /api/v1/chat/`

**描述**: 发送消息给AI并获取回复

**请求体**:
```json
{
  "username": "user123",
  "message": "你好，今天天气怎么样？",
  "stream": false
}
```

**响应**:
```json
{
  "success": true,
  "content": "你好！今天天气不错哦，很适合出门散步呢😊",
  "message_id": 42,
  "timestamp": "2025-01-15T10:30:00"
}
```

### 2. 获取聊天历史

**接口**: `GET /api/v1/chat/history`

**参数**:
- `username` (必需): 用户名
- `limit` (可选): 返回数量，默认50
- `offset` (可选): 偏移量，默认0

**响应**:
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "你好",
      "is_proactive": false,
      "created_at": "2025-01-15T10:00:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "你好！很高兴见到你😊",
      "is_proactive": false,
      "created_at": "2025-01-15T10:00:05"
    }
  ],
  "count": 2
}
```

### 3. 清除聊天历史

**接口**: `DELETE /api/v1/chat/history`

**参数**:
- `username` (必需): 用户名

**响应**:
```json
{
  "success": true,
  "message": "聊天历史已清除"
}
```

---

## 用户接口

### 1. 获取用户信息

**接口**: `GET /api/v1/users/{username}`

**响应**:
```json
{
  "id": 1,
  "username": "user123",
  "nickname": "小明",
  "avatar": null,
  "profile": {
    "interests": ["编程", "音乐"],
    "location": "北京"
  },
  "preferences": {
    "language": "zh-CN"
  },
  "is_online": true,
  "last_active_at": "2025-01-15T10:30:00",
  "created_at": "2025-01-01T08:00:00"
}
```

### 2. 更新用户画像

**接口**: `PUT /api/v1/users/{username}/profile`

**请求体**:
```json
{
  "profile": {
    "interests": ["编程", "音乐", "旅行"],
    "occupation": "软件工程师",
    "location": "北京"
  }
}
```

**响应**:
```json
{
  "success": true,
  "message": "用户画像更新成功",
  "profile": {
    "interests": ["编程", "音乐", "旅行"],
    "occupation": "软件工程师",
    "location": "北京"
  }
}
```

### 3. 更新用户偏好

**接口**: `PUT /api/v1/users/{username}/preferences`

**请求体**:
```json
{
  "preferences": {
    "language": "zh-CN",
    "theme": "dark",
    "notifications": true
  }
}
```

---

## WebSocket 实时通信

### 连接

**端点**: `ws://localhost:8000/api/v1/ws/chat/{username}`

### 消息格式

**客户端发送**:
```json
{
  "message": "你好，在吗？"
}
```

**服务器响应**:

1. **系统消息** (连接成功):
```json
{
  "type": "system",
  "content": "欢迎回来，小明！",
  "timestamp": null
}
```

2. **普通消息**:
```json
{
  "type": "message",
  "role": "assistant",
  "content": "在的！有什么可以帮你吗？",
  "message_id": 42,
  "timestamp": "2025-01-15T10:30:00"
}
```

3. **主动消息** (AI主动发起):
```json
{
  "type": "proactive",
  "role": "assistant",
  "content": "嘿，最近过得怎么样？有什么有趣的事情吗？😊",
  "timestamp": null
}
```

4. **错误消息**:
```json
{
  "type": "error",
  "content": "处理失败，请稍后重试",
  "timestamp": null
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

# 发送消息
response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    json={
        "username": "user123",
        "message": "今天天气怎么样？"
    }
)
print(response.json())

# 获取聊天历史
response = requests.get(
    "http://localhost:8000/api/v1/chat/history",
    params={"username": "user123", "limit": 10}
)
print(response.json())
```

### JavaScript 示例

```javascript
// 发送消息
fetch('http://localhost:8000/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'user123',
    message: '今天天气怎么样？'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// WebSocket 连接
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat/user123');

ws.onopen = () => {
  console.log('已连接');
  ws.send(JSON.stringify({ message: '你好' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};
```

---

## 注意事项

1. 所有时间戳均为UTC时间，ISO 8601格式
2. WebSocket连接会自动处理重连
3. 主动消息只会发送给在线用户
4. 聊天历史和记忆会持久化保存
5. LLM API密钥请妥善保管，不要泄露
