import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import os

class PDFSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter & Merger")
        self.root.geometry("700x700")
        self.root.configure(padx=20, pady=20)
        
        # Store selected PDFs for merging
        self.selected_pdfs = []

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
        self.split_button.pack(pady=10)

        # Separator
        separator = tk.Frame(root, height=2, bg="gray")
        separator.pack(fill="x", padx=5, pady=10)

        # Merge PDF section
        self.merge_frame = tk.LabelFrame(root, text="Merge PDFs", padx=10, pady=10)
        self.merge_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Listbox with scrollbar for selected PDFs
        listbox_frame = tk.Frame(self.merge_frame)
        listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        self.pdf_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=8)
        self.pdf_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.pdf_listbox.yview)

        # Buttons for merge section
        merge_buttons_frame = tk.Frame(self.merge_frame)
        merge_buttons_frame.pack(fill="x", padx=5, pady=5)

        self.browse_merge_button = tk.Button(merge_buttons_frame, text="Add PDFs", command=self.browse_merge_files)
        self.browse_merge_button.pack(side="left", padx=5)

        self.remove_button = tk.Button(merge_buttons_frame, text="Remove Selected", command=self.remove_selected)
        self.remove_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(merge_buttons_frame, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side="left", padx=5)

        # Order adjustment buttons
        order_frame = tk.Frame(merge_buttons_frame)
        order_frame.pack(side="left", padx=10)

        self.move_up_button = tk.Button(order_frame, text="↑ Move Up", command=self.move_up)
        self.move_up_button.pack(side="left", padx=2)

        self.move_down_button = tk.Button(order_frame, text="↓ Move Down", command=self.move_down)
        self.move_down_button.pack(side="left", padx=2)

        self.merge_button = tk.Button(merge_buttons_frame, text="Merge PDFs", command=self.merge_pdfs)
        self.merge_button.pack(side="right", padx=5)

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

    def browse_merge_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filenames:
            for filename in filenames:
                if filename not in self.selected_pdfs:
                    self.selected_pdfs.append(filename)
                    self.pdf_listbox.insert(tk.END, os.path.basename(filename))

    def remove_selected(self):
        selected_indices = self.pdf_listbox.curselection()
        # Remove in reverse order to maintain correct indices
        for index in reversed(selected_indices):
            self.pdf_listbox.delete(index)
            del self.selected_pdfs[index]

    def clear_all(self):
        self.pdf_listbox.delete(0, tk.END)
        self.selected_pdfs.clear()

    def move_up(self):
        selected_indices = list(self.pdf_listbox.curselection())
        if not selected_indices:
            return
        
        # Get the first selected index
        index = selected_indices[0]
        if index > 0:
            # Swap items in listbox
            item_text = self.pdf_listbox.get(index)
            self.pdf_listbox.delete(index)
            self.pdf_listbox.insert(index - 1, item_text)
            
            # Swap items in selected_pdfs list
            self.selected_pdfs[index], self.selected_pdfs[index - 1] = \
                self.selected_pdfs[index - 1], self.selected_pdfs[index]
            
            # Update selection to maintain focus on moved item
            self.pdf_listbox.selection_clear(0, tk.END)
            self.pdf_listbox.selection_set(index - 1)
            self.pdf_listbox.see(index - 1)

    def move_down(self):
        selected_indices = list(self.pdf_listbox.curselection())
        if not selected_indices:
            return
        
        # Get the last selected index (or first if single selection)
        index = selected_indices[-1] if len(selected_indices) > 1 else selected_indices[0]
        if index < len(self.selected_pdfs) - 1:
            # Swap items in listbox
            item_text = self.pdf_listbox.get(index)
            self.pdf_listbox.delete(index)
            self.pdf_listbox.insert(index + 1, item_text)
            
            # Swap items in selected_pdfs list
            self.selected_pdfs[index], self.selected_pdfs[index + 1] = \
                self.selected_pdfs[index + 1], self.selected_pdfs[index]
            
            # Update selection to maintain focus on moved item
            self.pdf_listbox.selection_clear(0, tk.END)
            self.pdf_listbox.selection_set(index + 1)
            self.pdf_listbox.see(index + 1)

    def merge_pdfs(self):
        if len(self.selected_pdfs) < 2:
            messagebox.showerror("Error", "Please select at least 2 PDF files to merge")
            return

        try:
            # Ask user for output file location
            output_path = filedialog.asksaveasfilename(
                title="Save merged PDF as",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if not output_path:
                return

            # Create PDF writer object
            writer = PdfWriter()

            # Merge all PDFs
            for pdf_path in self.selected_pdfs:
                try:
                    reader = PdfReader(pdf_path)
                    # Add all pages from this PDF
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read {os.path.basename(pdf_path)}: {str(e)}")
                    return

            # Write the merged PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            output_filename = os.path.basename(output_path)
            self.status_label.config(
                text=f"Success! Merged PDF saved as: {output_filename}",
                fg="green"
            )
            messagebox.showinfo("Success", f"Merged {len(self.selected_pdfs)} PDFs successfully!\nSaved as: {output_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while merging: {str(e)}")
            self.status_label.config(text="Failed to merge PDFs", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterApp(root)
    root.mainloop()
