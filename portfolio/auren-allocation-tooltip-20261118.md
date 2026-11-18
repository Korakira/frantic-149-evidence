# AUREN allocation tooltip formats fractional weights as dollar amounts

Reviewed on 18 November 2026 against commit `eef89475dece13ad243c6fc83d06f0ae1d1b0882`, still the upstream HEAD at verification time. This is a display/data-binding defect, not a claim that the risk engine or account balances are wrong.

## Actual and expected behavior

The allocation donut passes fractional portfolio weights to `go.Pie.values`, while putting the corresponding dollar amounts in `customdata`. Its dollar tooltip formats `value` instead of `customdata` in [app.py, lines 396–402](https://github.com/Ayush441-python/AUREN/blob/eef89475dece13ad243c6fc83d06f0ae1d1b0882/app.py#L396).

With a $10,000 portfolio and weights NVDA 40%, MSFT 30%, GOOGL 20%, ETH-USD 10%, hovering NVDA displays **`NVDA: 40% ($0)`**. The dollar allocation is **$4,000**. Changing the dollar portion of the hover template to use the existing `customdata` displays **`NVDA: 40% ($4,000)`**.

Other tested allocations were $3,000, $2,000 and $1,000; the original template formats all four as $0. A second synthetic $25,000 portfolio correctly contains $10,000 / $7,500 / $5,000 / $2,500 in `customdata`, while `values` remains 0.4 / 0.3 / 0.2 / 0.1.

## Minimal correction

```diff
- hovertemplate="%{label}: %{percent} ($%{value:,.0f})<extra></extra>",
+ hovertemplate="%{label}: %{percent} ($%{customdata:,.0f})<extra></extra>",
```

This preserves the fractional pie values and existing percentage labels. It changes only the dollar field in the tooltip.

## Offline reproduction using the actual upstream figure statement

Run from the repository root with pandas and Plotly installed. This extracts and executes the original `go.Figure(go.Pie(...))` assignment unchanged; it makes no API, market-data, wallet or paid-service calls.

```python
import ast
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
pie = next(n for n in ast.walk(tree)
    if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
    and ast.unparse(n.value.func) == 'go.Figure' and n.value.args
    and isinstance(n.value.args[0], ast.Call)
    and ast.unparse(n.value.args[0].func) == 'go.Pie')
scope = {
    'go': go,
    'weights': pd.Series({'NVDA': .4, 'MSFT': .3,
                         'GOOGL': .2, 'ETH-USD': .1}),
    'size': 10000.0,
    'donut_colors': ['#e6c36b', '#8e9196', '#666972', '#383e4b'],
    'BG': '#111318', 'TEXT': '#eef0f4',
}
exec(compile(ast.Module(body=[pie], type_ignores=[]),
             'upstream-app.py', 'exec'), scope)
fig = scope['fig']
assert fig.data[0].values[0] == .4
assert fig.data[0].customdata[0] == 4000
assert '%{value:,.0f}' in fig.data[0].hovertemplate
fig.write_html('original.html', include_plotlyjs=True)
fig.update_traces(hovertemplate=
    '%{label}: %{percent} ($%{customdata:,.0f})<extra></extra>')
fig.write_html('corrected.html', include_plotlyjs=True)
```

Open each generated file and hover the NVDA slice. Verified with Plotly 6.9.0 and an isolated Edge 157.0.4341.60 browser. Actual mouse-hover events produced these text readings from Plotly's rendered hover layer:

```json
[
  {"case": "original", "hover": "NVDA: 40% ($0)"},
  {"case": "corrected", "hover": "NVDA: 40% ($4,000)"}
]
```

Screenshots and the reproduction script were saved locally. The test renders the actual upstream figure in standalone Plotly with synthetic inputs; it does not claim to exercise the entire deployed Streamlit application. Both screenshots were visually checked.

## Review status

This issue appears distinct from the What-if normalization crash and from the 25 existing issues/PRs returned in the repository-wide search at verification time. Bounty eligibility, remaining budget and any award are unconfirmed. Prepared with AI assistance by Korakira for review under the project's published bug-bounty program.