import os
import sys
import tkinter as tk
from tkinter import font, messagebox

# ensure project root is importable so we can import users.py
base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if base not in sys.path:
    sys.path.insert(0, base)
import users
import usermgmt
import mapview

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
    def __init__(self, root):
        self.root = root
        self.root.title("neurolink")
        self.root.configure(bg="black")

        # Windowed mode slightly smaller than full screen (90%) and centered
        try:
            ws = self.root.winfo_screenwidth()
            hs = self.root.winfo_screenheight()
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

        label_font = font.Font(size=18)
        entry_font = font.Font(size=16)

        tk.Label(self.frame, text="用户名", fg="white", bg="black", font=label_font).grid(row=0, column=0, pady=8, sticky="e")
        self.username = tk.Entry(self.frame, font=entry_font, width=20)
        self.username.grid(row=0, column=1, pady=8, padx=10)

        tk.Label(self.frame, text="密码", fg="white", bg="black", font=label_font).grid(row=1, column=0, pady=8, sticky="e")
        self.password = tk.Entry(self.frame, font=entry_font, show="*", width=20)
        self.password.grid(row=1, column=1, pady=8, padx=10)

        self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=label_font)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=16)

        self.username.focus_set()
        self.root.bind("<Return>", lambda e: self.submit())

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

        label_font = font.Font(size=18)
        entry_font = font.Font(size=16)

        tk.Label(self.frame, text="用户名", fg="white", bg="black", font=label_font).grid(row=0, column=0, pady=8, sticky="e")
        self.username = tk.Entry(self.frame, font=entry_font, width=20)
        self.username.grid(row=0, column=1, pady=8, padx=10)

        tk.Label(self.frame, text="密码", fg="white", bg="black", font=label_font).grid(row=1, column=0, pady=8, sticky="e")
        self.password = tk.Entry(self.frame, font=entry_font, show="*", width=20)
        self.password.grid(row=1, column=1, pady=8, padx=10)

        self.login_btn = tk.Button(self.frame, text="登录", command=self.submit, font=label_font)
        self.login_btn.grid(row=2, column=0, columnspan=2, pady=16)

        self.username.focus_set()
        self.root.bind("<Return>", lambda e: self.submit())

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
            self.mapwin = mapview.MapWindow(self.root)
        except Exception as e:
            messagebox.showerror("错误", str(e))

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
    root = tk.Tk()
    app = LoginApp(root)
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
