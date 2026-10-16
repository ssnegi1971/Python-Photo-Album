import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

class ImageGalleryViewer(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("Image Scanner with Safe Top-Controls")
    self.geometry("1100x750")

    # Image tracking and properties
    self.photo_images = {}  # Map filename to its thumbnail PhotoImage object
    self.image_files = []  # Ordered list of all absolute file paths
    self.current_index = -1  # Index of the currently viewed image
    self.thumbnail_size = (80, 80)
    self.current_large_image = None

    # Top Control Frame (Directory Scan Selection Bar)
    ctrl_frame = ttk.Frame(self, padding=10)
    ctrl_frame.pack(fill=tk.X, side=tk.TOP)
    
    # --- CHANGED: Default value set to blank string ---
    self.dir_path_var = tk.StringVar(value="")
    
    ttk.Label(ctrl_frame, text="Directory:").pack(side=tk.LEFT, padx=5)
    ttk.Entry(ctrl_frame, textvariable=self.dir_path_var, width=60).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(ctrl_frame, text="Browse...", command=self.browse_directory).pack(
        side=tk.LEFT, padx=5
    )
    ttk.Button(ctrl_frame, text="Scan & Display", command=self.load_images).pack(
        side=tk.LEFT, padx=5
    )

    # Main Split Layout (PanedWindow)
    self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
    self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Left Frame: Scrollable Thumbnail List
    self.left_container = ttk.Frame(self.paned_window, width=400)
    self.canvas = tk.Canvas(self.left_container, bg="#f5f5f5")
    self.v_scrollbar = ttk.Scrollbar(
        self.left_container, orient=tk.VERTICAL, command=self.canvas.yview
    )
    self.scrollable_frame = ttk.Frame(self.canvas)
    self.scrollable_frame.bind(
        "<Configure>",
        lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ),
    )
    self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
    self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
    self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Right Frame: Viewer & Navigation Panel Container
    self.right_container = ttk.Frame(self.paned_window)

    # --- MOVED TO TOP OF PANE ---
    # Cycle Navigation Bar (Placed before/above the image display frame)
    self.nav_frame = ttk.Frame(self.right_container, padding=10)
    self.nav_frame.pack(fill=tk.X, side=tk.TOP)
    self.prev_btn = ttk.Button(
        self.nav_frame, text="◀ Previous", command=self.show_previous
    )
    self.prev_btn.pack(side=tk.LEFT, expand=True)
    self.status_label = ttk.Label(
        self.nav_frame, text="0 / 0", font=("Arial", 10, "bold"), justify=tk.CENTER
    )
    self.status_label.pack(side=tk.LEFT, expand=True)
    self.next_btn = ttk.Button(
        self.nav_frame, text="Next ▶", command=self.show_next
    )
    self.next_btn.pack(side=tk.LEFT, expand=True)

    # Display area frame (Fills the remaining space underneath the controls)
    self.preview_box = ttk.LabelFrame(
        self.right_container, text=" Preview Pane ", padding=10
    )
    self.preview_box.pack(fill=tk.BOTH, expand=True)
    self.preview_label = ttk.Label(
        self.preview_box, text="Select a thumbnail to preview", anchor="center"
    )
    self.preview_label.pack(fill=tk.BOTH, expand=True)

    # Add panes to the main window split
    self.paned_window.add(self.left_container, weight=1)
    self.paned_window.add(self.right_container, weight=2)

    # Event Bindings
    self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    self.preview_box.bind("<Configure>", self.on_preview_panel_resize)

    # Keyboard shortcuts for cycling
    self.bind("<Left>", lambda event: self.show_previous())
    self.bind("<Right>", lambda event: self.show_next())

    # --- REMOVED: self.load_images() auto-scan on launch ---

  def _on_mousewheel(self, event):
    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  def browse_directory(self):
    selected_dir = filedialog.askdirectory(initialdir=self.dir_path_var.get())
    if selected_dir:
      self.dir_path_var.set(selected_dir)
      self.load_images()

  def load_images(self):
    target_dir = self.dir_path_var.get()
    if not os.path.isdir(target_dir):
      messagebox.showerror("Error", "Selected path is not a valid directory.")
      return

    # Reset UI states
    for widget in self.scrollable_frame.winfo_children():
      widget.destroy()
    self.photo_images.clear()
    self.image_files.clear()
    self.current_index = -1
    self.preview_label.config(image="", text="Select a thumbnail to preview")
    self.status_label.config(text="0 / 0")

    valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    try:
      files = sorted(
          [
              f
              for f in os.listdir(target_dir)
              if f.lower().endswith(valid_exts)
          ]
      )
    except Exception as e:
      messagebox.showerror("Error", f"Failed to read directory: {e}")
      return

    if not files:
      ttk.Label(
          self.scrollable_frame, text="No image files found."
      ).pack(padx=20, pady=20)
      return

    self.image_files = [os.path.join(target_dir, f) for f in files]
    columns = 3
    for idx, filename in enumerate(files):
      file_path = self.image_files[idx]
      try:
        img = Image.open(file_path)
        img.thumbnail(self.thumbnail_size)
        photo = ImageTk.PhotoImage(img)
        self.photo_images[filename] = photo
        card = ttk.Frame(
            self.scrollable_frame, borderwidth=1, relief="solid", padding=2
        )
        r, c = idx // columns, idx % columns
        card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        img_label = ttk.Label(card, image=photo, cursor="hand2")
        img_label.pack()
        img_label.bind(
            "<Button-1>",
            lambda e, idx_val=idx: self.display_large_image_by_index(idx_val),
        )
        card.bind(
            "<Button-1>",
            lambda e, idx_val=idx: self.display_large_image_by_index(idx_val),
        )
      except Exception as e:
        print(f"Skiipping {filename}: {e}")

  def display_large_image_by_index(self, index):
    """Loads image tracking parameters by index array coordinates safely."""
    if not (0 <= index < len(self.image_files)):
      return
    self.current_index = index
    file_path = self.image_files[self.current_index]
    try:
      img = Image.open(file_path)
      # Extract updated dimensions for the display window 
      max_w = max(self.preview_box.winfo_width() - 20, 100)
      max_h = max(self.preview_box.winfo_height() - 40, 100)
      # Aspect ratio fit scaling
      img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
      self.current_large_image = ImageTk.PhotoImage(img)
      self.preview_label.config(image=self.current_large_image, text="")
      # Update status counters
      filename = os.path.basename(file_path)
      self.status_label.config(
          text=f"{self.current_index + 1} / {len(self.image_files)}\n{filename}"
      )
    except Exception as e:
      self.preview_label.config(
          image="", text=f"Error displaying preview:\n{e}"
      )

  def show_previous(self):
    if not self.image_files:
      return
    new_index = (
        (self.current_index - 1) if self.current_index > 0 else (len(self.image_files) - 1)
    )
    self.display_large_image_by_index(new_index)

  def show_next(self):
    if not self.image_files:
      return
    new_index = (self.current_index + 1) % len(self.image_files)
    self.display_large_image_by_index(new_index)

  def on_preview_panel_resize(self, event):
    """Maintains clean scaling updates during panel configuration modifications."""
    if self.current_index != -1:
      self.after(
          50, lambda: self.display_large_image_by_index(self.current_index)
      )

if __name__ == "__main__":
  app = ImageGalleryViewer()
  app.mainloop()
