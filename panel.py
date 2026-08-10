import tkinter as tk
from PIL import Image, ImageTk
import json
from pathlib import Path

import config




class InspectionPanel:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title(config.PANEL_TITLE)
        self.root.geometry(f"{config.PANEL_WIDTH}x{config.PANEL_HEIGHT}")
        self.root.configure(bg=config.PANEL_BG)

        self.root.resizable(False, False)

        # Prevent the panel from blocking the main program.
        self.root.protocol("WM_DELETE_WINDOW", self.hide)

        # ==========================================
        # Header
        # ==========================================

        self.header = tk.Label(
            self.root,
            text=config.PANEL_TITLE,
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            font=("Arial", 20, "bold")
        )

        self.header.pack(
            pady=(15, 10)
        )

        # ==========================================
        # Printer status
        # ==========================================

        self.status_label = tk.Label(
            self.root,
            text="Printer: Unknown",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            font=("Arial", 13, "bold"),
            anchor="w"
        )

        self.status_label.pack(
            fill="x",
            padx=20,
            pady=3
        )

        self.metadata_label = tk.Label(
            self.root,
            text="Metadata: Waiting...",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            font=("Consolas", 10),
            justify="left",
            anchor="w"
        )

        self.metadata_label.pack(
            fill="x",
            padx=20,
            pady=3
        )

        # ==========================================
        # Latest JSON
        # ==========================================

        json_title = tk.Label(
            self.root,
            text="Latest Inspection JSON",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            font=("Arial", 12, "bold")
        )

        json_title.pack(
            anchor="w",
            padx=20,
            pady=(10, 3)
        )

        self.json_text = tk.Text(
            self.root,
            height=10,
            width=90,
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            insertbackground=config.PANEL_TEXT,
            font=("Consolas", 9),
            relief="flat",
            highlightthickness=1,
            highlightbackground=config.PANEL_TEXT
        )

        self.json_text.pack(
            padx=20,
            fill="x"
        )

        # ==========================================
        # Images
        # ==========================================

        image_title = tk.Label(
            self.root,
            text="Latest Inspection",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT,
            font=("Arial", 12, "bold")
        )

        image_title.pack(
            anchor="w",
            padx=20,
            pady=(10, 3)
        )

        self.image_frame = tk.Frame(
            self.root,
            bg=config.PANEL_BG
        )

        self.image_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.render_label = tk.Label(
            self.image_frame,
            text="Render",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT
        )

        self.render_label.pack(
            side="left",
            expand=True
        )

        self.camera_label = tk.Label(
            self.image_frame,
            text="Camera",
            bg=config.PANEL_BG,
            fg=config.PANEL_TEXT
        )

        self.camera_label.pack(
            side="right",
            expand=True
        )

        self.render_photo = None
        self.camera_photo = None

        # Initial display.
        self.root.update_idletasks()

    # ==========================================
    # Update printer state
    # ==========================================

    def update_printer(
        self,
        state
    ):

        status = state.get(
            "state",
            "Unknown"
        )

        nozzle = state.get(
            "nozzle"
        )

        bed = state.get(
            "bed"
        )

        progress = state.get(
            "progress"
        )

        layer = state.get(
            "current_layer"
        )

        total = state.get(
            "total_layers"
        )

        self.status_label.config(
            text=f"Printer: {status}"
        )

        metadata = (
            f"Layer: {layer}/{total}\n"
            f"Progress: {progress:.1f}%\n"
            f"Nozzle: {nozzle} C\n"
            f"Bed: {bed} C"
        )

        self.metadata_label.config(
            text=metadata
        )

    # ==========================================
    # Update JSON
    # ==========================================

    def update_json(
        self,
        data
    ):

        if data is None:
            return

        if isinstance(data, dict):

            text = json.dumps(
                data,
                indent=4
            )

        else:

            text = str(data)

        self.json_text.delete(
            "1.0",
            tk.END
        )

        self.json_text.insert(
            tk.END,
            text
        )

    # ==========================================
    # Update images
    # ==========================================

    def update_images(
        self,
        camera_path=None,
        render_path=None
    ):

        if camera_path:

            self._load_image(
                camera_path,
                self.camera_label,
                "camera"
            )

        if render_path:

            self._load_image(
                render_path,
                self.render_label,
                "render"
            )

    def _load_image(
        self,
        path,
        label,
        image_type
    ):

        path = Path(path)

        if not path.exists():
            return

        try:

            image = Image.open(path)

            image.thumbnail(
                (350, 350)
            )

            photo = ImageTk.PhotoImage(
                image
            )

            label.config(
                image=photo,
                text=""
            )

            if image_type == "camera":
                self.camera_photo = photo

            else:
                self.render_photo = photo

        except Exception as e:

            print(
                f"Panel image error: {e}"
            )

    # ==========================================
    # Keep Tk responsive
    # ==========================================

    def update(self):

        try:
            self.root.update_idletasks()
            self.root.update()

        except tk.TclError:
            pass

    def hide(self):

        self.root.withdraw()

    def show(self):

        self.root.deiconify()

    def close(self):

        try:
            self.root.destroy()

        except tk.TclError:
            pass