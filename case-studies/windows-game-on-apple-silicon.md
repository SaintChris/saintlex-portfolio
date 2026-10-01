# Running a Windows-only game on Apple Silicon

## Status

Personal project, working on an Apple M1 Mac (16 GB) under macOS 26 and 27. The restore repository is private because it contains save games and account-specific configuration; this case study describes the approach.

## Objective

Play *Electrician Simulator* and its *Smart Devices* DLC, bought on the Epic Games Store and published only for Windows, on an Apple Silicon Mac. Then make the setup reproducible, so a reset Mac can be back to the same save game with one script.

## Constraints

- No Windows machine, virtual machine licence, or paid compatibility layer
- The Epic Games Launcher cannot install games under Wine (error DP-07)
- Apple Silicon runs x86 Windows code only through Rosetta 2 plus Wine
- The DLC is licence-checked online at every launch

## Stack

```text
Electrician Simulator (Windows, Unity, Direct3D 11)
    ↓
legendary (open-source Epic client: login, download, launch)
    ↓
Wine 11 via Whisky 3.7.0 (maintained fork)
    ↓
DXMT (Direct3D 11 → Metal)       GStreamer 1.26.11 (video decoding)
    ↓
Rosetta 2 → Apple M1
```

## Failures and how each was isolated

Each symptom was traced to one layer before anything was changed.

| Symptom | Evidence | Cause | Fix |
|---|---|---|---|
| Crash on start | Game log reported an `NVIDIA GeForce 6800` adapter | Wine fell back to its OpenGL renderer because the bottle lacked the Metal translation DLLs | Copy the DXMT DLLs into the bottle's `system32` and `syswow64` |
| Black screen | `WindowsVideoMedia error 0xc00d36bb` | The Homebrew GStreamer build needs a newer FFmpeg than Wine links against | Install the official GStreamer 1.26.11 framework instead |
| Stuck at title screen, DLC not owned | `InvalidUser` in the log | The Epic overlay process failed under Wine and broke the online session | Disable the overlay through `WINEDLLOVERRIDES` |
| Hangs on the first-run warning screen | Memory stayed near 0.2 GB; video calls climbed in the log | The intro waits for a video that the Metal layer cannot share | Clear the game's first-run registry flag before every launch |
| `bad CPU type in executable` after an OS upgrade | Nothing launched at all | The macOS 26 → 27 upgrade removed Rosetta 2 | Reinstall Rosetta; the restore script now checks for it first |
| Zero games listed | `IndexError` from the client | The Epic client defaults to Mac or CrossOver builds | Always pass `--platform Windows` and explicit Wine paths |

A healthy launch was defined from evidence too: the log shows a successful login, an ownership check returning true, and the base game and DLC asset bundles preloading, at about 0.5 GB of memory.

## Making it reproducible

The fix became a private repository with:

- `restore.sh`, a nine-step script that is safe to re-run. Each step checks whether it is already done, covering Rosetta, Whisky, GStreamer (size-checked download), the Wine bottle, the DXMT DLLs, the Epic client and its configuration, the download, save restore, and a small macOS launcher app.
- `backup-saves.sh`, which copies save slots and exports in-game settings from the Wine registry into the repository.
- A troubleshooting guide that records every failure above with its symptom and fix.

The script pauses only for the three things a person must do: finish Whisky's first-run download, enter the administrator password, and log in to Epic.

## Known limitation

Intro videos and cutscenes still do not display, because the Metal translation layer does not implement a shared-texture call the video player needs. Everything else works online, including achievements and the DLC.

## What I would do differently

Write the requirements list first. I lost most of the time to a loop: fix one failure, relaunch, hit the next one. The dependencies were knowable up front. CPU translation, graphics, video codecs, licensing, first-run state. Listing them on day one would have saved hours.
