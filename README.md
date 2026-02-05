# 🚀 Vivo Fiber Router Auto Rebooter

A Python automation tool designed to maintain optimal network performance by periodically rebooting the ISP router. Built using **Selenium**, this tool bypasses complex UI limitations (Frames, Hidden APIs) to execute a clean software reboot.

---

## 🧐 The Problem

ISP-provided routers (specifically **Mitrastar/Askey models used by Vivo Fibra**) are essentially low-power computers running 24/7. Over time, they suffer from:

* **Memory leaks:** RAM fills up, causing sluggishness.
* **NAT table saturation:** Connection tracking fails, causing packet loss.
* **Thermal throttling:** Passive cooling struggles with continuous uptime.

The native firmware often hides or disables the **Scheduled Reboot** feature.

---

## 💡 The Solution

This project creates a custom automation agent that:

* Authenticates securely using local credentials.
* Navigates the router's legacy HTML Frame-based interface.
* Injects JavaScript directly into the browser engine to trigger the internal reboot command, bypassing UI popups and hidden menus.
* Enforces limits: ensures the router is rebooted **only once per day** using a local history file.

---

## 🛠️ Tech Stack

* **Language:** Python 3
* **Core Library:** Selenium WebDriver
* **Driver:** GeckoDriver (Firefox Headless)
* **OS:** Linux (Pop!_OS/Ubuntu) — compatible with Windows/macOS

---

## 📂 Project Structure

```
.
├── auto_reboot_daily.py    # Runs on startup, checks date limit
├── auto_reboot_runtime.py  # Manual force-reboot script
├── config.py               # (Ignored by Git) Contains your secrets
├── config_sample.py        # Template for configuration
├── .gitignore              # Keeps secrets out of Git
└── README.md               # Documentation
```

---

## 🚀 Installation

### 1) Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Vivo-Router-Rebooter.git
cd Vivo-Router-Rebooter
```

### 2) Install dependencies

```bash
pip install selenium webdriver-manager
```

### 3) Configure credentials (OpSec)

Rename the sample file:

```bash
mv config_sample.py config.py
```

Edit `config.py`:

```python
ROUTER_IP = "192.168.15.1"
USERNAME = "admin"
PASSWORD = "your_secure_password"
```

---

## ⚙️ Usage

### **Option 1 — Automatic Daily Maintenance (Recommended)**

Ideal for adding to your OS startup applications:

```bash
python3 auto_reboot_daily.py
```

**Behavior:**
Waits for Wi-Fi → checks `~/.router_last_run` → reboots if needed → updates date.

### **Option 2 — Force Reboot (Manual)**

```bash
python3 auto_reboot_runtime.py
```

---

## 🧠 Technical Highlights (Reverse Engineering)

The router uses nested `<frame>` and `<iframe>` tags, and the reboot button triggers a fragile popup. Instead of automating clicks, the script directly calls the internal API via JavaScript:

```python
reboot_script = """
var data = { restoreFlag: 1, RestartBtn: "RESTART" };
$.post('/cgi-bin/device-management-resets.cgi', data, function(){});
"""
driver.execute_script(reboot_script)
```

This bypasses the UI entirely.

---

## 🛡️ Best Practices Applied

* **Separation of concerns:** Logic vs configuration.
* **Defensive programming:** Smart iframe detection.
* **Clean code:** Modular, readable, minimal dependencies.
* **Operational security:** Passwords never committed to Git.

---

## ⚠️ Disclaimer

This tool is for **educational purposes and personal network maintenance only**.
Use responsibly — I am not r
