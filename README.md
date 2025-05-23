## Stuck in the Matrix - Pygame Hackable RPG

> A modifiable, reverse-engineerable Zelda-style RPG sandbox for teaching binary analysis, memory editing, and game hacking.

⚠️ **Alpha Release** — unstable features, experimental modules, and active development. 
---

### About

**Stuck in the Matrix** is a fork and creative transformation of [`pyzelda-rpg`](https://github.com/artemshchirov/pyzelda-rpg), expanded into a hacking-friendly game engine built in Python using Pygame.

This project is designed to be explored with tools like **IDA**, **Cheat Engine**, **x64dbg**, and Python-level reverse engineering.  
Use it to practice:

- Memory patching  
- Debugger-assisted mods  
- Live hex editing  
- Game logic injection  
- Cheat tables and toggles

---

### Features

- Partial Zelda-style game world base: movement, combat, enemies, magic, UI  
- Reverse engineering targets: cheat-protected features, unlockables, conditional logic  
- **Real-time modding** via memory manipulation  
- Educational sandbox for CTFs or classroom binary labs  

---
## Try the Alpha Executable (Windows)

If you just want to **play the game** without installing Python or any dependencies:

1. Download the latest release from the [Releases page](https://github.com/ridpath/stuckinthematrix-base/releases)
3. Double-click `matrix.exe` 
4. Play!
> ⚠️ This is an experimental version — expect bugs and unfinished systems.
> ⚠️ Windows Defender might show a warning since the file is unsigned. Click "More info" → "Run anyway".

---

## Run project locally

```bash
### ⚙️ Setup & Run

```bash
git clone https://github.com/ridpath/stuckinthematrix-base.git
cd stuckinthematrix-base
pip install pygame
python code/main.py
```

![image_2022-11-28_01-22-10](https://user-images.githubusercontent.com/78075439/204165230-b9c48243-f1b8-4906-8088-5a5233865587.png)


## Hackable Toggles (CTF Reverse Engineering)

Find and patch in memory — to change behavior.

Sample toggles include:

god_mode

no_clip

infinite_mana

dash_ability

enemy_spawn_rate

regenerate

mute_music

build_mode

There are 100+ toggles for visuals, gameplay, audio, physics, and AI.

Designed for analysis with: IDA, Cheat Engine, frida, gdb, x64dbg 
---
## 🔍 Educational Uses
🔧 Game hacking 101 (Cheat Engine / memory patching)

RE challenges / CTF warmups

Binary diffing / function discovery

Memory signature scanning

Teaching intro RE in a visual, interactive way


##  Attribution
This project is based on and forked from:

🧩 Original Repository: artemshchirov/pyzelda-rpg
🛠 Created by: Artem Shchirov, based on tutorials by Clear Code
📄 Licensed under MIT

We’ve extended the base game engine into a hacking sandbox, but the core architecture and many sprites remain faithful to the original PyZelda RPG.

## ⚖️ License
This project inherits the original MIT License, with major modifications for reverse engineering use.
If you use this in coursework, demos, or public projects, please include a link to both repositories.
