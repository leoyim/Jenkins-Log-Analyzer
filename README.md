# Jenkins Log Analyzer

## 项目简介

Jenkins Log Analyzer 是一个自动化工具，用于获取 Jenkins 构建日志并分析失败原因。该工具集成了基础错误模式分析和 DeepSeek AI 智能分析功能，帮助开发者快速定位问题并提供修复建议。

---

## 功能特性

- **自动获取 Jenkins 构建日志**：通过 Jenkins API 自动获取最近的失败构建及其日志。
- **基础错误模式分析**：使用正则表达式匹配常见错误模式（如编译错误、测试失败、依赖问题等）。
- **AI 深度分析**：集成 DeepSeek AI，提供智能化的错误根因分析和修复建议。
- **生成分析报告**：输出详细的构建分析报告，包括基础分析结果和 AI 分析结果。

---

## 环境依赖

在运行此项目之前，请确保已安装以下依赖：

- Python 3.8 或更高版本
- `requests` 库
- `python-dotenv` 库
- `openai` 库

您可以通过以下命令安装依赖：

```bash
pip install requests python-dotenv openai
```

## 配置说明

在项目根目录下创建一个 `.env` 文件，并配置以下环境变量：

```bash
# Jenkins 配置
JENKINS_URL=<Jenkins 服务器地址>
JENKINS_USER=<Jenkins 用户名>
JENKINS_TOKEN=<Jenkins API Token>
JOB_NAME=<Jenkins 任务名称>

# DeepSeek AI 配置
DEEPSEEK_API_KEY=<DeepSeek API Key>
```

## 使用方法

1. **运行脚本** ： 在终端中运行以下命令：
   ```bash
   python main.py
   ```
2. **输出结果** ： 脚本会自动获取最近的失败构建日志，进行基础分析和 AI 深度分析，并输出分析报告。

## 输出示例

以下是一个示例分析报告：

```bash
🔧 Jenkins构建分析报告
任务名称: ExampleJob
构建编号: #123
构建时间: 2025-04-01 10:00:00
构建URL: http://jenkins.example.com/job/ExampleJob/123/

📊 基础分析结果:
  - 编译错误: 出现2次
    * error: Missing semicolon
    * error: Undefined variable 'x'
  - 测试失败: 出现1次
    * FAILED 3 tests

🤖 AI深度分析:
主要错误类型：编译错误
根本原因：代码中缺少分号，导致编译失败。
修复建议：检查代码中的语法错误，确保所有语句以分号结尾。
```

## 项目结构

Jenkins-Log-Analyzer/              
 ├── [main.py](http://_vscodecontentref_/1)          # 主程序文件                    
 ├── .env                                            # 环境变量配置文件                                      
 ├── [README.md](http://_vscodecontentref_/2)        # 项目说明文档                                               

## 常见问题

1. DeepSeek AI 分析失败

如果出现 `AI分析失败: HTTPSConnectionPool...` 错误，请检查以下内容：

* 确保网络连接正常。
* 检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 是否正确。
* 增加网络请求的超时时间（代码中默认设置为 30 秒）。

2. 无法获取 Jenkins 构建日志

* 确保 `.env` 文件中的 `JENKINS_URL`、`JENKINS_USER` 和 `JENKINS_TOKEN` 配置正确。
* 检查 Jenkins 服务器是否可访问。

## 贡献

欢迎提交 [Issue](https://github.com/leoyim/Jenkins-Log-Analyzer/issues "Issue") 或 [Pull Request](https://github.com/leoyim/Jenkins-Log-Analyzer/pulls "Pull Request") 来改进此项目。
