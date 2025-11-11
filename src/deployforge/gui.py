"""
Desktop GUI Application

Provides a graphical user interface for DeployForge using Tkinter.

Features:
- Image builder interface
- Profile and preset selection
- Progress tracking
- Analysis and validation
- Settings management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from pathlib import Path
from typing import Optional
import sys

logger = logging.getLogger(__name__)


class DeployForgeGUI:
    """Main GUI application."""

    def __init__(self, root: tk.Tk):
        """
        Initialize GUI.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("DeployForge - Windows Image Customization")
        self.root.geometry("900x700")

        # Variables
        self.image_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.selected_profile = tk.StringVar(value="gamer")
        self.selected_preset = tk.StringVar()

        # Progress tracking
        self.current_operation = tk.StringVar()
        self.progress_var = tk.DoubleVar()

        # Setup UI
        self._create_menu()
        self._create_notebook()
        self._create_status_bar()

        # Center window
        self._center_window()

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image...", command=self.select_image)
        file_menu.add_command(label="Recent Images", command=self.show_recent_images)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Analyze Image", command=self.analyze_image)
        tools_menu.add_command(label="Validate Image", command=self.validate_image)
        tools_menu.add_command(label="Compare Images", command=self.compare_images)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)

    def _create_notebook(self):
        """Create main notebook with tabs."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Builder tab
        builder_frame = ttk.Frame(notebook)
        notebook.add(builder_frame, text="Build Image")
        self._create_builder_tab(builder_frame)

        # Profiles tab
        profiles_frame = ttk.Frame(notebook)
        notebook.add(profiles_frame, text="Profiles")
        self._create_profiles_tab(profiles_frame)

        # Presets tab
        presets_frame = ttk.Frame(notebook)
        notebook.add(presets_frame, text="Presets")
        self._create_presets_tab(presets_frame)

        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self._create_settings_tab(settings_frame)

        # Log tab
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        self._create_log_tab(log_frame)

    def _create_builder_tab(self, parent: ttk.Frame):
        """Create image builder tab."""
        # Source image section
        source_frame = ttk.LabelFrame(parent, text="Source Image", padding=10)
        source_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(source_frame, text="Image Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(source_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(source_frame, text="Browse...", command=self.select_image).grid(row=0, column=2, pady=5)

        # Profile selection
        profile_frame = ttk.LabelFrame(parent, text="Profile", padding=10)
        profile_frame.pack(fill=tk.X, padx=10, pady=10)

        profiles = ['gamer', 'developer', 'enterprise', 'student', 'creator', 'custom']

        ttk.Label(profile_frame, text="Select Profile:").grid(row=0, column=0, sticky=tk.W, pady=5)
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.selected_profile, values=profiles, state='readonly', width=30)
        profile_combo.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        # Profile descriptions
        profile_descriptions = {
            'gamer': 'Gaming optimizations, performance tweaks, gaming launchers',
            'developer': 'Development tools, WSL2, Hyper-V, programming languages',
            'enterprise': 'Enterprise security, management features, BitLocker',
            'student': 'Balanced profile with productivity tools',
            'creator': 'Creative tools (OBS, GIMP, Audacity, Blender)',
            'custom': 'Minimal profile for manual customization'
        }

        description_label = ttk.Label(profile_frame, text=profile_descriptions['gamer'], wraplength=600, foreground='gray')
        description_label.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)

        def update_description(event):
            description_label.config(text=profile_descriptions.get(self.selected_profile.get(), ''))

        profile_combo.bind('<<ComboboxSelected>>', update_description)

        # Output section
        output_frame = ttk.LabelFrame(parent, text="Output", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(output_frame, text="Output Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(output_frame, text="Browse...", command=self.select_output).grid(row=0, column=2, pady=5)

        # Options
        options_frame = ttk.LabelFrame(parent, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.validate_option = tk.BooleanVar(value=True)
        self.report_option = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Validate after build", variable=self.validate_option).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Generate analysis report", variable=self.report_option).grid(row=1, column=0, sticky=tk.W)

        # Build button
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Build Image", command=self.build_image, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_build, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)

        # Progress section
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(progress_frame, textvariable=self.current_operation).pack(anchor=tk.W, pady=5)
        ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100).pack(fill=tk.X, pady=5)

    def _create_profiles_tab(self, parent: ttk.Frame):
        """Create profiles tab."""
        # Profile list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(list_frame, text="Available Profiles:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)

        profiles_data = [
            ("Gamer", "Gaming optimizations and performance tweaks"),
            ("Developer", "Development tools and programming environments"),
            ("Enterprise", "Enterprise security and management features"),
            ("Student", "Balanced profile for students"),
            ("Creator", "Content creation tools and optimizations"),
            ("Custom", "Minimal profile for manual customization")
        ]

        for name, description in profiles_data:
            profile_frame = ttk.Frame(list_frame, relief=tk.RIDGE, borderwidth=1)
            profile_frame.pack(fill=tk.X, pady=5, padx=5)

            ttk.Label(profile_frame, text=name, font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
            ttk.Label(profile_frame, text=description, foreground='gray').pack(anchor=tk.W, padx=10, pady=5)

            btn_frame = ttk.Frame(profile_frame)
            btn_frame.pack(anchor=tk.E, padx=10, pady=5)

            ttk.Button(btn_frame, text="View Details", command=lambda n=name: self.view_profile(n)).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Apply", command=lambda n=name: self.apply_profile_quick(n)).pack(side=tk.LEFT, padx=2)

    def _create_presets_tab(self, parent: ttk.Frame):
        """Create presets tab."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(toolbar, text="Create Preset", command=self.create_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Import Preset", command=self.import_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_presets).pack(side=tk.LEFT, padx=5)

        # Preset list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('Name', 'Description', 'Actions')
        self.preset_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)

        for col in columns:
            self.preset_tree.heading(col, text=col)
            self.preset_tree.column(col, width=200)

        self.preset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.preset_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preset_tree.configure(yscrollcommand=scrollbar.set)

    def _create_settings_tab(self, parent: ttk.Frame):
        """Create settings tab."""
        # General settings
        general_frame = ttk.LabelFrame(parent, text="General Settings", padding=10)
        general_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(general_frame, text="Python Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        python_path = tk.StringVar(value="python")
        ttk.Entry(general_frame, textvariable=python_path, width=40).grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(general_frame, text="Default Profile:").grid(row=1, column=0, sticky=tk.W, pady=5)
        default_profile = tk.StringVar(value="gamer")
        ttk.Combobox(general_frame, textvariable=default_profile, values=['gamer', 'developer', 'enterprise'], width=37).grid(row=1, column=1, pady=5, padx=5)

        # Advanced settings
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Settings", padding=10)
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(advanced_frame, text="Auto-validate images after build").grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(advanced_frame, text="Generate analysis reports automatically").grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(advanced_frame, text="Check for updates on startup").grid(row=2, column=0, sticky=tk.W)

        # Save settings
        ttk.Button(parent, text="Save Settings", command=self.save_settings).pack(pady=10)

    def _create_log_tab(self, parent: ttk.Frame):
        """Create log tab."""
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(toolbar, text="Clear Log", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)

    def _create_status_bar(self):
        """Create status bar."""
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(status_bar, textvariable=self.status_text, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def select_image(self):
        """Select source image file."""
        filename = filedialog.askopenfilename(
            title="Select Windows Image",
            filetypes=[("Windows Images", "*.wim *.esd"), ("All Files", "*.*")]
        )

        if filename:
            self.image_path.set(filename)
            self.log(f"Selected image: {filename}")

    def select_output(self):
        """Select output file."""
        filename = filedialog.asksaveasfilename(
            title="Save Customized Image As",
            defaultextension=".wim",
            filetypes=[("Windows Images", "*.wim"), ("All Files", "*.*")]
        )

        if filename:
            self.output_path.set(filename)
            self.log(f"Output path: {filename}")

    def build_image(self):
        """Build customized image."""
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select a source image")
            return

        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output path")
            return

        self.current_operation.set("Building image...")
        self.progress_var.set(0)
        self.status_text.set("Building...")

        # Run in thread to avoid blocking UI
        def build_thread():
            try:
                self.log(f"Building {self.selected_profile.get()} image...")

                # Simulate build process
                for i in range(0, 101, 10):
                    self.progress_var.set(i)
                    self.root.update_idletasks()
                    import time
                    time.sleep(0.5)

                self.log("Build completed successfully!")
                self.status_text.set("Build completed")

                messagebox.showinfo("Success", "Image built successfully!")

            except Exception as e:
                self.log(f"Build failed: {e}")
                messagebox.showerror("Error", f"Build failed: {e}")

        threading.Thread(target=build_thread, daemon=True).start()

    def cancel_build(self):
        """Cancel current build."""
        self.current_operation.set("Cancelled")
        self.status_text.set("Cancelled")
        self.log("Build cancelled by user")

    def analyze_image(self):
        """Analyze image."""
        filename = filedialog.askopenfilename(
            title="Select Image to Analyze",
            filetypes=[("Windows Images", "*.wim *.esd"), ("All Files", "*.*")]
        )

        if filename:
            self.log(f"Analyzing: {filename}")
            messagebox.showinfo("Analysis", "Image analysis feature coming soon!")

    def validate_image(self):
        """Validate image."""
        filename = filedialog.askopenfilename(
            title="Select Image to Validate",
            filetypes=[("Windows Images", "*.wim *.esd"), ("All Files", "*.*")]
        )

        if filename:
            self.log(f"Validating: {filename}")
            messagebox.showinfo("Validation", "Image validation feature coming soon!")

    def compare_images(self):
        """Compare two images."""
        self.log("Comparing images...")
        messagebox.showinfo("Compare", "Image comparison feature coming soon!")

    def view_profile(self, profile_name: str):
        """View profile details."""
        self.log(f"Viewing profile: {profile_name}")
        messagebox.showinfo("Profile", f"Details for {profile_name} profile")

    def apply_profile_quick(self, profile_name: str):
        """Quick apply profile."""
        self.selected_profile.set(profile_name.lower())
        self.log(f"Profile selected: {profile_name}")

    def create_preset(self):
        """Create new preset."""
        self.log("Creating preset...")
        messagebox.showinfo("Preset", "Preset creation feature coming soon!")

    def import_preset(self):
        """Import preset."""
        filename = filedialog.askopenfilename(
            title="Import Preset",
            filetypes=[("JSON Files", "*.json"), ("YAML Files", "*.yaml *.yml")]
        )

        if filename:
            self.log(f"Importing preset: {filename}")

    def refresh_presets(self):
        """Refresh preset list."""
        self.log("Refreshing presets...")

    def save_settings(self):
        """Save settings."""
        self.log("Settings saved")
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def save_log(self):
        """Save log to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if filename:
            Path(filename).write_text(self.log_text.get(1.0, tk.END))
            self.log(f"Log saved: {filename}")

    def show_recent_images(self):
        """Show recent images."""
        messagebox.showinfo("Recent", "Recent images feature coming soon!")

    def show_documentation(self):
        """Show documentation."""
        messagebox.showinfo("Help", "Documentation: https://github.com/YourOrg/DeployForge")

    def show_about(self):
        """Show about dialog."""
        about_text = """DeployForge v0.6.0

Windows Deployment Image Customization Suite

Features:
• Gaming and performance optimization
• Debloating and privacy tools
• Visual customization
• Developer environments
• Package management
• Container support
• Cloud integration
• AI-powered recommendations

© 2024 DeployForge Team
"""
        messagebox.showinfo("About DeployForge", about_text)

    def log(self, message: str):
        """
        Add message to log.

        Args:
            message: Log message
        """
        self.log_text.insert(tk.END, f"[{self._get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)
        logger.info(message)

    def _get_timestamp(self):
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def launch_gui():
    """Launch GUI application."""
    root = tk.Tk()

    # Set theme
    style = ttk.Style()
    style.theme_use('clam')

    app = DeployForgeGUI(root)

    root.mainloop()


if __name__ == '__main__':
    launch_gui()
