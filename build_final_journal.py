# -*- coding: utf-8 -*-
import os
import re
import json
import html as html_lib

ws = r"F:\Embedded_Workspace"
html_path = os.path.join(ws, "embedded_study_journal.html")

with open(html_path, "r", encoding="utf-8") as f:
    base_html = f.read()

# 1. 读取 15 篇学习日志
logs_dir = os.path.join(ws, "学习日志")
log_files = sorted([f for f in os.listdir(logs_dir) if f.endswith(".md")], reverse=True)
logs_html = ""

for idx, lf in enumerate(log_files):
    p = os.path.join(logs_dir, lf)
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        raw_md = f.read()
    date_str = lf.replace(".md", "")
    
    # 提取总结
    summary_match = re.search(r"##\s*当日小结[^\n]*\n(.*?)(?=\n##|\Z)", raw_md, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
    else:
        summary_text = raw_md[:200].strip()
    clean_summary = re.sub(r"[#*`]", "", summary_text)[:140] + "..."
    escaped_md = html_lib.escape(raw_md)
    
    logs_html += f"""
    <div class="border border-[var(--card-border,#e2e8f0)] bg-[var(--card,#ffffff)] rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div class="flex items-center justify-between gap-2 flex-wrap mb-2">
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-1 rounded-md text-xs font-bold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">📅 {date_str}</span>
          <span class="text-xs text-[var(--muted-foreground,#64748b)]">文件名: {lf}</span>
        </div>
        <button onclick="toggleLogDetail('log_content_{idx}')" class="text-xs font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 flex items-center gap-1 cursor-pointer">
          <span>展开全文</span>
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </button>
      </div>
      <p class="text-xs text-[var(--foreground,#0f172a)] leading-relaxed bg-[var(--background,#f8fafc)] p-3 rounded-lg border border-[var(--card-border,#e2e8f0)] font-sans">
        {html_lib.escape(clean_summary)}
      </p>
      <div id="log_content_{idx}" class="hidden mt-3 pt-3 border-t border-[var(--card-border,#e2e8f0)]">
        <pre class="text-xs font-mono bg-slate-900 text-slate-100 p-4 rounded-xl overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-96 custom-scrollbar">{escaped_md}</pre>
      </div>
    </div>
    """

# 2. 读取 3 个核心代码
def get_code_escaped(rel_path):
    p = os.path.join(ws, rel_path)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return html_lib.escape(f.read())
    return "// 读取失败"

code_1 = get_code_escaped("code/week01/FileName.c")
code_2 = get_code_escaped("code/week04/函数.c")
code_3 = get_code_escaped("code/week04/数组退化.c")

print("Generated logs HTML length:", len(logs_html))