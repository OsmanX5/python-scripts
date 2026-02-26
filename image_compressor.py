import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


def find_images(folder: str) -> list[str]:
    """Return a sorted list of image file paths in the given folder."""
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith(IMAGE_EXTENSIONS):
            files.append(os.path.join(folder, name))
    files.sort(key=lambda p: os.path.getsize(p), reverse=True)
    return files


def human_size(size_bytes: int) -> str:
    """Format byte count as a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class ImageCompressorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Compressor")
        self.root.geometry("750x520")
        self.root.resizable(True, True)

        self.folder = ""
        self.image_paths: list[str] = []

        self._build_ui()
        self._select_folder()

    # ── UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self.root, padx=8, pady=6)
        top.pack(fill=tk.X)

        tk.Label(top, text="Folder:").pack(side=tk.LEFT)
        self.folder_var = tk.StringVar(value="(none)")
        tk.Label(top, textvariable=self.folder_var, anchor=tk.W, fg="blue").pack(
            side=tk.LEFT, padx=(4, 10), fill=tk.X, expand=True
        )
        tk.Button(top, text="Browse…", command=self._select_folder).pack(side=tk.RIGHT)

        # Image list (Treeview)
        cols = ("name", "dimensions", "size")
        list_frame = tk.Frame(self.root, padx=8)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            list_frame, columns=cols, show="headings", selectmode="extended"
        )
        self.tree.heading("name", text="File Name")
        self.tree.heading("dimensions", text="Dimensions")
        self.tree.heading("size", text="File Size")
        self.tree.column("name", width=340, stretch=True)
        self.tree.column("dimensions", width=140, anchor=tk.CENTER)
        self.tree.column("size", width=100, anchor=tk.E)

        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Options frame
        opts = tk.LabelFrame(self.root, text="Options", padx=10, pady=8)
        opts.pack(fill=tk.X, padx=8, pady=(6, 4))

        # Scale factor
        tk.Label(opts, text="Scale:").grid(row=0, column=0, sticky=tk.W)
        self.scale_var = tk.StringVar(value="0.5")
        ttk.Radiobutton(opts, text="× 0.5", variable=self.scale_var, value="0.5").grid(
            row=0, column=1, padx=(4, 10)
        )
        ttk.Radiobutton(
            opts, text="× 0.25", variable=self.scale_var, value="0.25"
        ).grid(row=0, column=2, padx=(0, 20))

        # Output format
        tk.Label(opts, text="Format:").grid(row=0, column=3, sticky=tk.W)
        self.format_var = tk.StringVar(value="jpg")
        ttk.Radiobutton(
            opts, text="Convert to JPG", variable=self.format_var, value="jpg"
        ).grid(row=0, column=4, padx=(4, 10))
        ttk.Radiobutton(
            opts, text="Keep original format", variable=self.format_var, value="keep"
        ).grid(row=0, column=5)

        # JPG quality
        tk.Label(opts, text="JPG Quality:").grid(row=1, column=0, sticky=tk.W, pady=(6, 0))
        self.quality_var = tk.IntVar(value=85)
        quality_spin = ttk.Spinbox(
            opts, from_=10, to=100, textvariable=self.quality_var, width=5
        )
        quality_spin.grid(row=1, column=1, sticky=tk.W, padx=(4, 0), pady=(6, 0))

        # Replace originals checkbox
        self.replace_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opts, text="Replace original files", variable=self.replace_var
        ).grid(row=1, column=3, columnspan=3, sticky=tk.W, pady=(6, 0))

        # Buttons
        btn_frame = tk.Frame(self.root, padx=8, pady=8)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Select All", command=self._select_all).pack(
            side=tk.LEFT
        )
        tk.Button(btn_frame, text="Deselect All", command=self._deselect_all).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        tk.Button(
            btn_frame,
            text="Compress Selected",
            bg="#4CAF50",
            fg="white",
            command=self._compress,
        ).pack(side=tk.RIGHT)

        # Status bar
        self.status_var = tk.StringVar(value="Select a folder to begin.")
        tk.Label(
            self.root, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN
        ).pack(fill=tk.X, side=tk.BOTTOM)

    # ── Actions ───────────────────────────────────────────────────────

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if not folder:
            return
        self.folder = folder
        self.folder_var.set(folder)
        self._load_images()

    def _load_images(self):
        self.tree.delete(*self.tree.get_children())
        self.image_paths = find_images(self.folder)

        for path in self.image_paths:
            name = os.path.basename(path)
            size = human_size(os.path.getsize(path))
            try:
                with Image.open(path) as img:
                    dims = f"{img.width} × {img.height}"
            except Exception:
                dims = "?"
            self.tree.insert("", tk.END, iid=path, values=(name, dims, size))

        count = len(self.image_paths)
        self.status_var.set(f"{count} image(s) found in folder.")

    def _select_all(self):
        self.tree.selection_set(self.tree.get_children())

    def _deselect_all(self):
        self.tree.selection_remove(self.tree.get_children())

    def _compress(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select at least one image first.")
            return

        scale = float(self.scale_var.get())
        to_jpg = self.format_var.get() == "jpg"
        quality = self.quality_var.get()
        replace = self.replace_var.get()

        if replace:
            confirm = messagebox.askyesno(
                "Confirm Replace",
                "This will overwrite the selected original images.\n"
                "This action cannot be undone. Continue?",
            )
            if not confirm:
                return
            out_dir = self.folder
        else:
            out_dir = os.path.join(self.folder, "compressed")
            os.makedirs(out_dir, exist_ok=True)

        success = 0
        errors = []

        for path in selected:
            try:
                with Image.open(path) as img:
                    new_w = max(1, int(img.width * scale))
                    new_h = max(1, int(img.height * scale))
                    resized = img.resize((new_w, new_h), Image.LANCZOS)

                    base = os.path.splitext(os.path.basename(path))[0]

                    if to_jpg:
                        out_path = os.path.join(out_dir, base + ".jpg")
                        if resized.mode in ("RGBA", "P"):
                            resized = resized.convert("RGB")
                        resized.save(out_path, "JPEG", quality=quality)
                        # Remove original if format changed and replacing in place
                        if replace and out_path != path:
                            os.remove(path)
                    else:
                        ext = os.path.splitext(path)[1].lower()
                        out_path = os.path.join(out_dir, base + ext)
                        save_kwargs = {}
                        if ext in (".jpg", ".jpeg"):
                            save_kwargs["quality"] = quality
                        if resized.mode == "RGBA" and ext in (".jpg", ".jpeg"):
                            resized = resized.convert("RGB")
                        resized.save(out_path, **save_kwargs)

                    success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        if replace:
            dest_label = "original location (replaced)"
        else:
            dest_label = out_dir
        msg = f"Compressed {success}/{len(selected)} image(s).\nSaved to: {dest_label}"
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors)

        status_text = (
            f"Done – {success} image(s) replaced in place"
            if replace
            else f"Done – {success} image(s) saved to /compressed"
        )
        self.status_var.set(status_text)
        messagebox.showinfo("Done", msg)

        if replace:
            self._load_images()


if __name__ == "__main__":
    root = tk.Tk()
    ImageCompressorApp(root)
    root.mainloop()
