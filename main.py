"""
Author: Jonathan Ransbottom
Date: 01/21/2025
Version: v1.0.0
Python Version: 3.13.1
Description:
        This is the Parts Inventory desktop application. The application is used to
        manage each parts inventory to better provide accountablility for company owned parts.
        Each employee is responsible for his/her parts inventory and providing a random accessment of their
        parts monthly. This application will provide a place to enter part number, quantity, and description.
        Employees can search their inventory by using the search function and export the entire database to excel.
        They can also utilize an existing excel spreadsheet to import their parts inventory following the proper
        table format (Part, Quantity, Description).
"""

####################################################################################################
# Import module functions.
import tkinter as tk
from tkinter import *
from tkinter import messagebox  # This will allow us to display message boxes.
from tkinter import filedialog, ttk

import customtkinter
import pandas as pd  # This will allow us to use the pandas module for data manipulation such as exporting to excel. Also installed openpyxl.
from customtkinter import *
from PIL import Image, ImageTk

import database

####################################################################################################
########### Creating color pallette in case I want to use them. ####################################

# Default colors.
color_def1 = "#ffffff"
color_def2 = "#000000"
color_def3 = "lightgray"
color_def4 = "silver"
# Most used colors.
color_1 = "#6a6262"  # background color for main window and behind button/text
color_2 = "#4b3b47"  # background color header
color_3 = "#9c9990"  # background color for treeview odd rows
color_4 = "#e0d8de"  # Button hover color light orange
color_5 = "#cfd2b2"  # used a lot on button bg and fg colors


####################################################################################################
########### Creating the Window Frame ##############################################################
root = tk.Tk()
root.geometry("900x600+300+250")  # This will set the size of the window.
root.configure(bg=color_1)
root.resizable(0, 0)  # This will make the window non-resizable.
root.title("Parts Inventory Application")  # This will set the title of the window.
root.iconbitmap("assets/images/pyspider73.ico")  # Windows Icon
root.protocol("WM_DELETE_WINDOW", lambda: None)  # This will disable the close button.

####################################################################################################
########### Creating fonts in case I want to use them. #############################################
# ****************************************************************************************************
font_1 = customtkinter.CTkFont(family="Arial", size=36, weight="bold")
font_2 = customtkinter.CTkFont(family="Arial", size=12, weight="bold")
font_3 = customtkinter.CTkFont(family="Arial", size=18, weight="bold")
font_4 = customtkinter.CTkFont(family="Arial", size=14, weight="bold")
font_5 = customtkinter.CTkFont(family="Arial", size=20, weight="bold")
font_6 = customtkinter.CTkFont(family="Arial", size=16, weight="normal", slant="italic")
font_7 = customtkinter.CTkFont(family="Arial", size=16, weight="bold")


####################################################################################################
########### Functions for Buttons ##################################################################
####################################################################################################

# Define the Add New Button on side frame.


def insert():
    part_number = part_numberEntry.get()
    quantity = quantityEntry.get()
    description = descriptionEntry.get()
    if not (part_number and quantity and description):
        messagebox.showerror("Error", "All fields are required")
    elif database.part_numbers_exists(part_number):
        messagebox.showerror("Error", "Part number already exists.")
    else:
        try:
            part_number_value = str(part_number)
            database.insert_part_numbers(part_number_value, quantity, description)
            tree.delete(*tree.get_children())
            add_to_treeview()
            messagebox.showinfo("Success", "Data has been inserted.")
        except TypeError:
            messagebox.showerror("Error", "Part Number should be an integer.")


####################################################################################################
# Define the Update Button on side frame.


def update_inventory():
    selected_item = tree.focus()
    if selected_item is None:
        messagebox.showerror("Error", "Choose a part to update.")
    else:
        part_number = part_numberEntry.get()
        quantity = quantityEntry.get()
        description = descriptionEntry.get()
        if not (part_number and quantity and description):
            messagebox.showerror("Error", "All fields are required")
        else:
            try:
                part_number_value = str(part_number)
                database.update_inventory(part_number_value, quantity, description)
                tree.delete(*tree.get_children())
                add_to_treeview()
                messagebox.showinfo("Success", "Data has been updated.")
            except ValueError:
                messagebox.showerror("Error", "Part Number should be a string.")


####################################################################################################
# Define the Clear Button.


def clear(*clicked):
    if clicked:
        tree.selection_remove(tree.focus(""))
        part_numberEntry.delete(0, END)
        quantityEntry.delete(0, END)
        descriptionEntry.delete(0, END)


####################################################################################################
# Define the Search Button.


def search_part_numbers():
    if searchEntry.get() == "":
        messagebox.showerror("Error", "Enter value to search")
    elif searchBox.get() == "Search by":
        messagebox.showerror("Error", "Please select an option")
    else:
        search_by = searchBox.get()
        search_value = searchEntry.get()

        # Map display values to actual column names
        column_map = {
            "Part Number": "part_number",
            "Description": "description",
            "Quantity": "quantity",
        }

        search_by_column = column_map.get(search_by)
        print(f"Searching by: {search_by_column}, Value: {search_value}")  # Debug print
        searched_inventory = database.search(search_by_column, search_value)
        print(f"Search results: {searched_inventory}")  # Debug print

        # Clear the treeview
        tree.delete(*tree.get_children())

        # Insert the search results into the treeview
        for part in searched_inventory:
            tree.insert("", END, values=part)


####################################################################################################
# Define the Show All Button.


def show_all():
    add_to_treeview()
    searchEntry.delete(0, END)
    searchEntry.insert(0, "")
    searchBox.set("Search By")


####################################################################################################
# Define the Export to Excel Button.


def export():
    part_numbers = database.fetch_inventory()
    if not part_numbers:
        messagebox.showerror("Error", "No data available to export.")
        return

    df = pd.DataFrame(part_numbers, columns=["Part Number", "Quantity", "Description"])
    file_path = (
        filedialog.asksaveasfilename(  # Ask user to save file and where to save it.
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="parts_inventory.xlsx",
            initialdir="~/Desktop",
        )
    )
    if not file_path:
        return
    try:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {e}")


####################################################################################################
# Define the Import from Excel Button.


def import_data():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            part_number = row["Part Number"]
            quantity = row["Quantity"]
            description = row["Description"]
            if not database.part_numbers_exists(part_number):
                database.insert_part_numbers(part_number, quantity, description)
        add_to_treeview()
        messagebox.showinfo("Success", "Data imported successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import data: {e}")


####################################################################################################
# Define the DELETE Button.


def delete():
    """
    Deletes the selected part from the database.
    """
    selected_items = tree.selection()
    print(f"Selected items: {selected_items}")  # Debugging statement
    if not selected_items:
        messagebox.showerror("Error", "Choose a part to delete.")
    else:
        values = tree.item(selected_items[0]).get("values", [])
        print(f"Values: {values}")  # Debugging statement
        if not values:
            messagebox.showerror("Error", "Selected item has no values.")
        else:
            part_number = values[0]
            try:
                part_number_value = str(part_number)
                database.delete_inventory(part_number_value)
                tree.delete(selected_items[0])  # Remove the item from the tree view
                tree.delete(*tree.get_children())  # Clear the treeview
                add_to_treeview()  # Refresh the treeview
                messagebox.showinfo("Success", "Part deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete part: {e}")


####################################################################################################
# Define the DELETE ALL Button.


def deleteAll():
    print("DELETE ALL function called")
    confirm = messagebox.askyesnocancel(
        title="Delete All Inventory",
        message="Are you sure you want to DELETE ALL INVENTORY in the DATABASE? \nThis action cannot be undone!!!",
    )
    if confirm:
        database.delete_all_inventory()
        add_to_treeview()
        tree.delete(*tree.get_children())
        messagebox.showinfo("Info", "All Parts Deleted")
    elif confirm is None:
        print("Action cancelled")
    else:
        print("No action taken")


####################################################################################################
########## Top Frame ###############################################################################

####################################################################################################
# This will create a frame for the top frame.
root.topFrame = Frame(root, bg=color_2)
root.topFrame.place(x=0, y=0, width=900, height=90)

textLable = Label(
    root.topFrame,
    text="Parts Inventory",
    font=(font_1),
    bg=color_2,
    fg=color_def1,
)
textLable.place(x=20, y=10)

textLable = Label(
    root.topFrame,
    text="Parts Inventory Management Application",
    font=(font_6),
    bg=color_2,
    fg=color_5,
)
textLable.place(x=20, y=60)

####################################################################################################
# This will create a button 'Logout' to Logout of the window.

logout24 = customtkinter.CTkImage(Image.open("assets/images/logout24.png"))

root.logoutLink = customtkinter.CTkButton(
    root.topFrame,
    text_color=color_def1,
    bg_color=color_2,
    fg_color=color_2,
    hover_color=color_2,  # Set the hover color for the button
    width=20,
    height=4,
    image=logout24,
    compound=tk.LEFT,
    cursor="hand2",
    text="Logout",
    font=(font_5),
    command=root.quit,  # Used to close the program for "Logout".
)

root.logoutLink.place(x=785, y=25)

####################################################################################################
######### END OF MAIN WINDOW #######################################################################
####################################################################################################

####################################################################################################
#########  midFrame1 ###############################################################################
####################################################################################################

root.midFrame1 = customtkinter.CTkFrame(
    root,
    bg_color=color_1,
    fg_color=color_5,
    corner_radius=10,
    border_width=4,
    border_color=color_2,
    width=400,
    height=130,
)

####################################################################################################
####### Text Fields Labels #########################################################################
####################################################################################################

textLable = Label(
    root.midFrame1,
    text="Part Number",
    font=(font_2),
    bg=color_5,
    fg=color_def2,
)
textLable.place(x=10, y=5)

textLable = Label(
    root.midFrame1,
    text="Quantity",
    font=(font_2),
    bg=color_5,
    fg=color_def2,
)
textLable.place(x=120, y=5)

textLable = Label(
    root.midFrame1,
    text="Description",
    font=(font_2),
    bg=color_5,
    fg=color_def2,
)
textLable.place(x=200, y=5)


####################################################################################################
####### Text Entry Fields ##########################################################################

#################################################################################################
# This is the Part Entry.

part_numberEntry = entry = customtkinter.CTkEntry(
    root,
    width=100,
    height=28,
    bg_color=color_5,
    fg_color=color_def1,
    text_color=color_def2,
)
entry.place(x=30, y=125)

#################################################################################################
# This is the Quantity Entry.

quantityEntry = entry = customtkinter.CTkEntry(
    root,
    width=70,
    height=28,
    bg_color=color_5,
    fg_color=color_def1,
    text_color=color_def2,
)
entry.place(x=140, y=125)

#################################################################################################
# This is the Description Entry.

descriptionEntry = entry = customtkinter.CTkEntry(
    root,
    width=190,
    height=28,
    bg_color=color_5,
    fg_color=color_def1,
    text_color=color_def2,
)
entry.place(x=220, y=125)


root.midFrame1.place(
    x=20,
    y=100,
)

####################################################################################################
####### Buttons ####################################################################################

####################################################################################################
# This is the Add New Button.

root.addLink = customtkinter.CTkButton(
    root.midFrame1,
    corner_radius=50,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Add New",
    font=(font_3),
    command=lambda: (insert(), clear(True)),
)

root.addLink.place(x=30, y=60)

####################################################################################################
# This is the Update Button.

root.updateLink = customtkinter.CTkButton(
    root.midFrame1,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Update",
    font=(font_3),
    command=lambda: (update_inventory(), clear(True)),
    # This will update the fields and then clear the text fields after button pressed.
)

root.updateLink.place(x=140, y=60)


####################################################################################################
# This is the Clear Button.

root.clearLink = customtkinter.CTkButton(
    root.midFrame1,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    width=210,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Clear Fields",
    font=(font_3),
    command=lambda: clear(True),
)

root.clearLink.place(x=30, y=95)

####################################################################################################
# This is the Delete Button.

root.deleteLink = customtkinter.CTkButton(
    root.midFrame1,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Delete",
    font=(font_3),
    command=lambda: (delete(), clear(True)),
)

root.deleteLink.place(x=260, y=60)

####################################################################################################
# This is the Delete All Button.

root.deleteAllLink = customtkinter.CTkButton(
    root.midFrame1,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Delete All",
    font=(font_3),
    command=lambda: (deleteAll(), clear(True)),
)

root.deleteAllLink.place(x=260, y=95)

####################################################################################################
#########  midFrame2 ###############################################################################
####################################################################################################

root.midFrame2 = customtkinter.CTkFrame(
    root,
    bg_color=color_1,
    fg_color=color_5,
    corner_radius=10,
    border_width=4,
    border_color=color_2,
    width=400,
    height=130,
)


root.midFrame2.place(
    x=475,
    y=100,
)

####################################################################################################
# This is the Search Label.

textLable = Label(
    root.midFrame2,
    text="Search Inventory",
    font=(font_7),
    bg=color_5,
    fg=color_def2,
)
textLable.place(x=80, y=15)


####################################################################################################
# This is the Search ComboBox.


def search_by_part_number(part_number):
    return database.search("part_number", part_number)


def search_by_description(description):
    return database.search("description", description)


search_options = {
    "Part Number": search_by_part_number,
    "Description": search_by_description,
}

searchBox = customtkinter.CTkComboBox(
    root.midFrame2,
    width=120,
    height=28,
    bg_color=color_5,
    fg_color=color_def1,
    text_color=color_def2,
    values=list(search_options.keys()),
    state="readonly",
)
searchBox.set("Search by:")  # Set default value
searchBox.place(
    x=10,
    y=45,
)

####################################################################################################
# This is the Search Entry.

searchEntry = entry = customtkinter.CTkEntry(
    root.midFrame2,
    placeholder_text="",
    placeholder_text_color=color_def2,
    width=130,
    height=28,
    bg_color=color_5,
    fg_color=color_def1,
    text_color=color_def2,
)
entry.place(
    x=140,
    y=45,
)

####################################################################################################
# This is the Search Button.

root.searchButton = customtkinter.CTkButton(
    root.midFrame2,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Search",
    font=(font_3),
    command=lambda: search_part_numbers(),
)

root.searchButton.place(x=30, y=80)


####################################################################################################
# This is the Search All Button.

root.showAllButton = customtkinter.CTkButton(
    root.midFrame2,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Show All",
    font=(font_3),
    command=lambda: (
        show_all(),
        clear(True),
    ),  # This will update the fields and then clear the text fields after button pressed.
)

root.showAllButton.place(x=140, y=80)

####################################################################################################
# This is the Excel Functions Label.

textLable = Label(
    root.midFrame2,
    text="Excel Functions",
    font=(font_7),
    bg=color_5,
    fg=color_def2,
)
textLable.place(x=265, y=15)

####################################################################################################
# This is the Export to Excel Button.

root.exportLink = customtkinter.CTkButton(
    root.midFrame2,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    # corner_radius=30,
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    cursor="hand2",
    text="Export",
    font=(font_3),
    command=lambda: (export(), clear(True)),
)

root.exportLink.place(x=280, y=45)


####################################################################################################
# This is the Import from Excel Button.

root.importLink = customtkinter.CTkButton(
    root.midFrame2,
    text_color=color_def2,
    bg_color=color_5,
    fg_color=color_4,
    hover_color=color_def3,  # Set the hover color for the button
    width=100,
    height=4,
    border_color=color_2,
    border_width=2,
    # corner_radius=30,  # Set the corner radius for the button
    cursor="hand2",
    text="Import",
    font=(font_3),
    command=lambda: (import_data(), clear(True)),
)

root.importLink.place(x=280, y=80)


####################################################################################################
####################################################################################################
# Begin building the table. This will create a treeview for the Inventory List. ####################
####################################################################################################


####################################################################################################
# Define the treeview function.
def add_to_treeview():
    part_numbers = database.fetch_inventory()
    tree.delete(*tree.get_children())
    for part_number in part_numbers:
        tree.insert("", END, values=part_number)


def display_data_from_tree(event: None):
    selected_item = tree.focus()
    if selected_item:
        row = tree.item(selected_item)["values"]
        clear(True)
        part_numberEntry.insert(0, row[0])
        quantityEntry.insert(0, row[1])
        descriptionEntry.insert(0, row[2])
    else:
        pass


####################################################################################################
# Begin treeview.
####################################################################################################
style = ttk.Style()
# Pick a theme.
style.theme_use("clam")

# Configure treeview colors.
style.configure(
    "Treeview.Heading",
    font=(font_4),
    foreground=color_2,
    background=color_5,
    fieldbackground=color_3,
)

style.configure(
    "Treeview",
    foreground=color_def1,
    fieldbackground=color_5,
    background=(["selected", color_3]),
)
style.map("Treeview", background=[("selected", "green")])

tree = ttk.Treeview(
    root,
    height=15,
    column=(
        "Part Number",
        "Quantity",
        "Description",
    ),
    show="headings",
)

tree.tag_configure("oddrow", background=color_3)
tree.tag_configure("evenrow", background=color_2)


# Insert parts into the treeview with alternating row colors
def add_to_treeview():
    part_numbers = database.fetch_inventory()
    tree.delete(*tree.get_children())
    for index, part_numbers in enumerate(part_numbers):
        if index % 2 == 0:
            tree.insert("", END, values=part_numbers, tags=("evenrow",))
        else:
            tree.insert("", END, values=part_numbers, tags=("oddrow",))


tree.heading("#1", text="Part Number")
tree.heading("#2", text="Quantity")
tree.heading("#3", text="Description")

tree.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
tree.column("#1", width=120, anchor="nw")
tree.column("#2", width=80, anchor="center")
tree.column("#3", width=400, anchor="nw")


add_to_treeview()

####################################################################################################

####################################################################################################
# Sets the Scrollbar.
scrollbar = ttk.Scrollbar(
    root,
    orient=tk.VERTICAL,
    command=tree.yview,
)
scrollbar.place(x=737, y=278, height=300)
tree.configure(yscrollcommand=scrollbar.set)

tree.place(
    x=150,
    y=250,
)

tree.bind("<ButtonRelease>", display_data_from_tree)


root.mainloop()
