import os
import sys
import argparse
import tkinter as tk
from tkinter import font, messagebox

# ensure project root is importable so we can import users.py
base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base not in sys.path:
    sys.path.insert(0, base)
import users
import usermgmt
import mapview
import shutil
import subprocess
import threading
import time
import signal

# Optional Pillow support for JPEG/other formats
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

if PIL_AVAILABLE:
    try:
        RESAMPLE = Image.Resampling.LANCZOS
    except Exception:
        try:
            RESAMPLE = Image.LANCZOS
        except Exception:
            RESAMPLE = getattr(Image, "ANTIALIAS", 1)


def read_version():
    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(base, "VERSION"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"






class LoginApp:
    def __init__(self, root, touch_mode: bool = False):
        self.root = root
        self.root.title("neurolink")
        self.root.configure(bg="black")
        self.touch_mode = bool(touch_mode)

        # Always run fullscreen (user requested full-screen operation)
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            pass

        # Windowed mode slightly smaller than full screen (90%) and centered
        try:
            ws = self.root.winfo_screenwidth()
            hs = self.root.winfo_screenheight()
            # scale factor for fonts/widgets (allow making UI smaller on small screens)
            self._scale_factor = 1.0
            # If the attached display is the 800x480 LCD, prefer fullscreen and slightly reduce scale
            if ws == 800 and hs == 480:
                try:
                    self.root.attributes("-fullscreen", True)
                except Exception:
                    try:
                        self.root.geometry("800x480+0+0")
                    except Exception:
                        pass
                try:
                    self.root.resizable(False, False)
                except Exception:
                    pass
                # make UI a bit smaller to better fit limited pixels
                self._scale_factor = 0.85
            else:
                win_w = max(800, int(ws * 0.9))
                win_h = max(480, int(hs * 0.9))
                x = (ws - win_w) // 2
                y = (hs - win_h) // 2
                try:
                    self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
                except Exception:
                    # fallback to a reasonable window size
                    self.root.geometry(f"{max(800, ws-10)}x{max(480, hs-10)}+{x}+{y}")
        except Exception:
            try:
                self.root.geometry("800x480")
            except Exception:
                pass
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.version = read_version()

        # Create container for stacked layout (logo -> version -> login)
        # place near the center but slightly above center
        self.container = tk.Frame(self.root, bg="black")
        self.container.place(relx=0.5, rely=0.45, anchor="center")

        # Version label (white) as child of container
        ver_font = font.Font(size=14)
        self.ver_label = tk.Label(
            self.container,
            text=f"Version {self.version}",
            fg="white",
            bg="black",
            font=ver_font,
        )

        # Attempt to load logo image (kept in assets/logo.jpeg).
        # We'll keep the original PIL image in `self.logo_raw` and
        # perform resizing after the login entry is created so the
        # logo width can match the input width.
        self.logo_raw = None
        self.logo_img = None
        logo_path = None
        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            # prefer PNG if present, fall back to JPEG/JPG
            logo_path = None
            for candidate in ("logo.png", "logo.jpeg", "logo.jpg"):
                p = os.path.join(base, "assets", candidate)
                if os.path.exists(p):
                    logo_path = p
                    break
            if logo_path:
                if PIL_AVAILABLE:
                    try:
                        self.logo_raw = Image.open(logo_path).convert("RGBA")
                    except Exception:
                        self.logo_raw = None
                else:
                    try:
                        self.logo_img = tk.PhotoImage(file=logo_path)
                    except Exception:
                        self.logo_img = None
            else:
                self.logo_raw = None
        except Exception:
            self.logo_raw = None

        # Center frame for login (as child of container)
        self.frame = tk.Frame(self.container, bg="black")
        self.frame.grid(row=2, column=0)

        # fonts: increase sizes in touch mode, but respect scale factor
        scale = getattr(self, '_scale_factor', 1.0)
        if getattr(self, "touch_mode", False):
            label_font = font.Font(size=max(12, int(round(26 * scale))))
            entry_font = font.Font(size=max(10, int(round(22 * scale))))
            btn_font = font.Font(size=max(12, int(round(24 * scale))))
        else:
            # default smaller sizes to fit 800x480 better
            label_font = font.Font(size=max(10, int(round(16 * scale))))
            entry_font = font.Font(size=max(9, int(round(14 * scale))))
            btn_font = font.Font(size=max(10, int(round(16 * scale))))

        tk.Label(self.frame, text="用户名", fg="white", bg="black", font=label_font).grid(row=0, column=0, pady=8, sticky="e")
        self.username = tk.Entry(self.frame, font=entry_font, width=20)
        self.username.grid(row=0, column=1, pady=8, padx=10)

        tk.Label(self.frame, text="密码", fg="white", bg="black", font=label_font).grid(row=1, column=0, pady=8, sticky="e")
        self.password = tk.Entry(self.frame, font=entry_font, show="*", width=20)
        self.password.grid(row=1, column=1, pady=8, padx=10)

        # touch-friendly button size when enabled
        if getattr(self, "touch_mode", False):
            self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=btn_font, height=2, width=14)
        else:
            self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=btn_font)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=16)

        self.username.focus_set()
        self.root.bind("<Return>", lambda e: self.submit())

        # Virtual keyboard support: prefer system on-screen keyboard and start on click
        self._kb_proc = None
        self._kb_cmd = None
        self._kb_started_by_us = False
        self._started_at = time.time()
        self._last_kb_widget = None
        self._last_kb_start_time = 0.0
        # no internal fallback keyboard; use system keyboard only
        self._internal_kb = None
        try:
            # prefer onboard (GTK), then matchbox-keyboard (X), then squeekboard
            if shutil.which("onboard"):
                self._kb_cmd = ["onboard"]
            elif shutil.which("matchbox-keyboard"):
                self._kb_cmd = ["matchbox-keyboard"]
            elif shutil.which("squeekboard"):
                self._kb_cmd = ["squeekboard"]
            else:
                self._kb_cmd = None
        except Exception:
            self._kb_cmd = None

        # always bind clicks to attempt launching the system keyboard
        try:
            self.username.bind("<Button-1>", lambda e: self._on_field_click(e.widget))
            self.password.bind("<Button-1>", lambda e: self._on_field_click(e.widget))
            self.username.bind("<FocusOut>", lambda e: self._on_field_focus_out(e.widget))
            self.password.bind("<FocusOut>", lambda e: self._on_field_focus_out(e.widget))
        except Exception:
            pass

        # Now that entries exist and have requested sizes, resize logo to
        # match the username entry width and place it above the version.
        self.root.update_idletasks()
        try:
            target_w = self.username.winfo_width()
        except Exception:
            target_w = 0
        if not target_w or target_w < 50:
            try:
                ws = self.root.winfo_width() or self.root.winfo_screenwidth()
                target_w = int(ws * 0.4)
            except Exception:
                target_w = 300

        if self.logo_raw:
            try:
                ow, oh = self.logo_raw.size
                ratio = target_w / float(ow)
                new_h = max(20, int(oh * ratio))
                resized = self.logo_raw.resize((target_w, new_h), RESAMPLE)
                self.logo_img = ImageTk.PhotoImage(resized)
                self.logo_label = tk.Label(self.container, image=self.logo_img, bg="black")
                # logo tightly above version
                self.logo_label.grid(row=0, column=0, pady=(0, 2))
                self.ver_label.grid(row=1, column=0, pady=(0, 2))
                print(f"LOGO: loaded and resized to {target_w}x{new_h} from {logo_path}")
            except Exception as e:
                self.logo_label = None
                print("LOGO: failed to create image", e)
        elif self.logo_img:
            try:
                # If PIL wasn't available and we only have a Tk PhotoImage,
                # try to subsample it to approximate the target width.
                try:
                    cur_w = self.logo_img.width()
                except Exception:
                    cur_w = None
                if cur_w and target_w and cur_w > target_w:
                    try:
                        import math
                        factor = max(1, math.ceil(cur_w / float(target_w)))
                        if factor > 1:
                            self.logo_img = self.logo_img.subsample(factor, factor)
                    except Exception:
                        pass
                self.logo_label = tk.Label(self.container, image=self.logo_img, bg="black")
                self.logo_label.grid(row=0, column=0, pady=(0, 2))
                self.ver_label.grid(row=1, column=0, pady=(0, 2))
                print(f"LOGO: loaded PhotoImage from {logo_path} (cur_w={cur_w}, target_w={target_w})")
            except Exception:
                self.logo_label = None
                print("LOGO: PhotoImage exists but failed to place")
        else:
            self.logo_label = None
            self.ver_label.grid(row=1, column=0, pady=(0, 8))
            print(f"LOGO: not found at {logo_path} or failed to load")


        # second set (recreate fonts if needed) — keep same scale logic
        scale = getattr(self, '_scale_factor', 1.0)
        if getattr(self, "touch_mode", False):
            label_font = font.Font(size=max(12, int(round(26 * scale))))
            entry_font = font.Font(size=max(10, int(round(22 * scale))))
            btn_font = font.Font(size=max(12, int(round(24 * scale))))
        else:
            label_font = font.Font(size=max(10, int(round(16 * scale))))
            entry_font = font.Font(size=max(9, int(round(14 * scale))))
            btn_font = font.Font(size=max(10, int(round(16 * scale))))

        tk.Label(self.frame, text="用户名", fg="white", bg="black", font=label_font).grid(row=0, column=0, pady=8, sticky="e")
        self.username = tk.Entry(self.frame, font=entry_font, width=20)
        self.username.grid(row=0, column=1, pady=8, padx=10)

        tk.Label(self.frame, text="密码", fg="white", bg="black", font=label_font).grid(row=1, column=0, pady=8, sticky="e")
        self.password = tk.Entry(self.frame, font=entry_font, show="*", width=20)
        self.password.grid(row=1, column=1, pady=8, padx=10)

        if getattr(self, "touch_mode", False):
            self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=btn_font, height=2, width=14)
        else:
            self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=btn_font)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=16)

        self.username.focus_set()
        self.root.bind("<Return>", lambda e: self.submit())

        # Ensure event bindings are attached to the (possibly recreated) entry widgets
        if self._kb_cmd:
            try:
                self.username.bind("<Button-1>", lambda e: self._on_field_click(e.widget))
                self.password.bind("<Button-1>", lambda e: self._on_field_click(e.widget))
                self.username.bind("<FocusOut>", lambda e: self._on_field_focus_out(e.widget))
                self.password.bind("<FocusOut>", lambda e: self._on_field_focus_out(e.widget))
            except Exception:
                pass

    def submit(self):
        user = self.username.get().strip()
        pwd = self.password.get()
        if not user:
            messagebox.showwarning("提示", "请输入用户名")
            return
        mgr = users.get_manager()
        u = mgr.authenticate(user, pwd)
        if not u:
            messagebox.showerror("登录失败", "用户名或密码错误")
            return
        # On success, open the configured map view (replace login UI)
        try:
            role_name = u.role
            perms = users.PERMISSIONS.get(role_name, set())
            # hide login container and embed the map view
            try:
                self.container.place_forget()
            except Exception:
                pass
            self.mapwin = mapview.MapWindow(self.root, touch_mode=getattr(self, "touch_mode", False))
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _start_virtual_keyboard(self):
        try:
            # if we already have a running process, verify it's alive
            if getattr(self, "_kb_proc", None) is not None:
                try:
                    if self._kb_proc.poll() is None:
                        return
                except Exception:
                    return
            if not getattr(self, "_kb_cmd", None):
                return
            env = dict(**os.environ)
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            env["XAUTHORITY"] = env.get("XAUTHORITY", "/home/patrickcui/.Xauthority")
            # resolve path
            kb_path = None
            try:
                kb_path = shutil.which(self._kb_cmd[0]) if isinstance(self._kb_cmd, (list, tuple)) and self._kb_cmd else None
            except Exception:
                kb_path = None
            cmd = self._kb_cmd if not kb_path else [kb_path] + (self._kb_cmd[1:] if len(self._kb_cmd) > 1 else [])
            # avoid starting duplicate keyboard processes: check for existing processes
            try:
                existing = []
                proc_name = (self._kb_cmd[0] if isinstance(self._kb_cmd, (list, tuple)) else str(self._kb_cmd))
                if shutil.which("pgrep"):
                    try:
                        out = subprocess.check_output(["pgrep", "-f", proc_name])
                        existing = out.split()
                    except subprocess.CalledProcessError:
                        existing = []
                    except Exception:
                        existing = []
                else:
                    # fallback to ps -ef and text search
                    try:
                        out = subprocess.check_output(["ps", "-eo", "pid,cmd"]).decode(errors="ignore")
                        for ln in out.splitlines():
                            if proc_name in ln and 'pgrep' not in ln:
                                parts = ln.strip().split(None, 1)
                                if parts:
                                    existing.append(parts[0].encode())
                    except Exception:
                        existing = []
                if existing:
                    try:
                        if logf:
                            logf.write(f"KB: existing process(es) detected for {proc_name}, skipping spawn: {existing}\n")
                    except Exception:
                        pass
                    # don't spawn a new one if one is already present
                    self._kb_proc = None
                    self._kb_started_by_us = False
                    return
            except Exception:
                pass
            try:
                logf = open(os.path.join(base, "run.log"), "a", encoding="utf-8")
            except Exception:
                logf = None
            try:
                self._kb_proc = subprocess.Popen(cmd, env=env, preexec_fn=os.setsid, stdout=(logf or subprocess.DEVNULL), stderr=(logf or subprocess.DEVNULL))
                self._kb_started_by_us = True
                try:
                    self._last_kb_start_time = time.time()
                    if logf:
                        logf.write(f"KB: started {cmd} pid={self._kb_proc.pid}\n")
                except Exception:
                    pass
            except Exception as e:
                try:
                    if logf:
                        logf.write(f"KB: failed to start {cmd}: {e}\n")
                except Exception:
                    pass
        except Exception:
            pass

    def _stop_virtual_keyboard(self):
        try:
            if getattr(self, "_kb_proc", None):
                try:
                    pid = self._kb_proc.pid
                    if self._kb_started_by_us:
                        try:
                            os.killpg(os.getpgid(pid), signal.SIGTERM)
                        except Exception:
                            try:
                                os.kill(pid, signal.SIGTERM)
                            except Exception:
                                pass
                    else:
                        try:
                            self._kb_proc.terminate()
                        except Exception:
                            pass
                    try:
                        self._kb_proc.wait(timeout=1.0)
                    except Exception:
                        try:
                            if self._kb_started_by_us:
                                os.killpg(os.getpgid(pid), signal.SIGKILL)
                            else:
                                self._kb_proc.kill()
                        except Exception:
                            pass
                except Exception:
                    pass
                finally:
                    self._kb_proc = None
                    self._kb_started_by_us = False
            else:
                # fallback: try pkill to stop common keyboards
                try:
                    if shutil.which("pkill"):
                        subprocess.call(["pkill", "-f", "matchbox-keyboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
        except Exception:
            pass
        # hide internal keyboard as well
        # no internal keyboard to hide

    def _on_field_focus_out(self, widget):
        try:
            # small delay to avoid flicker when switching fields; increase delay
            # so clicks that move focus to the keyboard won't immediately close it
            self.root.after(600, lambda: self._stop_virtual_keyboard())
        except Exception:
            pass

    def _on_field_click(self, widget):
        try:
            # if keyboard command not set, try detect again
            if not getattr(self, "_kb_cmd", None):
                try:
                    if shutil.which("squeekboard"):
                        self._kb_cmd = ["squeekboard"]
                    elif shutil.which("matchbox-keyboard"):
                        self._kb_cmd = ["matchbox-keyboard"]
                    elif shutil.which("onboard"):
                        self._kb_cmd = ["onboard"]
                except Exception:
                    pass
            # remember which widget triggered the keyboard so positioning can use it
            try:
                self._last_kb_widget = widget
            except Exception:
                self._last_kb_widget = None

            # debounce rapid clicks: avoid restarting within 1s
            try:
                if getattr(self, "_kb_proc", None) is not None and getattr(self._kb_proc, "poll", lambda: 1)() is None:
                    # already running
                    pass
                else:
                    # prevent rapid restarts
                    if time.time() - getattr(self, "_last_kb_start_time", 0.0) < 1.0:
                        pass
                    else:
                        self._start_virtual_keyboard()
            except Exception:
                # best-effort start
                try:
                    self._start_virtual_keyboard()
                except Exception:
                    pass

            try:
                # position keyboard after a short delay to allow window to appear
                self.root.after(300, lambda: threading.Thread(target=self._position_virtual_keyboard, args=(self._last_kb_widget,), daemon=True).start())
            except Exception:
                threading.Thread(target=self._position_virtual_keyboard, args=(self._last_kb_widget,), daemon=True).start()

            # do not use internal keyboard fallback; rely on system keyboard only
        except Exception:
            pass

    def _position_virtual_keyboard(self, widget=None):
        try:
            if not getattr(self, "_kb_cmd", None):
                return
            # allow being called without widget (use last clicked or focused widget)
            if widget is None:
                widget = getattr(self, "_last_kb_widget", None) or self.root.focus_get()
            if widget is None:
                return
            if not shutil.which("xdotool"):
                return
            patterns = [b"onboard", b"Onboard", b"matchbox-keyboard", b"Matchbox", b"squeekboard", b"Squeekboard"]
            for attempt in range(10):
                try:
                    wx = widget.winfo_rootx()
                    wy = widget.winfo_rooty()
                    wh = widget.winfo_height()
                    sx = self.root.winfo_screenwidth()
                    sy = self.root.winfo_screenheight()
                except Exception:
                    return
                for p in patterns:
                    try:
                        out = subprocess.check_output(["xdotool", "search", "--name", p.decode()])
                        ids = out.split()
                    except subprocess.CalledProcessError:
                        ids = []
                    except Exception:
                        ids = []
                    if ids:
                        k_h = None
                        for wid in ids:
                            try:
                                geom = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", wid.decode()])
                                lines = geom.decode().splitlines()
                                kv = {}
                                for ln in lines:
                                    if '=' in ln:
                                        k, v = ln.split('=',1)
                                        try:
                                            kv[k.strip()] = int(v)
                                        except Exception:
                                            pass
                                if 'HEIGHT' in kv:
                                    k_h = kv['HEIGHT']
                                    break
                            except Exception:
                                k_h = None
                        margin = 6
                        if k_h:
                            # space available below the widget
                            space_below = sy - (wy + wh)
                            if space_below >= k_h + margin:
                                # place directly below the widget
                                ty = wy + wh + margin
                            else:
                                # not enough space below; prefer bottom-align the keyboard
                                ty = max(0, sy - k_h - margin)
                                # if bottom align would overlap the widget, try above the widget
                                if ty <= wy and wy - k_h - margin >= 0:
                                    ty = max(0, wy - k_h - margin)
                        else:
                            # unknown keyboard height: prefer bottom area but try below widget first
                            preferred_ty = wy + wh + margin
                            if preferred_ty <= sy - 80:
                                ty = preferred_ty
                            else:
                                ty = max(0, sy - 200)
                        tx = max(0, wx)
                        for wid in ids:
                            try:
                                subprocess.call(["xdotool", "windowmove", wid.decode(), str(tx), str(ty)])
                            except Exception:
                                pass
                        return
                time.sleep(0.25)
        except Exception:
            pass

    def open_usermgmt(self):
        # Prompt for admin credentials before opening management UI
        auth = AdminAuthDialog(self.root)
        if not auth.result:
            return
        user, pwd = auth.result
        mgr = users.get_manager()
        u = mgr.authenticate(user, pwd)
        if not u or u.role != users.ROLE_ADMIN:
            messagebox.showerror("认证失败", "需要系统管理员权限")
            return
        # Open management window
        usermgmt.UserMgmtWindow(self.root, manager=mgr)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--touch", action="store_true", help="enable touch-friendly UI (fullscreen, larger controls)")
    args, _ = parser.parse_known_args()

    root = tk.Tk()
    app = LoginApp(root, touch_mode=bool(args.touch))
    # add a small management button under the stacked container
    try:
        mgmt_btn = tk.Button(app.container, text="用户管理", command=app.open_usermgmt)
        mgmt_btn.grid(row=3, column=0, pady=(8, 2))
    except Exception:
        pass
    root.mainloop()


class AdminAuthDialog:
    def __init__(self, parent):
        self.result = None
        self.win = tk.Toplevel(parent)
        self.win.title("管理员认证")
        self.win.transient(parent)
        self.win.grab_set()

        frm = tk.Frame(self.win)
        frm.pack(padx=8, pady=8)
        tk.Label(frm, text="管理员用户名:").grid(row=0, column=0, sticky="e")
        self.user_ent = tk.Entry(frm)
        self.user_ent.grid(row=0, column=1)
        tk.Label(frm, text="密码:").grid(row=1, column=0, sticky="e")
        self.pw_ent = tk.Entry(frm, show="*")
        self.pw_ent.grid(row=1, column=1)

        btns = tk.Frame(self.win)
        btns.pack(pady=6)
        tk.Button(btns, text="取消", command=self.cancel).pack(side="right", padx=4)
        tk.Button(btns, text="确定", command=self.ok).pack(side="right", padx=4)

        self.win.bind("<Return>", lambda e: self.ok())
        self.win.bind("<Escape>", lambda e: self.cancel())
        self.user_ent.focus_set()
        parent.wait_window(self.win)

    def ok(self):
        user = self.user_ent.get().strip()
        pw = self.pw_ent.get()
        if not user or not pw:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        self.result = (user, pw)
        self.win.destroy()

    def cancel(self):
        self.result = None
        self.win.destroy()


if __name__ == "__main__":
    main()
