import os
import json
from gtts import gTTS
import speech_recognition as sr
from tkinter import *
from playsound import playsound
from fpdf import FPDF
import qrcode

# Define questions and their corresponding keys
QUESTIONS = {
    "name": "What is your full name?",
    "date_of_birth": "What is your date of birth? (Please provide in DD/MM/YYYY format)",
    "country": "Which country do you currently live in?",
    "city": "Which city do you currently live in?",
    "phone": "What is your phone number, including the country code?",
    "email": "What is your email address?",
    "github": "Do you have a GitHub profile or portfolio link you’d like to include?",
    "linkedin": "Do you have a LinkedIn profile you’d like to share?",
    "education": "What is your highest degree and the name of your university/college?",
    "school": "Which school did you attend for your XII (12th grade)?",
    "experience": "Have you had any internships or job experiences? If yes, mention your position, company, and duration.",
    "responsibilities": "Have you held any leadership positions in college, clubs, or organizations? Please describe.",
    "projects": "Have you worked on any academic or personal projects? Provide the title and a brief description.",
    "achievements": "Have you received any certifications or participated in any competitions? If yes, please specify.",
    "qr_code": "Would you like to include a QR code linking to your LinkedIn profile? (Yes/No)"
}

# Function to convert text to speech and play it
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("question.mp3")
        playsound("question.mp3")
        os.remove("question.mp3")  # Delete the audio file after playing
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Function to capture speech and convert it to text
def speech_to_text():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
            audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds
            print("Processing...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.UnknownValueError:
                print("Sorry, I could not understand what you said.")
                return None
            except sr.RequestError as e:
                print(f"Sorry, there was an issue with the speech recognition service: {e}")
                return None
    except Exception as e:
        print(f"Error accessing the microphone: {e}")
        return None

# Function to ask questions and store responses
def collect_responses():
    responses = {}
    for key, question in QUESTIONS.items():
        # Ask the question using TTS
        print(f"Question: {question}")
        text_to_speech(question)

        # Wait for the user's response and capture it using STT
        response = speech_to_text()
        if response:
            responses[key] = response
        else:
            responses[key] = "Not provided"

    # Save responses to a JSON file
    with open("responses.json", "w") as f:
        json.dump(responses, f, indent=4)
    print("Responses saved to responses.json")

    # Generate CV after collecting responses
    create_cv('cv.pdf')

# PDF Class for CV Generation
class PDF(FPDF):
    def header(self):
        if os.path.exists('profile.jpg'):
            self.image('profile.jpg', x=10, y=10, w=25)
        
        self.set_font("Arial", style="B", size=14)
        self.cell(0, 10, "YOUR NAME", ln=True, align="C")
        self.set_font("Arial", style="I", size=10)
        self.cell(0, 8, "C++, Python, AI, Machine Learning", ln=True, align="C")
        self.ln(5)
        
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-10)
        self.set_font("Arial", style="I", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Arial", style="B", size=12)
        self.cell(0, 7, title, ln=True)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def section_content(self, content):
        self.set_font("Arial", size=10)
        self.multi_cell(0, 6, content)
        self.ln(3)

    def add_hyperlink(self, text, url):
        self.set_text_color(0, 0, 255)
        self.set_font("Arial", style="U", size=10)
        self.write(5, text, url)
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", size=10)
        self.ln(4)

    def add_qr_code(self, url, filename):
        qr = qrcode.make(url)
        qr.save(filename)
        self.image(filename, x=170, y=250, w=25)
        os.remove(filename)

# Function to generate CV from responses
def create_cv(output_pdf):
    pdf = PDF()
    pdf.add_page()

    # Load responses from JSON
    with open("responses.json") as f:
        data = json.load(f)

    # Map responses to CV sections
    cv_data = {
        "Education": data.get("education", "Not provided"),
        "Experience": data.get("experience", "Not provided"),
        "Projects": data.get("projects", "Not provided"),
        "Responsibilities": data.get("responsibilities", "Not provided"),
        "Achievements": data.get("achievements", "Not provided"),
        "Contact": {
            "Email": data.get("email", "Not provided"),
            "GitHub": data.get("github", "Not provided"),
            "LinkedIn": data.get("linkedin", "Not provided")
        }
    }

    # Add sections to PDF
    for section, content in cv_data.items():
        pdf.section_title(section.upper())
        if isinstance(content, dict):
            for label, link in content.items():
                pdf.add_hyperlink(f"{label}: {link}\n", link)
                if label == "LinkedIn":
                    pdf.add_qr_code(link, "linkedin_qr.png")
        else:
            pdf.section_content(content)

    # Save the PDF
    pdf.output(output_pdf)
    print(f"CV saved to {output_pdf}")

# Create the main Tkinter window
def create_gui():
    root = Tk()
    root.title("CV Maker for Blind People")

    # Create a label for instructions
    label = Label(root, text="Click the button below to start answering questions.")
    label.pack(pady=20)

    # Create a button to start the process
    button = Button(root, text="Start", command=collect_responses)
    button.pack(pady=30)

    # Run the Tkinter event loop
    root.mainloop()

# Main function
if _name_ == "_main_":
    create_gui()