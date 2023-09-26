import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from PIL import Image, ImageTk
from io import BytesIO

class DeckApp:
    def __init__(self, root):
        self.root = root
        self.deck_data = []  # List to store (card_name, quantity) pairs from user input
        self.grade_data = {}  # Dictionary to store card grades
        self.root.title("Deck Tool")
        self.init_ui()
        self.deck_data = []  # Clear the deck data


    def load_card_grades(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.card_grades_file = file_path
        with open('card_grades.csv', 'r') as grade_file:
                for line in grade_file:
                    card, grade = line.strip().split(';')
                    self.grade_data[card] = grade
            


    def convert_grade(self, grade):
        # Define your grade to GPA mapping
        grade_to_gpa = {
            'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F+': 0.3, 'F': 0.0, 'F-': -0.3
        }

        if grade.startswith('BA '):
            grade = grade[3:]  # Remove 'BA ' prefix

        return grade_to_gpa.get(grade)

    def get_card_gpa(self, card_name):

        card_name = card_name.split('(', 1)[0].strip().split(' ', 1)[1]
        if card_name in self.grade_data:
            return self.convert_grade(self.grade_data[card_name])
        return -1
    def get_card_quantity(self, card_name):
        

        card_name = card_name[2:]
        for card, quantity in self.deck_data:
            if card == card_name:
                return quantity
        return 0

    def calculate_average_and_show_deck(self):
        self.deck_data = []  # Clear the deck data
        input_data = self.text_entry.get("1.0", "end-1c")

        for line in input_data.split('\n'):
            parts =  line.split('(', 1)[0].strip().split()
            if len(parts) > 1:
                quantity = int(parts[0])
                card_name = ' '.join(parts[1:])
                self.deck_data.append((card_name, quantity))

        total_gpa = 0.0
        total_cards = 0

        # Calculate GPA based on card grades and quantities
        for card_name, quantity in self.deck_data:
            if card_name in self.grade_data:
                grade = self.grade_data[card_name]
                gpa = self.convert_grade(grade)
                total_gpa += gpa * quantity
                total_cards += quantity

        average_gpa = total_gpa / total_cards if total_cards > 0 else 0.0
        self.result_label.config(text=f"Average GPA: {average_gpa:.2f}")

        self.show_deck()

    def fetch_card_image(self, card_name):
        card_name = card_name.split('(', 1)[0].strip().split(' ', 1)[1]
        base_url = "https://api.scryfall.com/cards/named"
        params = {
            "exact": card_name
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        image_url = data.get('image_uris', {}).get('normal', None)
        if image_url:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                image_data = response.raw.read()
                card_image = Image.open(BytesIO(image_data))
                card_image = card_image.resize((120, 168), Image.LANCZOS)
                return ImageTk.PhotoImage(card_image)
        return None

    def show_deck(self):
        decklist = self.text_entry.get("1.0", "end-1c").splitlines()
        self.clear_card_frame()

        row, col = 0, 0
        for card_name in decklist:
            card_image = self.fetch_card_image(card_name)
            if card_image:
                card_frame = tk.Frame(self.card_frame)
                card_frame.grid(row=row, column=col, padx=1, pady=1)

                # Create a label to display the GPA
                card_gpa_label = tk.Label(card_frame, text=f"GPA: {self.get_card_gpa(card_name):.2f} | Qty: {self.get_card_quantity(card_name)}")
                card_gpa_label.pack()

                # Display the card image
                card_label = tk.Label(card_frame, image=card_image)
                card_label.image = card_image
                card_label.pack()

                col += 1
                if col >= 10:  # Set the number of columns per row
                    col = 0
                    row += 1


    def clear_card_frame(self):
        for widget in self.card_frame.winfo_children():
            widget.destroy()

    def init_ui(self):
        # Create frames for sidebar and content
        sidebar_frame = tk.Frame(self.root, bg="lightgray")
        content_frame = tk.Frame(self.root)

        # Create a button to load card grades from a file
        load_grades_button = tk.Button(sidebar_frame, text="Load Card Grades", command=self.load_card_grades)
        load_grades_button.grid(row=4, column=0, pady=5)

        # Create widgets for sidebar_frame
        text_label = tk.Label(sidebar_frame, text="Enter your decklist:")
        self.text_entry = tk.Text(sidebar_frame, height=10, width=30)
        calculate_button = tk.Button(sidebar_frame, text="Calculate GPA & Show Deck", command=self.calculate_average_and_show_deck)
        self.result_label = tk.Label(sidebar_frame, text="")

        # Place widgets inside sidebar_frame using grid
        text_label.grid(row=0, column=0, pady=10)
        self.text_entry.grid(row=1, column=0, pady=5)
        calculate_button.grid(row=2, column=0, pady=5)
        self.result_label.grid(row=3, column=0, pady=5)

        # Place the sidebar on the left and expand the content frame on the right
        sidebar_frame.grid(row=0, column=0, sticky="ns")
        content_frame.grid(row=0, column=1, sticky="nsew")

        # Configure grid weights for content_frame to allow it to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Create the card_frame inside the content_frame
        self.card_frame = tk.Frame(content_frame)
        self.card_frame.pack(fill="both", expand=True)

        # Configure the content_frame to expand horizontally and vertically
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)



if __name__ == "__main__":
    root = tk.Tk()
    app = DeckApp(root)
    root.mainloop()
