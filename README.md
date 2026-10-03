# t-x — Termux Toolkit

A Termux-based multi-tool by **prvtspyyy404** (`saekacutie`): network utilities, account/temp-number helpers,
and device tools with a styled terminal UI, plus a self-update mechanism that pulls the latest version from this repo.

## Quick start (Termux)

```bash
pkg install python git -y
git clone https://github.com/saekacutie/t-x.git
cd t-x
python3 tx_toolkit.py
```

## Files

| File | Purpose |
|---|---|
| `tx_toolkit.py` | The toolkit (single-file app, stdlib + `requests`) |
| `README.md` | This file |

## Requirements

- Termux (Android) with Python 3
- `pip install requests`

## Self-update

The tool can update itself from `main`. Updates overwrite the local file and reload in place —
only update from this official repo.

## Security notes

- Never share session tokens or one-time codes the tool displays.
- Review the source before running any networked tool as root.
