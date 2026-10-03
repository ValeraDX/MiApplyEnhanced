<div align="center">

# THIS IS A FORK OF MIAPPLY THAT ADDS AUTOMATIC LAG COMPENSATION!!! IT'S NOT ON PYPI OR ANYTHING (YET)!!!

<a href="https://github.com/MiForge/MiCommunityTool/releases/latest">
  <img src="https://img.shields.io/badge/MiCommunityTool-%23FF6900?style=flat&logo=xiaomi&logoColor=white" alt="MiCommunityTool" width="200"/>
</a>

</div>

---

- Upstream [micommunity library](https://github.com/MiForge/MiCommunityTool/tree/main/micommunity) - A Python library for interacting with Mi Community APIs.
- [Credits](https://github.com/ValeraDX/MiApplyEnhanced/blob/main/CREDITS)

---


<div align="center">

[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

</div>

## How 2 use:
### IMPORTANT!!!
If you are on Termux, set Battery & Data usage to "Unrestricted" and enable Wakelock to prevent the system from killing the process. You can do this by running:
```
termux-wake-lock
```
If you're on a PC, make sure your PC does not go to sleep 
###  Run it with uv
This project uses `uv` because the creator (me) is an idiot. Despite that it's not really necessarry

To run it, clone this repo, install `uv` (`pkg install uv` on Termux), and then:
```
uv run miapplyenhanced
```
This will automatically install every needed dependency and run the cli.

### Run it without uv
If you're not a big fan of uv (understandable!), you can
```
pip install micommunity datetime ntplib pytz requests
```
manually and then run `./src/miapplyenhanced/cli.py`
