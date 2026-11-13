[![ZEUS LAB](https://zero-trace-ship-kit.zeus-lab-global.workers.dev/assets/readme-banner.png)](https://zero-trace-ship-kit.zeus-lab-global.workers.dev/hq/?utm_source=github_repo)

# quant-first-passage-sim

[![leak check: zero-trace](https://zero-trace-ship-kit.zeus-lab-global.workers.dev/badge/zero-trace.svg)](https://zero-trace-ship-kit.zeus-lab-global.workers.dev/badge/?utm_source=readme_badge)

Which comes first on an account with rules — the profit target, the daily loss limit or the maximum loss? A small seeded Monte Carlo script answers that for the numbers you enter.

MIT-licensed · Python standard library only · same model as the free in-browser calculator

**[Open the browser calculator](https://zero-trace-ship-kit.zeus-lab-global.workers.dev/quant/?utm_source=github_repo)** | **[CSV audit + process breaker kit ($99)](https://zeuslab.gumroad.com/l/quant-drawdown-bot-guard-kit)**

```sh
git clone https://github.com/ZEUSLABZERO/quant-first-passage-sim.git
cd quant-first-passage-sim
python3 first_passage.py --win 45 --rr 1.5 --risk 1 --tpd 3 --days 30 --daily 5 --maxl 10 --target 8
```

```
5,000 paths · seed 1
  target first              76.9 %
  ...
```

Change only `--risk` and watch the order of events change. Same seed, same result.

## The model, stated plainly

- A trade is `+rr × risk` with probability `win`, otherwise `−risk`. Trades are independent.
- Risk is a constant share of the start balance. The balance starts at 100 and cannot go below 0.
- Rules are checked after every trade. A path stops at the first event (`--cont` keeps trading).
- `0.0 %` means the event did not occur in these paths, or occurred below the displayed precision.

## What it is not

It is arithmetic on your inputs. It is not a forecast, a signal, a recommendation to trade or investment advice. Real trades are not independent, and each firm evaluates its rules in its own way; this script reproduces none of them.

The paid **Quant Drawdown & Bot Guard Kit** ($99, one-time) audits your own trade CSV with a bootstrap, adds a process breaker that stops a bot at a daily loss limit, and a commit gate for exchange keys. It is calculation and process control only.

## License

MIT (see `LICENSE`). © 2026 ZEUS LAB

---

**日本語の要約：** ルールのある口座で、利益目標・1日の損失上限・最大損失のどれに先に届くかを、入力した数字について数える小さな計算スクリプトです。無料のブラウザ計算機と同じ模型で、シードを固定すれば同じ結果になります。予測でも売買の推奨でもなく、投資助言ではありません。
