import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import csv
from fpdf import FPDF
import os
import datetime
import requests

root = tk.Tk()
root.title("Patient Appointment & Billing Tracker")
root.geometry("1100x650")
root.configure(bg='#f0f4ff')

patients = []

# ==== Functions ====
def send_sms(name, doctor, date, token, phone):
    url = "https://www.fast2sms.com/dev/bulkV2"
    message = f"Hello {name}, your appointment with Dr. {doctor} is confirmed.\nDate: {date}\nToken No: {token}\nThank you."
    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "v3",
        "numbers": phone
    }
    headers = {
        'authorization': 'GEx2cF3sZdBoTaeUg7QjDCt6XpP8ArVb5IwfMk9J0huLmqnS1KtCS5hHJPFled0ANYyMUxZ7kRo81Dfr',  # Replace this with your actual Fast2SMS API key
        'Content-Type': "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        print("SMS Sent:", response.json())
    except Exception as e:
        print("SMS failed:", e)

def add_patient():
    if not all([name_var.get(), age_var.get(), gender_var.get(), date_var.get(), treat_var.get(), bill_var.get(), doc_var.get(), phone_var.get()]):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    entry = [name_var.get(), age_var.get(), gender_var.get(), date_var.get(), treat_var.get(), bill_var.get(), doc_var.get(), phone_var.get()]
    patients.append(entry)
    table.insert("", "end", values=entry)

    # Send SMS
    send_sms(name_var.get(), doc_var.get(), date_var.get(), str(len(patients)), phone_var.get())

    clear_fields()

def delete_patient():
    selected = table.selection()
    for item in selected:
        item_values = table.item(item)['values']
        if item_values in patients:
            patients.remove(item_values)
        table.delete(item)

def update_patient():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Update Error", "No patient selected.")
        return
    table.item(selected[0], values=(name_var.get(), age_var.get(), gender_var.get(), date_var.get(), treat_var.get(), bill_var.get(), doc_var.get(), phone_var.get()))
    index = table.index(selected[0])
    patients[index] = [name_var.get(), age_var.get(), gender_var.get(), date_var.get(), treat_var.get(), bill_var.get(), doc_var.get(), phone_var.get()]
    clear_fields()

def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Age", "Gender", "Appointment Date", "Treatment", "Bill", "Doctor", "Phone"])
            writer.writerows(patients)
        messagebox.showinfo("Exported", "Data exported to CSV successfully.")

def export_pdf():
    file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Patient Appointments", ln=True, align='C')
        pdf.ln(10)

        for row in patients:
            pdf.cell(200, 10, txt=", ".join(str(x) for x in row), ln=True)

        pdf.output(file)
        messagebox.showinfo("Exported", "Data exported to PDF successfully.")

def print_data():
    temp_file = "temp_print.txt"
    with open(temp_file, "w") as f:
        for row in patients:
            f.write(", ".join(str(x) for x in row) + "\n")
    os.startfile(temp_file, "print")

def clear_fields():
    for var in [name_var, age_var, gender_var, date_var, treat_var, bill_var, doc_var, phone_var]:
        var.set("")

def search_patient():
    query = search_var.get().lower()
    for item in table.get_children():
        table.delete(item)
    for row in patients:
        if query in ",".join(str(x).lower() for x in row):
            table.insert("", "end", values=row)

# ==== Variables ====
name_var = tk.StringVar()
age_var = tk.StringVar()
gender_var = tk.StringVar()
date_var = tk.StringVar()
treat_var = tk.StringVar()
bill_var = tk.StringVar()
doc_var = tk.StringVar()
phone_var = tk.StringVar()
search_var = tk.StringVar()

# ==== UI Layout ====
title = tk.Label(root, text="Patient Appointment & Billing Tracker", font=("Helvetica", 20, "bold"), bg="#4a7abc", fg="white", pady=10)
title.pack(fill=tk.X)

frame = tk.Frame(root, bg="#f0f4ff")
frame.pack(pady=10)

entries = [
    ("Patient Name", name_var),
    ("Age", age_var),
    ("Gender", gender_var),
    ("Appointment Date", date_var),
    ("Treatment", treat_var),
    ("Bill Amount", bill_var),
    ("Doctor Name", doc_var),
    ("Phone No", phone_var)
]

for i, (label, var) in enumerate(entries):
    tk.Label(frame, text=label, font=("Arial", 12), bg="#f0f4ff").grid(row=i//2, column=(i%2)*2, padx=10, pady=5, sticky="e")
    if label == "Appointment Date":
        DateEntry(frame, textvariable=var, width=18, background='darkblue', foreground='white').grid(row=i//2, column=(i%2)*2+1, padx=10, pady=5)
    else:
        tk.Entry(frame, textvariable=var, width=20).grid(row=i//2, column=(i%2)*2+1, padx=10, pady=5)

# ==== Buttons ====
btn_frame = tk.Frame(root, bg="#f0f4ff")
btn_frame.pack(pady=10)

for text, cmd in [
    ("Add", add_patient),
    ("Delete", delete_patient),
    ("Update", update_patient),
    ("Export CSV", export_csv),
    ("Export PDF", export_pdf),
    ("Print", print_data)
]:
    tk.Button(btn_frame, text=text, width=12, bg="#4a7abc", fg="white", font=("Arial", 10), command=cmd).pack(side=tk.LEFT, padx=5)

# ==== Search Box ====
search_frame = tk.Frame(root, bg="#f0f4ff")
search_frame.pack()
tk.Label(search_frame, text="Search:", bg="#f0f4ff", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
tk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT)
tk.Button(search_frame, text="Go", command=search_patient).pack(side=tk.LEFT, padx=5)

# ==== Table ====
table = ttk.Treeview(root, columns=("Name", "Age", "Gender", "Date", "Treatment", "Bill", "Doctor", "Phone"), show="headings", height=10)
for col in table['columns']:
    table.heading(col, text=col)
    table.column(col, width=120)
table.pack(pady=10)

root.mainloop()
