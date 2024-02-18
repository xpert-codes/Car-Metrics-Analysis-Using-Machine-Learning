import tkinter as tk
from tkinter import filedialog, Toplevel, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import folium
import webbrowser
from folium import plugins
from functools import partial
from PIL import Image, ImageTk
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.widgets import Zoom


class CSVVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CarAnalysis")
        self.root.geometry("1000x600")  # Increased window size

        # Load background image
        background_image = Image.open("bg.jpg")  # Replace with the path to your image
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Create a label to hold the background image
        background_label = tk.Label(root, image=self.background_photo)
        background_label.place(relwidth=1, relheight=1)  # Cover the entire window

        self.df = None
        self.selected_column1 = None
        self.selected_column2 = None

        # Frame for widgets
        self.frame = tk.Frame(root, bg="#ECECEC")  # Light gray background
        self.frame.pack(padx=10, pady=10)

        # Load CSV Button
        self.load_button = tk.Button(self.frame, text="Load File", command=self.load_csv, bg="#4CAF50", fg="white")
        self.load_button.grid(row=0, column=0, padx=5, pady=5)

        # Dropdown for selecting the first column
        self.column_var1 = tk.StringVar()
        self.column_dropdown1 = tk.OptionMenu(self.frame, self.column_var1, "")
        self.column_dropdown1.grid(row=0, column=1, padx=5, pady=5)

        # Dropdown for selecting the second column
        self.column_var2 = tk.StringVar()
        self.column_dropdown2 = tk.OptionMenu(self.frame, self.column_var2, "")
        self.column_dropdown2.grid(row=0, column=2, padx=5, pady=5)

        # Visualize Button
        self.visualize_button = tk.Button(self.frame, text="Visualize the Chart", command=self.visualize_data, bg="#3498db", fg="white")
        self.visualize_button.grid(row=0, column=3, padx=5, pady=5)

        # Clear Button
        self.clear_button = tk.Button(self.frame, text="Clear Plots", command=self.clear_plots, bg="#E69138", fg="white")
        self.clear_button.grid(row=0, column=4, padx=5, pady=5)

        # Check Temperature Button
        self.check_temp_button = tk.Button(self.frame, text="Check Temperature", command=self.check_temperature, bg="#E74C3C", fg="white")
        self.check_temp_button.grid(row=0, column=5, padx=5, pady=5)

        # View Map Button
        self.view_map_button = tk.Button(self.frame, text="View Car Map", command=self.view_map, bg="#2ecc71", fg="white")
        self.view_map_button.grid(row=0, column=6, padx=5, pady=5)

        # Matplotlib figures
        self.figure1, self.ax1 = plt.subplots(figsize=(8, 5))

        # Canvas for the first plot
        self.canvas1 = FigureCanvasTkAgg(self.figure1, master=self.root)
        self.canvas1.get_tk_widget().pack(side=tk.LEFT, expand=1)
        # self.canvas1.get_tk_widget().pack_propagate(False)

        # Enable pan and zoom using mpl_connect
        self.canvas1.mpl_connect("scroll_event", self.on_scroll)
        self.canvas1.mpl_connect("button_press_event", self.on_button_press)
        self.canvas1.mpl_connect("button_release_event", self.on_button_release)
        self.canvas1.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas1.get_tk_widget().bind("<Enter>", self.enter_canvas)
        self.canvas1.get_tk_widget().bind("<Leave>", self.leave_canvas)

        # Flag to track whether the mouse button is pressed
        self.mouse_button_pressed = False

        # Initialize last mouse position
        self.last_x = None
        self.last_y = None

    def on_scroll(self, event):
        if event.button == 'up':
            self.ax1.set_xlim(self.ax1.get_xlim()[0] * 1.2, self.ax1.get_xlim()[1] * 1.2)
            self.ax1.set_ylim(self.ax1.get_ylim()[0] * 1.2, self.ax1.get_ylim()[1] * 1.2)
        elif event.button == 'down':
            self.ax1.set_xlim(self.ax1.get_xlim()[0] / 1.2, self.ax1.get_xlim()[1] / 1.2)
            self.ax1.set_ylim(self.ax1.get_ylim()[0] / 1.2, self.ax1.get_ylim()[1] / 1.2)

        self.canvas1.draw()

    def on_button_press(self, event):
        if event.button == 1:  # Check if left mouse button is clicked
            self.mouse_button_pressed = True

    def on_button_release(self, event):
        if event.button == 1:
            self.mouse_button_pressed = False
            # Reset the last position when releasing the mouse button
            self.last_x = None
            self.last_y = None

    def on_mouse_move(self, event):
        if self.mouse_button_pressed and self.last_x is not None and self.last_y is not None:
            # Calculate the change in mouse position
            dx = event.x - self.last_x
            dy = event.y - self.last_y

            # Convert pixel coordinates to data coordinates
            xlim = self.ax1.get_xlim()
            ylim = self.ax1.get_ylim()
            x_data = xlim[0] - dx * (xlim[1] - xlim[0]) / self.canvas1.get_width_height()[0]
            y_data = ylim[0] - dy * (ylim[1] - ylim[0]) / self.canvas1.get_width_height()[1]

            # Update the xlim and ylim
            self.ax1.set_xlim(x_data, x_data + (xlim[1] - xlim[0]))
            self.ax1.set_ylim(y_data, y_data + (ylim[1] - ylim[0]))

            self.canvas1.draw()

        # Save the current mouse position
        self.last_x = event.x
        self.last_y = event.y


    def enter_canvas(self, event):
        # Show the cursor when entering the canvas
        self.root.config(cursor='arrow')

    def leave_canvas(self, event):
        # Show the cursor when leaving the canvas
        self.root.config(cursor='arrow')


    def load_csv(self):
        file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            columns = self.df.columns

            # Clear previous options
            self.column_dropdown1['menu'].delete(0, 'end')
            self.column_dropdown2['menu'].delete(0, 'end')

            # Add "None" option to both dropdowns
            self.column_dropdown1['menu'].add_command(label="None", command=tk._setit(self.column_var1, ""))
            self.column_dropdown2['menu'].add_command(label="None", command=tk._setit(self.column_var2, ""))

            # Add columns to the dropdowns
            for column in columns:
                self.column_dropdown1['menu'].add_command(label=column, command=tk._setit(self.column_var1, column))
                self.column_dropdown2['menu'].add_command(label=column, command=tk._setit(self.column_var2, column))

            # Set the default selection to "None"
            self.column_var1.set("")
            self.column_var2.set("")



    def visualize_data(self):
        if self.df is not None:
            self.selected_column1 = self.column_var1.get()
            self.selected_column2 = self.column_var2.get()

            self.ax1.clear()

            if self.selected_column1:
                self.ax1.scatter(self.df.index, self.df[self.selected_column1], label=self.selected_column1, color="#3498db")

            if self.selected_column2:
                self.ax1.scatter(self.df.index, self.df[self.selected_column2], label=self.selected_column2, color="#e74c3c")

            if self.selected_column1 or self.selected_column2:
                self.ax1.set_title(f"Comparison of {self.selected_column1} and {self.selected_column2}", color="#333333")
                self.ax1.set_xlabel("Index", color="#333333")
                self.ax1.set_ylabel("Values", color="#333333")
                self.ax1.legend()

                # Adjust y-axis limits based on the selected columns
                if self.selected_column1 and self.selected_column2:
                    min_value = min(self.df[self.selected_column1].min(), self.df[self.selected_column2].min())
                    max_value = max(self.df[self.selected_column1].max(), self.df[self.selected_column2].max())
                elif self.selected_column1:
                    min_value, max_value = self.df[self.selected_column1].min(), self.df[self.selected_column1].max()
                elif self.selected_column2:
                    min_value, max_value = self.df[self.selected_column2].min(), self.df[self.selected_column2].max()
                else:
                    min_value, max_value = 0, 1  # Default values if no column is selected

                self.ax1.set_ylim(min_value, max_value)

            self.canvas1.draw()

            # Enable zooming with the scroll wheel using mplcursors
            mplcursors.cursor(hover=True)





    def clear_plots(self):
        self.ax1.clear()
        self.canvas1.draw()

    def check_temperature(self):
        if self.df is not None and ' Engine coolant temperature' in self.df.columns:
            coolant_temperatures = self.df[' Engine coolant temperature']
            max_temp = coolant_temperatures.max()
            min_temp = coolant_temperatures.min()

            if max_temp > 100:
                messagebox.showinfo("Temperature Alert", "Overheating problem!", icon="error")
            elif min_temp < 60:
                messagebox.showinfo("Temperature Alert", "Low temperature.", icon="warning")
            else:
                messagebox.showinfo("Temperature Alert", "Normal temperature.", icon="info")
        else:
            messagebox.showinfo("Information", "No data or ' Engine coolant temperature' column in the dataset.")

    def view_map(self):
        if self.df is not None and ' Latitude (deg)' in self.df.columns and ' Longitude (deg)' in self.df.columns:
            latitudes = self.df[' Latitude (deg)'].tolist()
            longitudes = self.df[' Longitude (deg)'].tolist()

            # Create a folium map centered at the first location
            car_map = folium.Map(location=[latitudes[0], longitudes[0]], zoom_start=15)

            # Add a line to the map representing the car's movement
            folium.PolyLine(list(zip(latitudes, longitudes)), color='blue').add_to(car_map)

            # Add a marker for each data point
            for lat, lon in zip(latitudes, longitudes):
                folium.Marker(location=[lat, lon], popup=f"Latitude: {lat}, Longitude: {lon}").add_to(car_map)

            # Save the map to an HTML file
            map_file_path = "car_movement_map.html"
            car_map.save(map_file_path)

            # Open the HTML file in a web browser
            webbrowser.open(map_file_path)
        else:
            messagebox.showinfo("Information", "No data or ' Latitude (deg)' and ' Longitude (deg)' columns in the dataset.")


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

def main():
    root = tk.Tk()
    root.configure(bg="#ECECEC")  # Set the window background color

    # Create splash screen with background image
    splash = Toplevel(root)
    splash.title("CarAnalysis")

    # Load background image for the splash screen
    splash_bg_image = Image.open("bg.jpg")  # Replace with the path to your image
    splash_bg_photo = ImageTk.PhotoImage(splash_bg_image)

    # Create a label to hold the background image
    splash_bg_label = tk.Label(splash, image=splash_bg_photo)
    splash_bg_label.image = splash_bg_photo
    splash_bg_label.pack()

    # Add text directly on the image
    tk.Label(splash, text="CarAnalysis", font=("Helvetica", 20), fg="white", bg="green").place(relx=0.54, rely=0.5, anchor="center")
    tk.Label(splash, text="Ahmad", font=("Helvetica", 20), fg="white", bg="green").place(relx=1, rely=1, anchor="se")

    center_window(splash, 1000, 600)

    root.withdraw()


    app = CSVVisualizerApp(root)

    splash_closed = tk.StringVar()
    splash_closed.set("no")

    def close_splash():
        splash_closed.set("yes")

    splash.after(1000, close_splash)

    def check_splash():
        if splash_closed.get() == "yes":
            splash.destroy()  # Destroy the splash window
            root.deiconify()  # Show the main application window
            root.update_idletasks()  # Ensure all idle tasks are complete
            center_window(root, 1000, 600)  # Center the main window
        else:
            root.after(100, check_splash)

    root.after(100, check_splash)
    root.mainloop()

if __name__ == "__main__":
    main()
