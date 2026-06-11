import re

css = open('C:/Users/ALEKHYA/.gemini/antigravity/scratch/dsa-prep/frontend/src/App.css').read()

replacements = [
    (r'font-family:\s*-apple-system[^;]+;', 'font-family: var(--font-ui);'),
    (r'font-family:\s*\'Courier New\'[^;]+;', 'font-family: var(--font-mono);'),
    (r'background-color:\s*#f4f7f6;', 'background-color: var(--bg-main);'),
    (r'background:\s*#f4f7f6;', 'background: var(--bg-main);'),
    (r'color:\s*#333(;|\s*})', r'color: var(--text-main)\1'),
    (r'background-color:\s*#2c3e50;', 'background-color: var(--bg-header);'),
    (r'background:\s*white;', 'background: var(--bg-card);'),
    (r'background-color:\s*white;', 'background-color: var(--bg-card);'),
    (r'color:\s*white(;|\s*})', r'color: var(--text-inverse)\1'),
    (r'color:\s*#555(;|\s*})', r'color: var(--text-muted)\1'),
    (r'border-right:\s*1px solid #eee;', 'border-right: 1px solid var(--border-color);'),
    (r'border-bottom:\s*2px solid #eee;', 'border-bottom: 2px solid var(--border-color);'),
    (r'border-bottom:\s*1px solid #eee;', 'border-bottom: 1px solid var(--border-color);'),
    (r'border:\s*1px solid #eee;', 'border: 1px solid var(--border-color);'),
    (r'background-color:\s*#f8f9fa;', 'background-color: var(--bg-hover);'),
    (r'border-color:\s*#ddd;', 'border-color: var(--border-input);'),
    (r'background-color:\s*#ebf5fb;', 'background-color: var(--bg-active);'),
    (r'border-color:\s*#3498db;', 'border-color: var(--accent);'),
    (r'color:\s*#bdc3c7(;|\s*})', r'color: var(--text-muted)\1'),
    (r'color:\s*#e74c3c(;|\s*})', r'color: var(--danger)\1'),
    (r'color:\s*#888(;|\s*})', r'color: var(--text-muted)\1'),
    (r'color:\s*#999(;|\s*})', r'color: var(--text-muted)\1'),
    (r'border:\s*1px solid #ddd;', 'border: 1px solid var(--border-input);'),
    (r'background-color:\s*#3498db;', 'background-color: var(--accent);'),
    (r'background:\s*#3498db;', 'background: var(--accent);'),
    (r'background-color:\s*#2980b9;', 'background-color: var(--accent-hover);'),
    (r'background-color:\s*#95a5a6;', 'background-color: var(--text-muted);'),
    (r'color:\s*#3498db(;|\s*})', r'color: var(--accent)\1'),
    (r'border:\s*2px solid #3498db;', 'border: 2px solid var(--accent);'),
    (r'color:\s*#2c3e50(;|\s*})', r'color: var(--text-header)\1'),
    (r'color:\s*#444(;|\s*})', r'color: var(--text-main)\1'),
    (r'border-left:\s*4px solid #3498db;', 'border-left: 4px solid var(--accent);'),
    (r'background:\s*#ecf0f1;', 'background: var(--bg-hover);'),
    (r'color:\s*#7f8c8d(;|\s*})', r'color: var(--text-muted)\1'),
    (r'background-color:\s*#2d2d2d;', 'background-color: var(--code-bg);'),
    (r'color:\s*#f8f8f2(;|\s*})', r'color: var(--text-inverse)\1'),
    (r'background:\s*#fdf0ed;', 'background: var(--danger-bg);'),
    (r'border-left:\s*4px solid #e74c3c;', 'border-left: 4px solid var(--danger);'),
    (r'color:\s*#c0392b(;|\s*})', r'color: var(--danger)\1'),
    (r'background-color:\s*#e67e22;', 'background-color: var(--warning);'),
    (r'background-color:\s*#d35400;', 'background-color: var(--warning-hover);'),
    (r'border-top:\s*4px solid #f1c40f;', 'border-top: 4px solid var(--warning);'),
    (r'border-color:\s*#f1c40f;', 'border-color: var(--warning);'),
    (r'background-color:\s*#f1c40f;', 'background-color: var(--warning);'),
    (r'background-color:\s*#f39c12;', 'background-color: var(--warning-hover);'),
    (r'background:\s*#f1f2f6;', 'background: var(--bg-hover);'),
    (r'border-bottom:\s*1px solid #f1f2f6;', 'border-bottom: 1px solid var(--border-color);'),
    (r'border:\s*1px solid rgba\(231, 76, 60, 0.2\);', 'border: 1px solid var(--danger);'),
    (r'background:\s*#fdfdfd;', 'background: var(--bg-card);'),
    (r'color:\s*#34495e(;|\s*})', r'color: var(--text-header)\1'),
    (r'background-color:\s*#9b59b6;', 'background-color: var(--accent);'),
    (r'background-color:\s*#8e44ad;', 'background-color: var(--accent-hover);'),
    (r'color:\s*#95a5a6(;|\s*})', r'color: var(--text-muted)\1'),
    (r'background:\s*#d4efdf;', 'background: var(--success-bg);'),
    (r'color:\s*#27ae60(;|\s*})', r'color: var(--success)\1'),
    (r'background:\s*#fdebd0;', 'background: var(--warning-bg);'),
    (r'color:\s*#f39c12(;|\s*})', r'color: var(--warning)\1'),
    (r'background:\s*#fadbd8;', 'background: var(--danger-bg);'),
]

for pat, repl in replacements:
    css = re.sub(pat, repl, css)

header = '''@import url("https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap");

:root {
  --bg-main: #f4f7f6;
  --bg-card: #ffffff;
  --bg-header: #2c3e50;
  --bg-hover: #f8f9fa;
  --bg-active: #ebf5fb;
  --text-main: #333333;
  --text-muted: #888888;
  --text-header: #2c3e50;
  --text-inverse: #ffffff;
  --border-color: #eeeeee;
  --border-input: #dddddd;
  --accent: #3498db;
  --accent-hover: #2980b9;
  --danger: #e74c3c;
  --danger-bg: #fdf0ed;
  --warning: #e67e22;
  --warning-hover: #d35400;
  --warning-bg: #fdebd0;
  --success: #27ae60;
  --success-bg: #d4efdf;
  --code-bg: #2d2d2d;
  --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: 'Fira Code', 'JetBrains Mono', monospace;
}

[data-theme="dark"] {
  --bg-main: #121212;
  --bg-card: #1e1e1e;
  --bg-header: #1f1f1f;
  --bg-hover: #2a2a2a;
  --bg-active: #2c3e50;
  --text-main: #e0e0e0;
  --text-muted: #aaaaaa;
  --text-header: #e0e0e0;
  --text-inverse: #ffffff;
  --border-color: #333333;
  --border-input: #444444;
  --accent: #3498db;
  --accent-hover: #5dade2;
  --danger: #e74c3c;
  --danger-bg: #4a1c17;
  --warning: #e67e22;
  --warning-hover: #f39c12;
  --warning-bg: #4a2c00;
  --success: #2ecc71;
  --success-bg: #144525;
  --code-bg: #0d0d0d;
}

'''

with open('C:/Users/ALEKHYA/.gemini/antigravity/scratch/dsa-prep/frontend/src/App.css', 'w') as f:
    f.write(header + css)
