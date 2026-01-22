import os
import json
import tkinter as tk
from tkinter import messagebox

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
            # older Pillow may provide ANTIALIAS; if not, fallback to 1
            RESAMPLE = getattr(Image, "ANTIALIAS", 1)


class MapWindow:
    """Embed a simple map view into a parent Tk widget.

    It looks for a map image under `assets/map.png|jpg|jpeg` and a JSON
    config file `map_config.json` next to the package root. The config
    stores a relative position [rx, ry] in 0..1 indicating where to draw
    the location arrow on the map.
    """

    def __init__(self, parent, config_path=None):
        self.parent = parent
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        self.base = base
        if config_path is None:
            config_path = os.path.join(base, "map_config.json")
        self.config_path = config_path

        self.frame = tk.Frame(parent, bg="black")
        self.frame.pack(fill="both", expand=True)

        # load config
        self.rel_pos = [0.5, 0.5]
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                p = data.get("position")
                if isinstance(p, (list, tuple)) and len(p) == 2:
                    self.rel_pos = [float(p[0]), float(p[1])]
        except Exception:
            self.rel_pos = [0.5, 0.5]

        # top toolbar
        tb = tk.Frame(self.frame, bg="#222")
        tb.pack(fill="x")
        tk.Button(tb, text="返回", command=self.close).pack(side="right", padx=6, pady=6)
        tk.Button(tb, text="设置为当前位置(点击地图)", command=self.enable_set_mode).pack(side="right", padx=6, pady=6)

        # canvas for map
        self.canvas = tk.Canvas(self.frame, bg="#333")
        self.canvas.pack(fill="both", expand=True)

        # load image
        self.map_image = None
        self.tk_image = None
        self.map_path = None
        for candidate in ("map.png", "map.jpg", "map.jpeg"):
            p = os.path.join(base, "assets", candidate)
            if os.path.exists(p):
                self.map_path = p
                break

        if self.map_path and PIL_AVAILABLE:
            try:
                self.map_image = Image.open(self.map_path).convert("RGBA")
            except Exception:
                self.map_image = None

        self._resized = None
        self._arrow = None
        self.set_mode = False

        self.parent.update_idletasks()
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)

    def enable_set_mode(self):
        self.set_mode = True
        messagebox.showinfo("提示", "单击地图以设置当前位置。完成后地图会保存配置。")

    def _on_click(self, event):
        if not self.set_mode:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        rx = event.x / float(w) if w else 0.5
        ry = event.y / float(h) if h else 0.5
        self.rel_pos = [max(0.0, min(1.0, rx)), max(0.0, min(1.0, ry))]
        self._draw_overlay()
        # save config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"position": self.rel_pos}, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("已保存", "当前位置已保存到配置。")
        except Exception as e:
            messagebox.showwarning("保存失败", str(e))
        self.set_mode = False

    def _on_resize(self, event):
        # redraw background image to canvas size while preserving aspect
        w = max(1, event.width)
        h = max(1, event.height)
        if self.map_image and PIL_AVAILABLE:
            try:
                ow, oh = self.map_image.size
                # fit into canvas while preserving aspect
                ratio = min(w / ow, h / oh)
                nw = max(1, int(ow * ratio))
                nh = max(1, int(oh * ratio))
                resized = self.map_image.resize((nw, nh), RESAMPLE)
                self.tk_image = ImageTk.PhotoImage(resized)
                self.canvas.delete("_bg")
                # center
                x = (w - nw) // 2
                y = (h - nh) // 2
                self.canvas.create_image(x, y, anchor="nw", image=self.tk_image, tags=("_bg",))
                self._resized = (x, y, nw, nh)
            except Exception:
                self.canvas.delete("_bg")
                self._resized = None
        else:
            # no image: clear and show placeholder text
            self.canvas.delete("_bg")
            self.canvas.create_rectangle(0, 0, w, h, fill="#222", tags=("_bg",))
            self.canvas.create_text(w//2, h//2, text="地图未找到 (assets/map.png) ", fill="white", tags=("_bg",))
            self._resized = (0, 0, w, h)

        self._draw_overlay()

    def _draw_overlay(self):
        # remove previous overlay
        self.canvas.delete("_overlay")
        if not self._resized:
            return
        x0, y0, nw, nh = self._resized
        rx, ry = self.rel_pos
        px = x0 + int(rx * nw)
        py = y0 + int(ry * nh)
        # draw a simple arrow (triangle) pointing up
        size = max(8, int(min(nw, nh) * 0.03))
        points = [px, py - size, px - size//2, py + size, px + size//2, py + size]
        self.canvas.create_polygon(points, fill="red", outline="black", tags=("_overlay",))
        # optional circle
        self.canvas.create_oval(px-3, py-3, px+3, py+3, fill="yellow", outline="black", tags=("_overlay",))

    def close(self):
        # destroy the frame to return to previous UI
        try:
            self.frame.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    mw = MapWindow(root)
    root.mainloop()
