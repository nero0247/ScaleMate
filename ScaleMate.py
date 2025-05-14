import tkinter as tk
from tkinter import ttk, messagebox
import uuid

# --- Conversion Logic Functions ---

def eng_to_raw(eng_value, lrv, urv, resolution, current_type=None):
    max_count = (2 ** resolution) - 1
    if current_type == "4–20 mA" and resolution == 12:
        raw_low = 655   # Hardware-specific: 4 mA maps to raw count 655
        raw_high = 3276 # Hardware-specific: 20 mA maps to raw count 3276
        percent = (eng_value - lrv) / (urv - lrv)
        return round(raw_low + percent * (raw_high - raw_low))
    return round(((eng_value - lrv) / (urv - lrv)) * max_count)

def raw_to_eng(raw_count, lrv, urv, resolution, current_type=None):
    max_count = (2 ** resolution) - 1
    if current_type == "4–20 mA" and resolution == 12:
        raw_low = 655   # Hardware-specific: 4 mA maps to raw count 655
        raw_high = 3276 # Hardware-specific: 20 mA maps to raw count 3276
        raw_count = max(min(raw_count, raw_high), raw_low)
        percent = (raw_count - raw_low) / (raw_high - raw_low)
        return lrv + percent * (urv - lrv)
    return ((raw_count / max_count) * (urv - lrv)) + lrv

def raw_to_voltage(raw_count, resolution, signal_type):
    max_count = (2 ** resolution) - 1
    if signal_type == "Voltage (0–5V)":
        return (raw_count / max_count) * 5.0
    elif signal_type == "Voltage (0–10V)":
        return (raw_count / max_count) * 10.0
    elif signal_type == "Voltage (1–5V)":
        return 1.0 + (raw_count / max_count) * 4.0  # Offset of 1V, span of 4V
    return 0.0

def raw_to_ma(raw_count, resolution, current_type):
    max_count = (2 ** resolution) - 1
    if current_type == "0–20 mA":
        return (raw_count / max_count) * 20
    elif current_type == "0–25 mA":
        return (raw_count / max_count) * 25
    elif current_type == "4–20 mA":
        if resolution == 12:
            raw_low = 655   # Hardware-specific: 4 mA maps to raw count 655
            raw_high = 3276 # Hardware-specific: 20 mA maps to raw count 3276
            raw_count = max(min(raw_count, raw_high), raw_low)
            return 4 + ((raw_count - raw_low) / (raw_high - raw_low) * 16)
        else:
            return 4 + ((raw_count / max_count) * 16)
    return 0

def get_signal_mode():
    selection = signal_type_var.get()
    return "voltage" if selection.startswith("Voltage") else "current"

def get_percent_span(value, lrv, urv):
    return ((value - lrv) / (urv - lrv)) * 100

# --- Button Actions ---

def convert_eng_to_raw():
    try:
        lrv = float(lrv_entry.get())
        urv = float(urv_entry.get())
        eng_value = float(eng_entry.get())
        resolution = int(res_var.get())
        signal_type = signal_type_var.get()
        mode = get_signal_mode()
        
        if lrv >= urv:
            raise ValueError("LRV must be less than URV")
        if not (lrv <= eng_value <= urv):
            raise ValueError("Engineering value must be between LRV and URV")

        raw = eng_to_raw(eng_value, lrv, urv, resolution, signal_type)
        percent = get_percent_span(eng_value, lrv, urv)
        result_var.set(f"Raw Count ({resolution}-bit): {raw}")
        percent_var_display.set(f"{percent:.1f}%")

        if mode == "voltage":
            voltage = raw_to_voltage(raw, resolution, signal_type)
            voltage_var_display.set(f"{voltage:.3f} V")
            ma_var_display.set("")
        else:
            ma = raw_to_ma(raw, resolution, signal_type)
            ma_var_display.set(f"{ma:.2f} mA")
            voltage_var_display.set("")

    except ValueError as e:
        messagebox.showerror("Error", str(e) if str(e) else "Please enter valid numeric values.")

def convert_raw_to_eng():
    try:
        lrv = float(lrv_entry.get())
        urv = float(urv_entry.get())
        raw_count = int(raw_entry.get())
        resolution = int(res_var.get())
        signal_type = signal_type_var.get()
        mode = get_signal_mode()

        max_count = (2 ** resolution) - 1
        if lrv >= urv:
            raise ValueError("LRV must be less than URV")
        if not (0 <= raw_count <= max_count):
            raise ValueError(f"Raw count must be between 0 and {max_count}")
        if signal_type == "4–20 mA" and resolution == 12:
            if not (655 <= raw_count <= 3276):
                raise ValueError("Raw count must be between 655 and 3276 for 4–20 mA, 12-bit")

        eng = raw_to_eng(raw_count, lrv, urv, resolution, signal_type)
        percent = get_percent_span(eng, lrv, urv)
        result_var.set(f"Engineering Value: {eng:.4f}")
        percent_var_display.set(f"{percent:.1f}%")

        if mode == "voltage":
            voltage = raw_to_voltage(raw_count, resolution, signal_type)
            voltage_var_display.set(f"{voltage:.3f} V")
            ma_var_display.set("")
        else:
            ma = raw_to_ma(raw_count, resolution, signal_type)
            ma_var_display.set(f"{ma:.2f} mA")
            voltage_var_display.set("")

    except ValueError as e:
        messagebox.showerror("Error", str(e) if str(e) else "Please enter valid numeric values.")

def clear_all():
    lrv_entry.delete(0, tk.END)
    urv_entry.delete(0, tk.END)
    eng_entry.delete(0, tk.END)
    raw_entry.delete(0, tk.END)
    result_var.set("")
    voltage_var_display.set("")
    ma_var_display.set("")
    percent_var_display.set("")

# GUI Initialization and Layout

root = tk.Tk()
root.title("Transmitter Conversion Tool")

frame = ttk.Frame(root, padding=8)
frame.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Button Panel (Left)
button_frame = ttk.Frame(frame)
button_frame.grid(row=0, column=0, sticky="ns", padx=6, pady=4)

ttk.Button(button_frame, text="Convert to Raw", command=convert_eng_to_raw).pack(fill="x", pady=2)
ttk.Button(button_frame, text="Convert to Engineering", command=convert_raw_to_eng).pack(fill="x", pady=2)
ttk.Button(button_frame, text="Clear", command=clear_all).pack(fill="x", pady=2)

# Input/Output Panel (Right)
input_frame = ttk.Frame(frame)
input_frame.grid(row=0, column=1, sticky="nsew", pady=4)

row_idx = 0

def add_labeled_entry(label_text, var=None):
    global row_idx
    ttk.Label(input_frame, text=label_text).grid(row=row_idx, column=0, sticky="e", pady=2)
    entry = ttk.Entry(input_frame, textvariable=var) if var else ttk.Entry(input_frame)
    entry.grid(row=row_idx, column=1, sticky="ew", pady=2)
    row_idx += 1
    return entry

# Signal Type
ttk.Label(input_frame, text="Signal Type:").grid(row=row_idx, column=0, sticky="e", pady=2)
signal_type_var = tk.StringVar(value="Voltage (0–5V)")
signal_type_combo = ttk.Combobox(
    input_frame, textvariable=signal_type_var,
    values=["Voltage (0–5V)", "Voltage (0–10V)", "Voltage (1–5V)", "4–20 mA", "0–20 mA", "0–25 mA"],
    state="readonly"
)
signal_type_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
row_idx += 1

# Inputs
lrv_entry = add_labeled_entry("Lower Range Value (LRV):")
urv_entry = add_labeled_entry("Upper Range Value (URV):")
res_var = tk.StringVar(value="16")
ttk.Label(input_frame, text="A/D Resolution:").grid(row=row_idx, column=0, sticky="e", pady=2)
res_combo = ttk.Combobox(input_frame, textvariable=res_var, values=["12", "14", "16", "24"], state="readonly")
res_combo.grid(row=row_idx, column=1, sticky="ew", pady=2)
row_idx += 1

eng_entry = add_labeled_entry("Engineering Value:")
raw_entry = add_labeled_entry("Raw Count:")

# Outputs
result_var = tk.StringVar()
ttk.Label(input_frame, text="Result:").grid(row=row_idx, column=0, sticky="e", pady=4)
result_label = ttk.Label(input_frame, textvariable=result_var, font=("Segoe UI", 10))
result_label.grid(row=row_idx, column=1, sticky="w", pady=4)
row_idx += 1

voltage_var_display = tk.StringVar()
add_labeled_entry("Calculated Voltage:", voltage_var_display)
ma_var_display = tk.StringVar()
add_labeled_entry("Calculated Current:", ma_var_display)
percent_var_display = tk.StringVar()
add_labeled_entry("Percent of Span:", percent_var_display)

input_frame.columnconfigure(1, weight=1)
frame.columnconfigure(1, weight=1)

root.update_idletasks()
root.geometry(f"{frame.winfo_reqwidth()+20}x{frame.winfo_reqheight()+20}")
root.mainloop()