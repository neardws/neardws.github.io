#!/usr/bin/env python3
"""
MinerU PDF Parser Client for OpenClaw
通过 SSH 调用 Mac Mini 上部署的 MinerU Gradio HTTP API
"""

import argparse
import json
import sys
import os
import subprocess
import tempfile

# 默认配置
DEFAULT_HOST = "192.168.31.114"
DEFAULT_PORT = 7860
DEFAULT_USER = "neardws"


class MinerUClient:
    """通过 SSH 调用 MinerU Gradio API"""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, user=DEFAULT_USER):
        self.host = host
        self.port = port
        self.user = user
        
    def _run_ssh(self, cmd):
        """在远程主机上执行命令"""
        full_cmd = ["ssh", f"{self.user}@{self.host}", cmd]
        result = subprocess.run(full_cmd, capture_output=True, text=True, shell=False)
        return result
    
    def parse_pdf(self, pdf_path, backend="hybrid-auto-engine", lang="ch", 
                  formula=True, table=True):
        """
        调用 MinerU 解析 PDF
        
        Args:
            pdf_path: PDF 文件本地路径（会被传到 Mac Mini）
            backend: 解析后端
            lang: 语言
            formula: 是否启用公式识别
            table: 是否启用表格识别
            
        Returns:
            dict: {success: bool, status: str, markdown: str, error: str}
        """
        try:
            # 1. 将本地文件传到 Mac Mini 临时目录
            remote_filename = f"mineru_{os.path.basename(pdf_path)}"
            remote_path = f"/tmp/{remote_filename}"
            
            # 使用 scp 上传文件
            scp_result = subprocess.run(
                ["scp", "-q", pdf_path, f"{self.user}@{self.host}:{remote_path}"],
                capture_output=True, text=True
            )
            
            if scp_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"文件上传失败: {scp_result.stderr}"
                }
            
            # 2. 在 Mac Mini 上创建 Python 脚本并执行
            script_content = f'''#!/usr/bin/env python3
import requests
import json
import os
import sys

remote_path = "{remote_path}"
port = {self.port}
backend = "{backend}"
lang = "{lang}"
formula = {str(formula)}
table = {str(table)}

try:
    # 1. 上传文件到 Gradio
    with open(remote_path, "rb") as f:
        resp = requests.post(f"http://localhost:{{port}}/gradio_api/upload", files={{"files": f}})
    
    if resp.status_code != 200:
        print(json.dumps({{"success": False, "error": f"上传失败: {{resp.status_code}}"}}))
        sys.exit(0)
    
    file_path = resp.json()[0]
    file_size = os.path.getsize(remote_path)
    
    # 2. 构造 FileData
    file_data = {{
        "path": file_path,
        "url": None,
        "size": file_size,
        "orig_name": os.path.basename(remote_path),
        "mime_type": "application/pdf",
        "is_stream": False,
        "meta": {{"_type": "gradio.FileData"}}
    }}
    
    # 3. 调用解析
    payload = {{
        "data": [file_data, backend, lang, formula, table]
    }}
    
    resp = requests.post(f"http://localhost:{{port}}/gradio_api/call/parse_pdf", json=payload)
    if resp.status_code != 200:
        print(json.dumps({{"success": False, "error": f"API调用失败: {{resp.status_code}}"}}))
        sys.exit(0)
    
    event_id = resp.json()["event_id"]
    
    # 4. 获取结果
    resp = requests.get(f"http://localhost:{{port}}/gradio_api/call/parse_pdf/{{event_id}}", stream=True)
    
    result = None
    for line in resp.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                data = line_str[6:]
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                    if isinstance(event, list) and len(event) >= 2:
                        result = event
                except:
                    pass
    
    # 5. 清理
    os.remove(remote_path)
    
    if result:
        print(json.dumps({{
            "success": True,
            "status": result[0],
            "markdown": result[1] if len(result) > 1 else ""
        }}))
    else:
        print(json.dumps({{"success": False, "error": "解析结果为空"}}))

except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
'''
            
            # 将脚本写入远程临时文件
            remote_script = f"/tmp/mineru_script_{os.getpid()}.py"
            
            # 使用 echo 写入脚本（避免引号问题）
            write_cmd = f'cat > {remote_script} << \'SCRIPT_EOF\'\n{script_content}\nSCRIPT_EOF'
            write_result = self._run_ssh(write_cmd)
            
            if write_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"写入远程脚本失败: {write_result.stderr}"
                }
            
            # 执行脚本
            exec_cmd = f'export MAMBA_ROOT_PREFIX=/Users/neardws/micromamba && /tmp/mineru-install/micromamba run -n mineru python3 {remote_script}'
            exec_result = self._run_ssh(exec_cmd)
            
            # 清理远程脚本
            self._run_ssh(f"rm -f {remote_script}")
            
            # 解析结果
            if exec_result.returncode == 0 and exec_result.stdout:
                try:
                    return json.loads(exec_result.stdout.strip())
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"解析返回结果失败: {e}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"远程执行失败: {exec_result.stderr}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"解析失败: {str(e)}"
            }


def main():
    parser = argparse.ArgumentParser(
        description="MinerU PDF Parser Client - 通过 SSH 调用 Mac Mini 上的服务"
    )
    parser.add_argument("pdf", help="PDF 文件路径")
    parser.add_argument("--host", default=DEFAULT_HOST, 
                       help=f"Mac Mini 主机地址 (默认: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                       help=f"Gradio 服务端口 (默认: {DEFAULT_PORT})")
    parser.add_argument("--user", default=DEFAULT_USER,
                       help=f"SSH 用户名 (默认: {DEFAULT_USER})")
    parser.add_argument("--backend", default="hybrid-auto-engine",
                       choices=["hybrid-auto-engine", "pipeline", "vlm-auto-engine"],
                       help="解析后端 (默认: hybrid-auto-engine)")
    parser.add_argument("--lang", default="ch",
                       choices=["ch", "en", "ch_server", "ch_lite", "korean", "japan"],
                       help="文档语言 (默认: ch)")
    parser.add_argument("--formula", action="store_true", default=True,
                       help="启用公式识别 (默认)")
    parser.add_argument("--no-formula", dest="formula", action="store_false",
                       help="禁用公式识别")
    parser.add_argument("--table", action="store_true", default=True,
                       help="启用表格识别 (默认)")
    parser.add_argument("--no-table", dest="table", action="store_false",
                       help="禁用表格识别")
    parser.add_argument("--output", "-o", help="输出 markdown 文件路径")
    
    args = parser.parse_args()
    
    # 检查文件
    if not os.path.exists(args.pdf):
        print(json.dumps({
            "success": False, 
            "error": f"文件不存在: {args.pdf}"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    if not args.pdf.lower().endswith('.pdf'):
        print(json.dumps({
            "success": False,
            "error": "文件必须是 PDF 格式"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    # 检查 SSH 是否可用
    ssh_test = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", f"{args.user}@{args.host}", "echo ok"],
        capture_output=True, text=True
    )
    if ssh_test.returncode != 0:
        print(json.dumps({
            "success": False,
            "error": f"无法连接到 {args.user}@{args.host}，请检查 SSH 配置"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    # 创建客户端并调用
    client = MinerUClient(args.host, args.port, args.user)
    result = client.parse_pdf(
        args.pdf,
        backend=args.backend,
        lang=args.lang,
        formula=args.formula,
        table=args.table
    )
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 保存到文件
    if args.output and result.get("success") and result.get("markdown"):
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result["markdown"])
            print(f"\n✓ Markdown 已保存至: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"\n✗ 保存文件失败: {e}", file=sys.stderr)
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
