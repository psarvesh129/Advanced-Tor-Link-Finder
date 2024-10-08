import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  
import pandas as pd
import pickle

# Load the trained model and label encoder
with open('trained_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('label_encoder.pkl', 'rb') as encoder_file:
    label_encoder = pickle.load(encoder_file)

# Load the CSV data for displaying the dropdown options
df = pd.read_csv('unique_urls.csv')

# Function to get relevant links for a selected keyword
def get_links_for_keyword(keyword):
    filtered_df = df[df['keyword'].str.contains(keyword, case=False, na=False)]
    
    # If no links are found using keyword filtering, use the model to predict
    if filtered_df.empty:
        # Prepare the input features for the model
        url_features = {
            'url_length': len(keyword),
            'num_dots': keyword.count('.'),
            'num_slashes': keyword.count('/'),
            'keyword_length': len(keyword),
            'has_numbers': int(any(char.isdigit() for char in keyword)),
            'has_special_chars': int(any(not char.isalnum() for char in keyword))
        }
        
        # Convert to DataFrame for prediction
        features_df = pd.DataFrame([url_features])
        
        # Predict the keyword
        predicted_label = model.predict(features_df)
        predicted_keyword = label_encoder.inverse_transform(predicted_label)[0]
        
        # Find URLs for the predicted keyword
        filtered_df = df[df['keyword'] == predicted_keyword]

    return filtered_df['url'].tolist()

# Function to copy the selected URL to the clipboard
def copy_url(url):
    pyperclip.copy(url)
    messagebox.showinfo("Copied", f"URL copied to clipboard:\n{url}")

# Function to search for URLs based on a keyword from the dropdown or input
def search_links():
    keyword = entry_keyword.get().strip()  # Get the keyword entered by the user
    if keyword:
        links = get_links_for_keyword(keyword)
        display_results(keyword, links)  # Display keyword and links
    else:
        messagebox.showwarning("Input Error", "Please enter a keyword.")

# Function to display the predicted or searched links in the result section with a scrollbar
def display_results(keyword, links):
    # Clear previous results
    for widget in results_frame.winfo_children():
        widget.destroy()
    
    result_label.config(text=f"Results for Keyword: {keyword}")  # Display the keyword
    if links:
        canvas = tk.Canvas(results_frame)
        scrollbar = tk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display each URL with a "Copy" button
        for link in links:
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill="x", pady=2, padx=5)
            
            url_label = tk.Label(frame, text=link, fg="#007BFF", cursor="hand2", anchor='w', font=('Arial', 10))
            url_label.pack(side="left", fill="x", expand=True)

            copy_button = tk.Button(frame, text="Copy", command=lambda l=link: copy_url(l), width=8, bg="#28A745", fg="white")
            copy_button.pack(side="right")

    else:
        result_label.config(text=f"No related URLs found for '{keyword}'.")

# Function to populate the dropdown with unique keywords
def populate_dropdown():
    keywords = sorted(df['keyword'].unique())
    dropdown_menu['values'] = keywords

# Function to update input field when dropdown item is selected
def select_from_dropdown(event):
    selected_keyword = dropdown_menu.get()
    entry_keyword.delete(0, tk.END)
    entry_keyword.insert(0, selected_keyword)

# Create the main window
root = tk.Tk()
root.title("Advanced Tor Link Finder")
root.geometry("600x600")
root.config(bg="#f0f0f0")  # Set background color

# Styling using ttk Style
style = ttk.Style()
style.configure('TLabel', background="#f0f0f0", font=('Helvetica', 10))
style.configure('TButton', font=('Helvetica', 10), relief="flat", padding=5)
style.configure('TCombobox', font=('Helvetica', 10))
style.configure('TEntry', font=('Helvetica', 10))
style.configure('TFrame', background="#f0f0f0")

# Frame for the main content
content_frame = tk.Frame(root, bg="#f0f0f0")
content_frame.pack(pady=10, fill="both", expand=True)

# Header label
header_label = tk.Label(content_frame, text="Advanced Tor Link Finder", font=('Helvetica', 16, 'bold'), bg="#f0f0f0")
header_label.grid(row=0, column=0, columnspan=2, pady=10)

# Label for keyword input
label_keyword = tk.Label(content_frame, text="Enter Keyword to Search for URLs:", bg="#f0f0f0")
label_keyword.grid(row=1, column=0, sticky="w", padx=10)

# Entry box for keyword input with placeholder
entry_keyword = tk.Entry(content_frame, width=50)
entry_keyword.insert(0, "Type your keyword here...")
entry_keyword.bind("<FocusIn>", lambda e: entry_keyword.delete(0, tk.END) if entry_keyword.get() == "Type your keyword here..." else None)
entry_keyword.grid(row=1, column=1, pady=10)

# Dropdown label
label_dropdown = tk.Label(content_frame, text="Or Select a Keyword from the List:", bg="#f0f0f0")
label_dropdown.grid(row=2, column=0, sticky="w", padx=10)

# Dropdown menu for keyword selection
dropdown_menu = ttk.Combobox(content_frame)
dropdown_menu.grid(row=2, column=1, pady=10)
dropdown_menu.bind("<<ComboboxSelected>>", select_from_dropdown)

# Button to load keywords into the dropdown
load_button = tk.Button(content_frame, text="Load Keywords", command=populate_dropdown, bg="#007BFF", fg="white")
load_button.grid(row=3, column=0, columnspan=2, pady=10)

# Button to search for links based on keyword
search_button = tk.Button(content_frame, text="Search Links", command=search_links, bg="#007BFF", fg="white")
search_button.grid(row=4, column=0, columnspan=2, pady=20)

# Label to display prediction results
result_label = tk.Label(content_frame, text="", font=('Helvetica', 10, 'bold'), bg="#f0f0f0")
result_label.grid(row=5, column=0, columnspan=2, pady=10)

# Frame to display the results (links) with scrollbar
results_frame = tk.Frame(content_frame, bg="#f0f0f0")
results_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")

# Configure grid weights to allow expansion
content_frame.grid_rowconfigure(6, weight=1)  # Allow row 6 to expand
content_frame.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand
content_frame.grid_columnconfigure(1, weight=1)  # Allow column 1 to expand

# Disclaimer label
disclaimer_label = tk.Label(content_frame, text="Disclaimer: This is a personal model created to learn machine learning, scraping, and web development concepts. It is not a perfect tool but works well for providing Tor links.", wraplength=580, justify="center", bg="#f0f0f0", font=('Helvetica', 8))
disclaimer_label.grid(row=7, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
