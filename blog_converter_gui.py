#!/usr/bin/env python3
"""
DPP Blog Converter - GUI Application
Converts .docx blog files to clean HTML using Google Docs API
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
from io import StringIO

# Get the correct path for bundled files (PyInstaller support)
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Import the conversion functions from convert_blog
try:
    from convert_blog import get_credentials, convert_docx_to_html, OUTPUT_FOLDER, RAW_FOLDER
    from googleapiclient.discovery import build
except ImportError as e:
    print(f"Error importing convert_blog module: {e}")
    print("Make sure convert_blog.py is in the same directory as this script.")
    sys.exit(1)


class StreamCapture:
    """Captures stdout/stderr for display in GUI"""
    def __init__(self, callback):
        self.callback = callback
        self.buffer = StringIO()

    def write(self, text):
        if text and text.strip():
            self.callback(text)
        self.buffer.write(text)

    def flush(self):
        pass


class BlogConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DPP Blog Converter")
        self.root.geometry("700x900")
        self.root.resizable(True, True)

        # Config file to store project location
        self.config_file = Path.home() / ".dpp_blog_converter_config.json"
        self.project_folder = None

        # Check if we have a saved project location
        if self.load_config():
            self.show_main_ui()
        else:
            self.show_setup_screen()

    def load_config(self):
        """Load saved project location from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    project_folder = config.get('project_folder')

                    if project_folder and Path(project_folder).exists():
                        # Validate that it's a proper project folder
                        if self.validate_project_folder(project_folder):
                            self.project_folder = project_folder
                            return True
            except Exception as e:
                print(f"Error loading config: {e}")
        return False

    def save_config(self):
        """Save project location to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'project_folder': self.project_folder}, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def validate_project_folder(self, folder_path):
        """Check if folder contains convert_blog.py or DPPBlogConvert.exe"""
        folder = Path(folder_path)
        return (folder / "convert_blog.py").exists() or (folder / "DPPBlogConvert.exe").exists()

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_setup_screen(self):
        """Show initial setup screen with Setup and Find Project buttons"""
        self.clear_window()

        # Main frame
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header image for setup screen
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=20)

        # Try to load header image if it exists
        header_path = get_resource_path("header.png")
        if os.path.exists(header_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(header_path)
                # Resize to 2/3 size while maintaining aspect ratio
                img.thumbnail((427, 133), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                header_label = ttk.Label(header_frame, image=photo)
                header_label.image = photo  # Keep a reference
                header_label.pack()
            except Exception as e:
                # If image loading fails, show text instead
                print(f"Failed to load header.png: {e}")
                ttk.Label(header_frame, text="DPP BLOG CONVERTER",
                         font=('Arial', 24, 'bold')).pack()
        else:
            print(f"header.png not found at: {header_path}")
            ttk.Label(header_frame, text="DPP BLOG CONVERTER",
                     font=('Arial', 24, 'bold')).pack()

        # Welcome text
        ttk.Label(main_frame, text="Welcome to DPP Blog Converter",
                 font=('Arial', 16)).pack(pady=20)

        ttk.Label(main_frame, text="Choose an option to get started:",
                 font=('Arial', 11)).pack(pady=10)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)

        # Setup button
        setup_btn = ttk.Button(button_frame, text="Setup New Project",
                              command=self.setup_new_project, width=20)
        setup_btn.pack(pady=10)

        # Find Project button
        find_btn = ttk.Button(button_frame, text="Find Existing Project",
                             command=self.find_existing_project, width=20)
        find_btn.pack(pady=10)

        # Info text
        info_text = """Setup: Create a new DPPBlogBuilder folder at your chosen location
Find: Locate an existing DPPBlogBuilder installation"""

        ttk.Label(main_frame, text=info_text, font=('Arial', 9),
                 foreground='gray', justify=tk.CENTER).pack(pady=20)

    def setup_new_project(self):
        """Create new DPPBlogBuilder folder structure"""
        # Ask user where to create the project
        parent_folder = filedialog.askdirectory(
            title="Select location for DPPBlogBuilder folder",
            initialdir=str(Path.home() / "Desktop")
        )

        if not parent_folder:
            return  # User cancelled

        # Create DPPBlogBuilder folder
        project_folder = Path(parent_folder) / "DPPBlogBuilder"

        try:
            # Create main folder
            project_folder.mkdir(exist_ok=True)

            # Create subdirectories
            (project_folder / "todo").mkdir(exist_ok=True)
            (project_folder / "docx").mkdir(exist_ok=True)
            (project_folder / "output_html").mkdir(exist_ok=True)
            (project_folder / "raw_html").mkdir(exist_ok=True)

            # Copy convert_blog.py
            source_script = Path(__file__).parent / "convert_blog.py"
            if source_script.exists():
                shutil.copy2(source_script, project_folder / "convert_blog.py")

            # Copy tagFinder.py
            source_tagfinder = Path(__file__).parent / "tagFinder.py"
            if source_tagfinder.exists():
                shutil.copy2(source_tagfinder, project_folder / "tagFinder.py")

            # Create README.md (will be created separately)
            readme_path = project_folder / "README.md"
            if not readme_path.exists():
                readme_path.write_text("# DPP Blog Converter\n\nSee setup instructions below.")

            # Create Tags.txt
            tags_path = project_folder / "Tags.txt"
            if not tags_path.exists():
                tags_path.write_text("# Add your blog tags here, one per line\n")

            # Save project location
            self.project_folder = str(project_folder)
            self.save_config()

            # Show success message
            messagebox.showinfo("Setup Complete",
                              f"Project created successfully at:\n{project_folder}\n\n" +
                              "Please add your client_secret.json file to this folder.\n" +
                              "See README.md for instructions.")

            # Switch to main UI
            self.show_main_ui()

        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to create project:\n{e}")

    def find_existing_project(self):
        """Find and validate existing DPPBlogBuilder folder"""
        project_folder = filedialog.askdirectory(
            title="Select your DPPBlogBuilder folder",
            initialdir=str(Path.home() / "Desktop")
        )

        if not project_folder:
            return  # User cancelled

        # Validate the folder
        if not self.validate_project_folder(project_folder):
            messagebox.showerror("Invalid Project",
                               "The selected folder does not contain convert_blog.py or DPPBlogConvert.exe.\n\n" +
                               "Please select a valid DPPBlogBuilder folder.")
            return

        # Save and switch to main UI
        self.project_folder = project_folder
        self.save_config()
        self.show_main_ui()

    def show_main_ui(self):
        """Show main conversion interface"""
        self.clear_window()

        # Main frame
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Entry style for minimal, flat read-only fields
        style = ttk.Style(self.root)
        style.configure('FlatRO.TEntry', relief='flat', borderwidth=0, padding=(4, 2, 4, 2))
        self.tags_scroll_handler = None

        # Header image placeholder
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=10, fill=tk.X)

        # Try to load header image if it exists
        header_path = get_resource_path("header.png")
        if os.path.exists(header_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(header_path)
                # Resize to 2/3 size while maintaining aspect ratio
                img.thumbnail((427, 133), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                header_label = ttk.Label(header_frame, image=photo)
                header_label.image = photo  # Keep a reference
                header_label.pack()
            except Exception as e:
                print(f"Failed to load header.png: {e}")
                ttk.Label(header_frame, text="DPP BLOG CONVERTER",
                         font=('Arial', 20, 'bold')).pack()
        else:
            print(f"header.png not found at: {header_path}")
            ttk.Label(header_frame, text="DPP BLOG CONVERTER",
                     font=('Arial', 20, 'bold')).pack()

        # Project folder info with Change link
        project_frame = ttk.Frame(main_frame)
        project_frame.pack(pady=5)

        ttk.Label(project_frame, text="Current Project: ",
                 font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)

        change_link = ttk.Label(project_frame, text="Change",
                               font=('Arial', 9, 'underline'),
                               foreground='blue',
                               cursor='hand2')
        change_link.pack(side=tk.LEFT, padx=5)
        change_link.bind('<Button-1>', lambda e: self.change_project())

        ttk.Label(project_frame, text=f"{self.project_folder}",
                 font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)

        # Instruction text
        ttk.Label(main_frame, text="Convert everything in todo folder",
                 font=('Arial', 12)).pack(pady=15)

        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert",
                                     command=self.start_conversion,
                                     width=20)
        self.convert_btn.pack(pady=10)

        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Progress bar (determinate mode for real percentage)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(pady=10)

        # Completion label (replaces progress bar when done)
        self.completion_label = ttk.Label(progress_frame, text="",
                                         font=('Arial', 12, 'bold'),
                                         foreground='green')

        # Status text area (with scrollbar) - increased height
        status_scroll_frame = ttk.Frame(progress_frame)
        status_scroll_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(status_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_text = tk.Text(status_scroll_frame, height=16, width=70,
                                   yscrollcommand=scrollbar.set,
                                   font=('Consolas', 9),
                                   wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.status_text.yview)
        self.status_scroll_frame = status_scroll_frame

        # Configure text tags for colored output
        self.status_text.tag_configure('success', foreground='#00AA00')
        self.status_text.tag_configure('error', foreground='#CC0000')
        self.status_text.tag_configure('header', foreground='#0066CC', font=('Consolas', 9, 'bold'))

        # Tags display frame (separate from status) with its own scrollbar
        self.tags_frame = ttk.LabelFrame(main_frame, text="Blog Names & Tags", padding="10")
        tags_canvas = tk.Canvas(self.tags_frame, height=260, highlightthickness=0)
        tags_scrollbar = ttk.Scrollbar(self.tags_frame, orient="vertical", command=tags_canvas.yview)
        tags_canvas.configure(yscrollcommand=tags_scrollbar.set)
        tags_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tags_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner frame to hold each tag entry
        self.tags_inner = ttk.Frame(tags_canvas)
        tags_canvas.create_window((0, 0), window=self.tags_inner, anchor="nw")

        # Update scrollregion when inner frame changes size
        def _on_frame_configure(event):
            tags_canvas.configure(scrollregion=tags_canvas.bbox("all"))
        self.tags_inner.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            tags_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        for w in (self.tags_frame, tags_canvas, self.tags_inner):
            w.bind("<MouseWheel>", _on_mousewheel)
        self.tags_scroll_handler = _on_mousewheel

        self.tags_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Bottom button frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(pady=10)

        # Open output folder button (Change Project moved to top)
        ttk.Button(bottom_frame, text="Open Output Folder",
                  command=self.open_output_folder).pack()

    def update_status(self, message, tag=None):
        """Update status text area with new message and optional color tag"""
        if tag:
            self.status_text.insert(tk.END, message, tag)
        else:
            # Auto-detect success/error for coloring
            if '✓ SUCCESS' in message or '✓ ALL FILES' in message:
                self.status_text.insert(tk.END, message, 'success')
            elif '✗ FAILED' in message or 'Error:' in message:
                self.status_text.insert(tk.END, message, 'error')
            elif message.startswith('Processing:'):
                self.status_text.insert(tk.END, message, 'header')
            else:
                self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        self.status_text.update()

    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        # Check for client_secret.json
        client_secret_path = Path(self.project_folder) / "client_secret.json"
        if not client_secret_path.exists():
            messagebox.showerror("Missing Credentials",
                               "client_secret.json not found!\n\n" +
                               "Please add your Google API credentials to:\n" +
                               f"{self.project_folder}\n\n" +
                               "See README.md for instructions.")
            return

        # Check for .docx files in todo folder
        todo_folder = Path(self.project_folder) / "todo"
        docx_files = list(todo_folder.glob("*.docx"))

        if not docx_files:
            messagebox.showwarning("No Files",
                                 "No .docx files found in the todo folder.\n\n" +
                                 f"Please add .docx files to:\n{todo_folder}")
            return

        # Disable convert button
        self.convert_btn.config(state='disabled')

        # Clear status and hide completion label
        self.status_text.delete(1.0, tk.END)
        self.completion_label.pack_forget()
        self.progress_bar.pack(pady=10)
        for widget in self.tags_inner.winfo_children():
            widget.destroy()

        # Reset progress bar
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(docx_files)

        # Store file count for progress tracking
        self.total_files = len(docx_files)
        self.completed_files = 0

        # Run conversion in separate thread
        thread = threading.Thread(target=self.run_conversion, daemon=True)
        thread.start()

    def run_conversion(self):
        """Run the actual conversion process"""
        # Store conversion results (filename -> (html_path, tags))
        self.conversion_results = []

        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(self.project_folder)

            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = StreamCapture(self.update_status)

            try:
                # Get credentials
                self.update_status("Authenticating with Google...\n")

                # Check if token exists (first time setup)
                token_path = Path(self.project_folder) / "token.pickle"
                if not token_path.exists():
                    self.update_status("First-time setup: Browser will open for authentication...\n")
                    self.update_status("Please log in and grant access in your browser.\n\n")

                creds = get_credentials()
                drive_service = build("drive", "v3", credentials=creds)

                self.update_status("✓ Authentication successful!\n\n")

                # Get folders
                input_folder = Path(self.project_folder) / "todo"
                output_folder = Path(self.project_folder) / OUTPUT_FOLDER
                raw_folder = Path(self.project_folder) / RAW_FOLDER
                tags_file = Path(self.project_folder) / "Tags.txt"

                output_folder.mkdir(exist_ok=True)
                raw_folder.mkdir(exist_ok=True)

                self.update_status("Starting conversion...\n")
                self.update_status("-" * 60 + "\n\n")

                # Process each .docx file
                for filename in os.listdir(input_folder):
                    if filename.lower().endswith(".docx"):
                        input_path = input_folder / filename
                        self.update_status(f"Processing: {filename}\n")
                        try:
                            html_path, tags = convert_docx_to_html(
                                drive_service, str(input_path),
                                str(output_folder), str(raw_folder),
                                str(tags_file) if tags_file.exists() else None
                            )
                            # Success - add checkmark
                            self.update_status(f"  ✓ SUCCESS: {filename} converted\n\n")

                            # Store result for display
                            self.conversion_results.append((filename, html_path, tags))

                            # Update progress bar
                            self.completed_files += 1
                            self.root.after(0, lambda: self.progress_bar.config(value=self.completed_files))
                        except Exception as e:
                            # Failure - add red X
                            self.update_status(f"  ✗ FAILED: {filename}\n")
                            self.update_status(f"     Error: {e}\n\n")
                            self.completed_files += 1
                            self.root.after(0, lambda: self.progress_bar.config(value=self.completed_files))

                self.update_status("-" * 60 + "\n")
                self.update_status("✓ ALL FILES PROCESSED!\n\n")
                self.update_status(f"Output Location:\n")
                self.update_status(f"  • Cleaned HTML: {output_folder}\n")
                self.update_status(f"  • Raw HTML: {raw_folder}\n")
                self.update_status("-" * 60 + "\n")

                # Show completion in label instead of popup
                self.root.after(0, self.show_completion_with_tags)

            finally:
                # Restore stdout
                sys.stdout = old_stdout
                os.chdir(original_dir)

        except Exception as e:
            self.update_status(f"\nERROR: {e}\n")
            self.root.after(0, lambda: messagebox.showerror("Conversion Error",
                f"An error occurred during conversion:\n{e}"))

        finally:
            # Re-enable button (progress bar handled by show_completion)
            self.root.after(0, lambda: self.convert_btn.config(state='normal'))

    def show_completion(self):
        """Show completion message in place of progress bar"""
        # Hide progress bar
        self.progress_bar.pack_forget()

        # Show completion label with larger text in the same position as progress bar
        self.completion_label.config(text="✓ Conversion Complete!",
                                     font=('Arial', 14, 'bold'),
                                     foreground='#00AA00')

        # Pack it in the correct position (before the status area)
        # Find the status scroll frame to pack before it
        status_frame = None
        for child in self.completion_label.master.winfo_children():
            if isinstance(child, ttk.Frame) and child != self.completion_label.master:
                status_frame = child
                break

        if status_frame:
            self.completion_label.pack(before=status_frame, pady=15)
        else:
            self.completion_label.pack(pady=15)

    def show_completion_with_tags(self):
        """Show completion message with tags in separate frame"""
        # First, do the normal completion display
        self.show_completion()

        # Also write a summary into the status area for clarity
        self.update_status("\n--- Blog Names & Tags ---\n", 'header')

        # Clear any existing tags display
        for widget in self.tags_inner.winfo_children():
            widget.destroy()

        # Display each blog with its tags
        for idx, (filename, html_path, tags) in enumerate(self.conversion_results):
            base_name = os.path.splitext(filename)[0]

            # Build UI row for this entry
            entry = ttk.Frame(self.tags_inner, padding="6 4 6 6")
            entry.pack(fill=tk.X, pady=4)

            row1 = ttk.Frame(entry)
            row1.pack(fill=tk.X)
            row1.columnconfigure(1, weight=1)

            ttk.Label(row1, text="name:",
                      font=('Consolas', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 6))

            name_entry = tk.Entry(
                row1,
                width=42,
                relief='flat',
                borderwidth=0,
                highlightthickness=0,
                background=self.root.cget('bg'),
                fg='#000',
                readonlybackground=self.root.cget('bg')
            )
            name_entry.insert(0, base_name)
            name_entry.config(state='readonly')
            name_entry.grid(row=0, column=1, sticky='ew', padx=(0, 8))

            copy_btn = ttk.Button(row1, text="Copy HTML",
                                  command=lambda p=html_path: self.copy_html_to_clipboard(p),
                                  width=12)
            copy_btn.grid(row=0, column=2, sticky='e', padx=5)

            row2 = ttk.Frame(entry)
            row2.pack(fill=tk.X, pady=(4, 0))
            row2.columnconfigure(1, weight=1)

            ttk.Label(row2, text="tags:",
                      font=('Consolas', 10, 'bold')).grid(row=0, column=0, sticky='nw', padx=(0, 6), pady=(2, 0))

            tags_text = ", ".join(tags) if tags else "(none found)"
            tags_box = tk.Text(
                row2, height=3, wrap=tk.WORD,
                font=('Consolas', 10),
                borderwidth=0, relief='flat',
                background=self.root.cget('bg'),  # match window background
            )
            tags_box.insert('1.0', tags_text)
            tags_box.config(state='disabled')
            tags_box.grid(row=0, column=1, sticky='ew')

            # Bind mousewheel to scroll the tags area even when hovering inputs/text
            if self.tags_scroll_handler:
                for w in (entry, row1, row2, name_entry, copy_btn, tags_box):
                    w.bind("<MouseWheel>", self.tags_scroll_handler)

            # Mirror the info in the status box so it's always visible
            self.update_status(f"name: {base_name}\n", 'header')
            self.update_status(f"tags: {tags_text}\n-\n")

    def copy_html_to_clipboard(self, html_path):
        """Copy HTML content to clipboard"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(html_content)
            self.root.update()  # Required for clipboard to work

            # Show brief confirmation
            messagebox.showinfo("Copied!", f"HTML content copied to clipboard!\n\nReady to paste into your blog editor.")

        except Exception as e:
            messagebox.showerror("Copy Failed", f"Failed to copy HTML:\n{e}")

    def change_project(self):
        """Allow user to change project folder"""
        # Go directly to setup screen
        self.show_setup_screen()

    def open_output_folder(self):
        """Open the output_html folder in file explorer"""
        output_folder = Path(self.project_folder) / OUTPUT_FOLDER
        if output_folder.exists():
            os.startfile(output_folder)
        else:
            messagebox.showwarning("Folder Not Found",
                                 "Output folder doesn't exist yet.\n" +
                                 "Run a conversion first.")


def main():
    root = tk.Tk()
    app = BlogConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
