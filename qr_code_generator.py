import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
import io


def create_qr_image(text: str):
    """Generate a QR code PIL image from the given text."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


class QRCodeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.resizable(False, False)
        self.qr_pil_image = None

        # --- Input Frame ---
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Enter text:").pack(anchor=tk.W)
        self.text_entry = tk.Text(input_frame, height=4, width=45)
        self.text_entry.pack(fill=tk.X, pady=(2, 6))

        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Generate QR Code", command=self.generate).pack(
            side=tk.LEFT
        )
        self.save_btn = tk.Button(
            btn_frame, text="Save As…", command=self.save, state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=(8, 0))

        # --- Preview Frame ---
        preview_frame = tk.LabelFrame(root, text="Preview", padx=10, pady=10)
        preview_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH)

        self.preview_label = tk.Label(preview_frame, text="No QR code yet")
        self.preview_label.pack()

    def generate(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty input", "Please enter some text first.")
            return

        self.qr_pil_image = create_qr_image(text)

        # Resize for preview (fit in ~300×300)
        preview = self.qr_pil_image.copy()
        preview = preview.resize((300, 300))
        self.tk_image = ImageTk.PhotoImage(preview)

        self.preview_label.config(image=self.tk_image, text="")
        self.save_btn.config(state=tk.NORMAL)

    def save(self):
        if self.qr_pil_image is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        )
        if path:
            self.qr_pil_image.save(path)
            messagebox.showinfo("Saved", f"QR code saved to {path}")


if __name__ == "__main__":
    root = tk.Tk()
    QRCodeApp(root)
    root.mainloop()
