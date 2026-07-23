# 🧩 Schema‑Merger‑Splitter

## 🔗 Input → Merge → Output Pipeline
A high‑fidelity schema transformation engine designed for structured JSON ingestion,
mapping, merging, validation, and CI‑optimized artifact generation.

### 🖼️ Pipeline Preview (Inputs → Selection → Output)

<table align="center" style="border-collapse: collapse; background: transparent;">
  <tr>
    <td style="padding: 10px; vertical-align: top; text-align: left;">
      <strong>validation_input_1.json</strong><br>
      <pre style="margin-top: 6px; margin-bottom: 0px; font-size: 10px;"><code>{
  "p1": 4.8E+6,
  "p2": 3.2E+6,
  "v1": 45.0,
  "v2": 62.0,
  "h1": 120.0,
  "h2": 350.0
}</code></pre>
    </td>
    <td rowspan="3" style="padding: 8px; font-size: 24px; color: #666; vertical-align: middle; text-align: center;">
      &rarr;
    </td>
    <td rowspan="3" style="padding: 10px; vertical-align: top; text-align: left;">
      <strong>validation_task.json (Selection)</strong><br>
      <div style="font-size: 13px; margin-top: 6px; line-height: 1.4;"><strong>validation_input_1.json</strong><br><code>$.p1</code> &rarr; <code>p_min</code><br><code>$.p2</code> &rarr; <code>p_max</code><br><code>$.v1</code> &rarr; <code>v_min</code><br><code>$.v2</code> &rarr; <code>v_max</code><br><br><strong>validation_input_2.json</strong><br><code>$.height.h2</code> &rarr; <code>h</code><br><code>$.properties</code> &rarr; <code>properties</code></div>
    </td>
    <td rowspan="3" style="padding: 8px; font-size: 24px; color: #666; vertical-align: middle; text-align: center;">
      &rarr;
    </td>
    <td rowspan="3" style="padding: 10px; vertical-align: top; text-align: left;">
      <strong>validation_output.json</strong><br>
      <pre style="margin-top: 6px; margin-bottom: 0px; font-size: 10px;"><code>{
  "p_min": 4800000.0,
  "p_max": 3200000.0,
  "v_min": 45.0,
  "v_max": 62.0,
  "h": 0.1,
  "properties": {
    "rho": 1000.0,
    "temperature": 10.0
  }
}</code></pre>
    </td>
  </tr>
  <tr>
    <td style="padding: 2px; text-align: center; font-size: 20px; font-weight: bold; color: #888;">
      +
    </td>
  </tr>
  <tr>
    <td style="padding: 10px; vertical-align: top; text-align: left;">
      <strong>validation_input_2.json</strong><br>
      <pre style="margin-top: 6px; margin-bottom: 0px; font-size: 10px;"><code>{
  "pressure": {
    "p1": 1500.0,
    "p2": 324.0
  },
  "velocity": {
    "v1": 0.5,
    "v2": 0.8
  },
  "height": {
    "h1": 0.0,
    "h2": 0.1
  },
  "properties": {
    "rho": 1000.0,
    "temperature": 10.0
  }
}</code></pre>
    </td>
  </tr>
</table>

### 📚 Resources & Documentation
- **Tutorial/Book:** ***currently in development***

---

### 🧮 Performance Audit:
### Audit: 2026-07-23 16:57:15 UTC
- **Branch:** `main`
- **Status:** `success`
- **Run:** [Detailed Execution Logs](https://github.com/Dmitrii-Zavalin-Deployments/schema_merger_splitter/actions/runs/30027285994)
- **CPU Load:** `0.0%`
- **Memory Usage:** `21/15989MB`
