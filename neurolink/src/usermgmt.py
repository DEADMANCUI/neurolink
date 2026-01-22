import tkinter as tk
from tkinter import ttk, messagebox
import users


class UserMgmtWindow:
    def __init__(self, parent, manager=None):
        self.parent = parent
        self.manager = manager or users.get_manager()
        self.win = tk.Toplevel(parent)
        self.win.title("用户管理")
        self.win.transient(parent)
        self.win.grab_set()
        self.win.geometry("600x400")

        # Treeview for users
        self.tree = ttk.Treeview(self.win, columns=("role",), show="headings")
        self.tree.heading("role", text="角色")
        self.tree.column("role", width=200)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(fill="x", padx=8, pady=4)

        tk.Button(btn_frame, text="添加", command=self.add_user).pack(side="left", padx=4)
        tk.Button(btn_frame, text="编辑", command=self.edit_user).pack(side="left", padx=4)
        tk.Button(btn_frame, text="删除", command=self.delete_user).pack(side="left", padx=4)
        tk.Button(btn_frame, text="重置密码", command=self.reset_password).pack(side="left", padx=4)
        tk.Button(btn_frame, text="关闭", command=self.close).pack(side="right", padx=4)

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in sorted(self.manager.users.values(), key=lambda x: x.username):
            self.tree.insert("", "end", iid=u.username, values=(u.role,))

    def add_user(self):
        dlg = UserEditDialog(self.win, title="添加用户")
        if not dlg.result:
            return
        username, password, role = dlg.result
        try:
            self.manager.create_user(username, password, role)
            messagebox.showinfo("已添加", f"已添加用户 {username}")
            self.refresh()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def edit_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请选择要编辑的用户")
            return
        uname = sel[0]
        u = self.manager.get_user(uname)
        if not u:
            messagebox.showerror("错误", "找不到用户")
            return
        dlg = UserEditDialog(self.win, title="编辑用户", username=u.username, role=u.role, allow_password=True, editing=True)
        if not dlg.result:
            return
        username, password, role = dlg.result
        try:
            # username editing not supported to avoid key complications
            self.manager.update_role(uname, role)
            if password:
                self.manager.set_password(uname, password)
            messagebox.showinfo("已更新", f"已更新用户 {uname}")
            self.refresh()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请选择要删除的用户")
            return
        uname = sel[0]
        if uname == "admin":
            messagebox.showwarning("禁止", "不能删除默认 admin 用户")
            return
        if not messagebox.askyesno("确认", f"确定要删除用户 {uname} 吗？"):
            return
        try:
            self.manager.delete_user(uname)
            messagebox.showinfo("已删除", f"已删除用户 {uname}")
            self.refresh()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def reset_password(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("提示", "请选择要重置密码的用户")
            return
        uname = sel[0]
        dlg = PasswordDialog(self.win, title=f"为 {uname} 重置密码")
        if not dlg.result:
            return
        newpw = dlg.result
        try:
            self.manager.set_password(uname, newpw)
            messagebox.showinfo("已重置", f"已为 {uname} 重置密码")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def close(self):
        self.win.grab_release()
        self.win.destroy()


class UserEditDialog:
    def __init__(self, parent, title="用户", username="", role=users.ROLE_SOLDIER, allow_password=True, editing=False):
        self.result = None
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.transient(parent)
        self.win.grab_set()

        frm = tk.Frame(self.win)
        frm.pack(padx=8, pady=8)

        tk.Label(frm, text="用户名:").grid(row=0, column=0, sticky="e")
        self.user_ent = tk.Entry(frm)
        self.user_ent.grid(row=0, column=1)
        self.user_ent.insert(0, username)
        if editing:
            self.user_ent.config(state="disabled")

        tk.Label(frm, text="角色:").grid(row=1, column=0, sticky="e")
        self.role_var = tk.StringVar(value=role)
        roles = [users.ROLE_ADMIN, users.ROLE_COMMANDER, users.ROLE_SOLDIER]
        self.role_cb = ttk.Combobox(frm, textvariable=self.role_var, values=roles, state="readonly")
        self.role_cb.grid(row=1, column=1)

        tk.Label(frm, text="密码:").grid(row=2, column=0, sticky="e")
        self.pw_ent = tk.Entry(frm, show="*")
        self.pw_ent.grid(row=2, column=1)

        tk.Label(frm, text="确认密码:").grid(row=3, column=0, sticky="e")
        self.pw2_ent = tk.Entry(frm, show="*")
        self.pw2_ent.grid(row=3, column=1)

        btns = tk.Frame(self.win)
        btns.pack(pady=6)
        tk.Button(btns, text="取消", command=self.cancel).pack(side="right", padx=4)
        tk.Button(btns, text="确定", command=self.ok).pack(side="right", padx=4)

        self.win.bind("<Return>", lambda e: self.ok())
        self.win.bind("<Escape>", lambda e: self.cancel())
        self.user_ent.focus_set()
        parent.wait_window(self.win)

    def ok(self):
        username = self.user_ent.get().strip()
        role = self.role_var.get()
        pw = self.pw_ent.get()
        pw2 = self.pw2_ent.get()
        if not username:
            messagebox.showwarning("提示", "用户名不能为空")
            return
        if pw or pw2:
            if pw != pw2:
                messagebox.showwarning("提示", "两次密码输入不一致")
                return
        self.result = (username, pw, role)
        self.win.destroy()

    def cancel(self):
        self.result = None
        self.win.destroy()


class PasswordDialog:
    def __init__(self, parent, title="密码"):
        self.result = None
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.transient(parent)
        self.win.grab_set()

        frm = tk.Frame(self.win)
        frm.pack(padx=8, pady=8)
        tk.Label(frm, text="新密码:").grid(row=0, column=0, sticky="e")
        self.pw_ent = tk.Entry(frm, show="*")
        self.pw_ent.grid(row=0, column=1)
        tk.Label(frm, text="确认:").grid(row=1, column=0, sticky="e")
        self.pw2_ent = tk.Entry(frm, show="*")
        self.pw2_ent.grid(row=1, column=1)

        btns = tk.Frame(self.win)
        btns.pack(pady=6)
        tk.Button(btns, text="取消", command=self.cancel).pack(side="right", padx=4)
        tk.Button(btns, text="确定", command=self.ok).pack(side="right", padx=4)

        self.win.bind("<Return>", lambda e: self.ok())
        self.win.bind("<Escape>", lambda e: self.cancel())
        self.pw_ent.focus_set()
        parent.wait_window(self.win)

    def ok(self):
        pw = self.pw_ent.get()
        pw2 = self.pw2_ent.get()
        if not pw:
            messagebox.showwarning("提示", "密码不能为空")
            return
        if pw != pw2:
            messagebox.showwarning("提示", "两次密码输入不一致")
            return
        self.result = pw
        self.win.destroy()

    def cancel(self):
        self.result = None
        self.win.destroy()
