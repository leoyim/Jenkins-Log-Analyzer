#!/usr/bin/env python3
"""
Jenkins 日志分析工具 - 自动获取构建日志并分析失败原因
集成 DeepSeek AI 进行智能分析
"""

import os
import re
import requests
import time
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

class JenkinsLogAnalyzer:
    def __init__(self):
        self.base_url = os.getenv("JENKINS_URL").rstrip('/')
        self.auth = (os.getenv("JENKINS_USER"), os.getenv("JENKINS_TOKEN"))
        self.job_name = os.getenv("JOB_NAME")
        self.max_log_size = 5000  # 限制日志大小以避免内存问题

    def fetch_json(self, url):
        """通用方法：获取JSON数据"""
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_job_info(self):
        """获取任务基本信息"""
        url = f"{self.base_url}/job/{self.job_name}/api/json"
        return self.fetch_json(url)

    def get_failed_builds(self, limit=5):
        """获取最近的失败构建"""
        job_info = self.get_job_info()
        if not job_info:
            return []

        failed_builds = []
        for build in job_info['builds'][:limit]:
            build_info = self.fetch_json(f"{self.base_url}/job/{self.job_name}/{build['number']}/api/json")
            if build_info and build_info.get('result') == 'FAILURE':
                failed_builds.append({
                    'number': build['number'],
                    'url': build_info['url'],
                    'timestamp': build_info['timestamp']
                })
        return failed_builds

    def get_log(self, build_number):
        """获取构建日志"""
        url = f"{self.base_url}/job/{self.job_name}/{build_number}/consoleText"
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.text[:self.max_log_size]  # 限制日志大小
        except requests.exceptions.RequestException as e:
            print(f"获取构建 #{build_number} 日志失败: {e}")
            return None

    def basic_analysis(self, log):
        """基础错误模式分析"""
        error_patterns = {
            "编译错误": r"error: .*|FAILED to compile|编译失败",
            "测试失败": r"FAILED \d+ tests?|测试用例.*失败",
            "依赖问题": r"Unable to resolve dependency|404 Not Found|无法下载依赖",
            "超时": r"Timeout.*exceeded|执行超时",
            "权限问题": r"Permission denied|权限被拒绝",
            "磁盘空间": r"No space left on device|磁盘空间不足",
            "内存不足": r"OutOfMemoryError|内存溢出",
            "网络问题": r"Connection refused|连接超时|无法连接到"
        }

        findings = {}
        for category, pattern in error_patterns.items():
            matches = re.findall(pattern, log, re.IGNORECASE)
            if matches:
                findings[category] = {
                    'count': len(matches),
                    'samples': list(set(matches))[:3]  # 展示前3个不重复样例
                }
        
        return findings

class DeepSeekAIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"
        self.max_tokens = 2000

        if not self.api_key:
            raise ValueError("未配置DeepSeek API Key")

        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def analyze(self, log_snippet):
        """调用DeepSeek AI进行分析"""
        prompt = f"""
        你是一个资深的DevOps工程师，请分析以下Jenkins构建日志片段：

        分析要求：
        1. 识别主要错误类型
        2. 分析根本原因
        3. 提供具体的修复建议

        日志内容：
        {log_snippet}
        """

        try:
            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                max_tokens=self.max_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI分析失败: {str(e)}"

def generate_report(build_info, basic_findings, ai_analysis):
    """生成分析报告"""
    report = [
        f"\n🔧 Jenkins构建分析报告",
        f"任务名称: {os.getenv('JOB_NAME')}",
        f"构建编号: #{build_info['number']}",
        f"构建时间: {build_info['timestamp']}",
        f"构建URL: {build_info['url']}",
        "\n📊 基础分析结果:"
    ]

    if basic_findings:
        for category, data in basic_findings.items():
            report.append(f"  - {category}: 出现{data['count']}次")
            for sample in data['samples']:
                report.append(f"    * {sample}")
    else:
        report.append("  - 未识别到常见错误模式")

    report.append("\n🤖 AI深度分析:")
    report.append(ai_analysis)

    return "\n".join(report)

def main():
    # 初始化分析器
    jenkins_analyzer = JenkinsLogAnalyzer()
    ai_analyzer = DeepSeekAIAnalyzer()

    # 获取失败构建
    print("正在获取失败构建列表...")
    failed_builds = jenkins_analyzer.get_failed_builds()
    if not failed_builds:
        print("未发现失败的构建")
        return

    # 分析所有失败构建
    for build in failed_builds:
        print(f"\n正在分析构建 #{build['number']}...")
        
        # 获取日志
        log = jenkins_analyzer.get_log(build['number'])
        if not log:
            print("无法获取构建日志")
            continue

        # 分析日志
        basic_findings = jenkins_analyzer.basic_analysis(log)
        ai_analysis = ai_analyzer.analyze(log)

        # 生成报告
        report = generate_report(build, basic_findings, ai_analysis)
        print(report)

if __name__ == "__main__":
    main()