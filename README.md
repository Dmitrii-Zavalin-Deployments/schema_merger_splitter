# 🧩 Schema‑Merger‑Splitter

## 🔗 Input → Merge → Output Pipeline
A high‑fidelity schema transformation engine designed for structured JSON ingestion,
mapping, merging, validation, and CI‑optimized artifact generation.

### 🖼️ Pipeline Preview (Input → Merge → Output)

<table align="center" style="border-collapse: collapse; background: transparent;">
  <tr>
    <td style="padding: 8px; vertical-align: top;">
      <strong>validation_input_1.json</strong><br>
      <div style="font-size: 14px; color: #ccc;">p1: 4.8E+6<br>p2: 3.2E+6<br>v1: 45.0<br>v2: 62.0<br>h1: 120.0</div>
    </td>
    <td style="padding: 12px; font-size: 32px; color: #666; vertical-align: middle;">
      &rarr;
    </td>
    <td style="padding: 8px; vertical-align: top;">
      <strong>validation_input_2.json</strong><br>
      <div style="font-size: 14px; color: #ccc;">pressure: {"p1":1500.0,"p2":324.0}<br>velocity: {"v1":0.5,"v2":0.8}<br>height: {"h1":0.0,"h2":0.1}<br>properties: {"rho":1000.0,"temperature":10.0}</div>
    </td>
    <td style="padding: 12px; font-size: 32px; color: #666; vertical-align: middle;">
      &rarr;
    </td>
    <td style="padding: 8px; vertical-align: top;">
      <strong>validation_output.json</strong><br>
      <div style="font-size: 14px; color: #ccc;">p_min: 4800000.0<br>p_max: 3200000.0<br>v_min: 45.0<br>v_max: 62.0<br>h: 0.1</div>
    </td>
  </tr>
</table>

### 📚 Resources & Documentation
- **Tutorial/Book:** ***currently in development***

---

### 🧮 Performance Audit:
### Audit: 2026-07-21 14:30:35 UTC
- **Branch:** `main`
- **Status:** `success`
- **Run:** [Detailed Execution Logs](https://github.com/Dmitrii-Zavalin-Deployments/schema_merger_splitter/actions/runs/29839369897)
- **CPU Load:** `0.0%`
- **Memory Usage:** `22/15993MB`
---
### Audit: 2026-07-21 13:42:37 UTC
- **Branch:** `main`
- **Status:** `success`
- **Run:** [Detailed Execution Logs](https://github.com/Dmitrii-Zavalin-Deployments/schema_merger_splitter/actions/runs/29835622539)
- **CPU Load:** `0.0%`
- **Memory Usage:** `22/15989MB`
---
### Audit: 2026-07-17 18:42:40 UTC
- **Branch:** `main`
- **Status:** `success`
- **Run:** [Detailed Execution Logs](https://github.com/Dmitrii-Zavalin-Deployments/schema_merger_splitter/actions/runs/29604780924)
- **CPU Load:** `0.0%`
- **Memory Usage:** `22/15988MB`
---
### Audit: 2026-07-15 15:52:42 UTC
- **Branch:** `main`
- **Status:** `success`
- **Run:** [Detailed Execution Logs](https://github.com/Dmitrii-Zavalin-Deployments/schema_merger_splitter/actions/runs/29429963092)
- **CPU Load:** `0.0%`
- **Memory Usage:** `22/15988MB`
---
