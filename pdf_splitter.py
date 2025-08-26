import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import os

class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter")
        self.root.geometry("600x400")
        self.root.configure(padx=20, pady=20)

        # Input file section
        self.input_frame = tk.LabelFrame(root, text="Input PDF", padx=10, pady=10)
        self.input_frame.pack(fill="x", padx=5, pady=5)

        self.input_path = tk.StringVar()
        self.input_entry = tk.Entry(self.input_frame, textvariable=self.input_path, width=50)
        self.input_entry.pack(side="left", padx=5)

        self.browse_button = tk.Button(self.input_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side="left", padx=5)

        # Page range section
        self.range_frame = tk.LabelFrame(root, text="Page Range", padx=10, pady=10)
        self.range_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(self.range_frame, text="Start Page:").pack(side="left", padx=5)
        self.start_page = tk.Entry(self.range_frame, width=10)
        self.start_page.pack(side="left", padx=5)

        tk.Label(self.range_frame, text="End Page:").pack(side="left", padx=5)
        self.end_page = tk.Entry(self.range_frame, width=10)
        self.end_page.pack(side="left", padx=5)

        # Split button
        self.split_button = tk.Button(root, text="Split PDF", command=self.split_pdf)
        self.split_button.pack(pady=20)

        # Status label
        self.status_label = tk.Label(root, text="", wraplength=500)
        self.status_label.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)

    def split_pdf(self):
        input_path = self.input_path.get()
        
        try:
            start = int(self.start_page.get())
            end = int(self.end_page.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid page numbers")
            return

        if not input_path:
            messagebox.showerror("Error", "Please select an input PDF file")
            return

        try:
            # Create PDF reader object
            reader = PdfReader(input_path)
            
            # Validate page range
            if start < 1 or end > len(reader.pages) or start > end:
                messagebox.showerror("Error", 
                    f"Invalid page range. PDF has {len(reader.pages)} pages.")
                return

            # Create PDF writer object
            writer = PdfWriter()

            # Add specified pages to writer
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])

            # Generate output filename
            input_dir = os.path.dirname(input_path)
            input_filename = os.path.basename(input_path)
            output_filename = f"{os.path.splitext(input_filename)[0]}_pages_{start}_to_{end}.pdf"
            output_path = os.path.join(input_dir, output_filename)

            # Write the output PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            self.status_label.config(
                text=f"Success! New PDF saved as: {output_filename}",
                fg="green"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Failed to split PDF", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterApp(root)
    root.mainloop()
