# API 文档

DLP3D Web Backend 为动作数据管理、用户管理和角色配置提供全面的 RESTful API。要获取详细的 API 文档，您可以：

## 交互式 API 文档

服务运行后，访问交互式 API 文档：
- **Swagger UI**：`http://localhost:18080/docs`
- **ReDoc**：`http://localhost:18080/redoc`

## 编程式 API 参考

对于开发者，完整的 API 实现和端点定义可以在以下文件中找到：
- **服务器实现**：`dlp3d_web_backend/service/server.py`
- **请求/响应模型**：`dlp3d_web_backend/service/requests.py` 和 `dlp3d_web_backend/service/responses.py`

## API 分类

API 按以下主要类别组织：
- **用户管理** - 用户生命周期、认证和凭据管理
- **角色管理** - 角色创建、配置和管理
- **动作数据访问** - 动作文件、静止姿态数据、网格文件和元数据访问
- **系统管理** - 健康检查、日志记录和操作工具

## API 特性

- **OpenAPI 文档**：在 `/docs` 提供交互式 API 文档
- **错误处理**：标准化的错误响应，包含详细的错误消息
- **认证**：基于用户的认证和凭据管理
- **缓存**：动作数据的智能缓存，具有版本控制功能
- **验证**：全面的请求/响应验证
- **CORS 支持**：可配置的跨域资源共享

---

