# -*- coding: utf-8 -*-

# **WELLBOT: WELL.CA'S PHARMACY CHAT BOT**

*   Includes four primary scenarios: Prescription Ordering, Prescription Management, Mediction Information Index, and Feedback/Improvement.

* The user_registration function creates a new user and stores the information in a JSON file to be later pulled by the user_Login function
* The four scenarios are connected by the main pharmacy_chatbot function that prompts the user to login or register then takes the user to the main welcome menu which calls upon the main scenario functions

**Scenario 1: Prescription Ordering**
* connected to the prescription JSON file
* uses random to generate RX numbers  
---
Includes:
* Initiate Prescription Transfer (Incoming)
> *functions:* generate_prescription_number
* Submit New Prescription
> *functions:* new_prescription, generate_random_prescription_data
* Get Drug Price
> *functions:* get_drug_price,
> * uses pandas dataframe to store drug pricing info


---

**Scenario 2: Prescription Management**
* connected to the prescription JSON file
---
Includes:
* Refill Medication
> *functions*: refill_prescription
* Check Medication Availability
> *functions*: check_availability

 > * connects to the stock pandas dataframe through the check_availability function to check if the medication the user entered is in stock. If it is the number of units available is displayed.

* Check Order Status
> *functions*: order_status
  
  > * connects to the delivery_status dictionary and JSON file to show the status of the order (pending, completed etc..)

**Scenario 3: Medication Information Index**
* connects to the OpenFDA API for medication information
* uses the fetch_medication_info function
* provides drug information for the drug the user inputs
---
Includes:
* Dosage
* Allergy
* General Information/Interactions
---

**Scenario 4: Feedback/Improvement**
* connected to the improvements and ratings JSON file (stored information for further analysis_|)
* uses VADER for sentiment analysis of reviews stored in the improvements JSON file  
* displays the polarity (postive,negative, neutral) after analysis
---
Includes:
* Need further assistance
> * email and phone number of Well.ca pharmacy for assistance
* Rate our service
> * *functions:* store_ratings
* Review our service
>* *functions*: store_improvement, analyze_sentiment
"""

import random
import pandas as pd
import requests
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

title = "WellBot: Well.ca's Pharmacy Chatbot"
border = "=" * len(title)
print(f"\n{border}\n{title}\n{border}\n")

# Load prescriptions from JSON file
def load_prescriptions():
    try:
        with open("prescriptions.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save prescriptions to JSON file
def save_prescriptions(prescriptions):
    with open("prescriptions.json", "w") as f:
        json.dump(prescriptions, f, indent=4)

def user_registration():
    username = input("Enter a username: ")
    password = input("Enter a password: ")

    # Load existing users from JSON file
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    # Check if username already exists
    if username in users:
        print("Username already exists. Please choose a different username.")
        return False

    # Store the new user's credentials
    users[username] = {"password": password, "name": username}

    # Write the updated users to the JSON file
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

    print("Registration successful!")
    return True

# User Login
def user_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Load existing users from JSON file
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Unable to load user data.")
        return False

    # Check if username and password match
    if username in users and users[username]["password"] == password:
        return True
    else:
        print("Invalid username or password.")
        return False

# Prescription Ordering
def prescription_ordering():
    global prescriptions, delivery_status
    prescriptions= {}
    def generate_prescription_number():
        return f"RX{random.randint(1000, 9999)}"

    def new_prescription(medication, dosage, instructions, refills, fax_needed, telephone_number=None):
        prescription_number = generate_prescription_number()
        prescription = {
            'prescription_number': prescription_number,
            'medication': medication,
            'dosage': dosage,
            'instructions': instructions,
            'refills': refills,
            'sending_pharmacy': 'N/A',
            'fax_needed': fax_needed,
            'telephone_number': telephone_number,
        }
        prescriptions[prescription_number] = prescription
        save_prescriptions(prescriptions)
        # Add a default delivery status for the new prescription
        delivery_status[prescription_number] = 'Pending'

    def generate_random_prescription_data():
        medication = f"Medication_{random.randint(1, 100)}"
        dosage = f"{random.randint(1, 20)}mg"
        instructions = f"Take {random.randint(1, 3)} times daily"
        refills = random.randint(0, 5)
        return medication, dosage, instructions, refills

    data = {
    'Medication': ['Amoxicillin', 'Ibuprofen', 'Lisinopril', 'Metformin', 'Levothyroxine', 'Atorvastatin', 'Amlodipine', 'Omeprazole', 'Losartan', 'Aspirin'],
    'Brand_Public': [10.0, 12.0, 15.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0],
    'Brand_Private': [8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0],
    'Brand_Manufacturer_Rebate': [1.0, 1.5, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2],
    'Generic_Public': [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0],
    'Generic_Private': [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0],
    'Generic_Manufacturer_Rebate': [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
}

    df = pd.DataFrame(data)  # Provided drug pricing data

    def get_drug_price(medication, category, medication_type):
        col_name = f'{medication_type}_{category}'
        try:
            price = df.loc[df['Medication'].str.lower() == medication.lower(), col_name].values[0]
            return price
        except IndexError:
            return None

    print("\nWelcome to the ordering prescriptions tab!")

    while True:
        print("1. Initiate Prescription Transfer (Incoming)")
        print("2. Submit New Prescription")
        print("3. Get Drug Price")
        print("4. Exit")
        choice = input("Select an option (1/2/3): ")
        if choice == '1':
            print("\nInitiate Prescription Transfer (Incoming)")
            sending_pharmacy = input("Enter the name of the sending pharmacy: ")

            # Generate a random prescription number for the incoming transfer
            prescription_number = generate_prescription_number()

            print(f"Generated Prescription Number: {prescription_number}")

            fax_needed = True  # Fax is always needed for prescription transfer
            telephone_number = input("Enter the telephone number of the sending pharmacy: ")

            # Generate random prescription data for transfer
            medication, dosage, instructions, refills = generate_random_prescription_data()
            new_prescription(medication, dosage, instructions, refills, fax_needed, telephone_number)
            print(f"Prescription {prescription_number} initiated for transfer from {sending_pharmacy}. Telephone number: {telephone_number}")

        elif choice == '2':
            medication = input("Enter the medication name: ")
            dosage = input("Enter the dosage: ")
            instructions = input("Enter the instructions: ")
            refills = input("Enter the number of refills: ")

            fax_needed = input("Fax of prescription from doctor's office needed? (y/n): ").lower() == 'y'
            telephone_number = None
            if fax_needed:
                telephone_number = input("Enter the telephone number of the doctor's office: ")

            new_prescription(medication, dosage, instructions, refills, fax_needed, telephone_number)
            if fax_needed:
                print("Prescription submitted successfully.")
            else:
                print("Prescription submission pending. Upload a picture of your prescription to your account.")

        elif choice == '3':
            medication = input("Enter the medication name: ").lower()
            category = input("Select category (Public/Private Insurance): ").title()
            medication_type = input("Select medication type (Brand/Generic): ").title()

            manufacturer_rebate = input("Do you have a manufacturer rebate? (y/n): ")
            if manufacturer_rebate.lower() == 'y':
                has_rebate = True
            else:
                has_rebate = False

            price = get_drug_price(medication, category, medication_type)

            if has_rebate and price is not None:
                manufacturer_rebate = df.loc[df['Medication'].str.lower() == medication, f'{medication_type}_Manufacturer_Rebate'].values[0]
                price -= manufacturer_rebate

            if price is not None:
                print(f"The price of {medication_type} {medication} under {category} Insurance is ${price:.2f}")
            else:
                print("Invalid input or medication not found.")
        elif choice == '4':
            break  # Exit the loop and return to the main menu
        else:
            print("Invalid choice. Please select 1, 2, 3 or 4.")

        another_action = input("Do you want to perform another action? (y/n): ")
        if another_action.lower() != "y":
            print("\nPrescription Database:")
            for prescription_number, prescription in prescriptions.items():
                print(f"Prescription Number: {prescription_number}")
                print(f"Medication: {prescription['medication']}")
                print(f"Dosage: {prescription['dosage']}")
                print(f"Instructions: {prescription['instructions']}")
                print(f"Refills: {prescription['refills']}")
                if 'sending_pharmacy' in prescription:
                    print(f"Sending Pharmacy: {prescription['sending_pharmacy']}")
                if 'fax_needed' in prescription:
                    print(f"Fax Needed: {'Yes' if prescription['fax_needed'] else 'No'}")
                if prescription.get('fax_needed') and 'telephone_number' in prescription:
                    print(f"Telephone Number: {prescription['telephone_number']}")
                print("-" * 20)
            break

# Prescription Management
def prescription_management():

    # The stock dict. match a medicine with its current stock
    stock_df = pd.DataFrame({
    'Medication': ['Amoxicillin', 'Ibuprofen', 'Lisinopril', 'Metformin', 'Levothyroxine', 'Atorvastatin', 'Amlodipine', 'Omeprazole', 'Losartan'],
    'Stock': [100, 0, 150, 120, 80, 90, 110, 130, 140]  # Set Ibuprofen to 0 for demonstration
})


    # Create a function to ask for refills of medicines (use prescription_refill dict.)
    def refill_prescription():
        prescriptions = load_prescriptions()
        orders = []
        while True:
            prescription_number = input("Please enter your prescription number: ")
            while prescription_number not in prescriptions:
                prescription_number = input("Invalid prescription number. Please try again or enter 'x' to exit WellBot: ")
                if prescription_number.lower() == 'x':
                    print("Thank you for using WellBot!")
                    return
                continue
            name = input("Please enter your full name: ")
            medicine = prescriptions[prescription_number]
            order = {
                "prescription_number": prescription_number,
                "customer": name,
                "medicine": medicine
            }
            orders.append(order)
            print(f"\nOrder Summary:\nPrescription Number: {prescription_number}\nCustomer: {name}\nMedicine: {medicine}")
            print("\nOrder placed! We will send you an email with the delivery information.")
            choice = input("\nWould you like to place another order? (y/n): ")
            if choice.lower() != 'y':
                break

    # Create a function to check if certain medicine is in stock (use stock dict.)
    def check_availability(stock_df):
        while True:
            medicine_name = input("Please enter the name of the medicine you want to check: ").capitalize()
            if medicine_name == "X":
              print("Exiting WellBot. Have a great day!")
              break
            if medicine_name not in   stock_df['Medication'].values:
              print(f"Sorry, we don't have {medicine_name} in our inventory. Please try again or enter 'x' to exit WellBot:")
              continue
            available_stock = stock_df.loc[stock_df['Medication'] == medicine_name, 'Stock'].values[0]

            if available_stock > 0:
                print(f"{medicine_name} is available, we have {available_stock} units in stock.")
            else:
                print(f"Sorry, {medicine_name} is currently out of stock.")
                # Recommend other available drugs using pandas
                available_meds = stock_df[stock_df['Stock'] > 0]['Medication'].tolist()
                if available_meds:
                  print("Here are some other available medications:")
                  for med in available_meds:
                    print(f"- {med}")
                else:
                   print("Unfortunately, we're currently out of stock for all medications.")
            choice = input("\nWould you like to check another medicine? (y/n): ")
            if choice.lower() != 'y':
                print("Thank you for using WellBot!")
                break

     # Create a function to inform about the order status of presciption number (use delivery_status dict.)
    def order_status():
        global delivery_status
        prescriptions = load_prescriptions()

        while True:
            prescription_number = input("Please enter your prescription number: ")
            if prescription_number in prescriptions:
              status = delivery_status.get(prescription_number, "Pending Delivery")
              print(f"\nThe order status for prescription number {prescription_number} is: {status}")
              prescription = prescriptions[prescription_number]
              print(f"\nPrescription Details:")
              print(f"Medication: {prescription['medication']}")
              print(f"Dosage: {prescription['dosage']}")
              print(f"Instructions: {prescription['instructions']}")
              print(f"Refills: {prescription['refills']}")
              if 'sending_pharmacy' in prescription:
                print(f"Sending Pharmacy: {prescription['sending_pharmacy']}")
              if 'fax_needed' in prescription:
                print(f"Fax Needed: {'Yes' if prescription['fax_needed'] else 'No'}")
              if prescription.get('fax_needed') and 'telephone_number' in prescription:
                print(f"Telephone Number: {prescription['telephone_number']}")

              if status in ['Canceled', 'On Hold', 'Rescheduled']:
                print('For further assistance, please contact our call center: 514 123 4567')
            else:
              print("Invalid prescription number. Please try again or enter 'x' to exit WellBot.")
              if prescription_number.lower() == 'x':
                print("Thank you for using WellBot!")
                return
            choice = input("\nWould you like to check another order? (y/n): ")
            if choice.lower() != 'y':
              break

    while True:
        print("\nPlease select an option: ")
        print("1. Refill Medication")
        print("2. Check Medication Availability")
        print("3. Check Order Status")
        print("4. Exit")

        option = input("Select the number: ")

        if option == '1':
            refill_prescription()
        elif option == '2':
            check_availability(stock_df)
        elif option == '3':
            order_status()
        elif option == '4':
            break
        else:
            print("\nInvalid option. Please choose a valid option.")

# Medication Information
def medication_information():
    def fetch_medication_info(medication_name):
        api_url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{medication_name}&limit=1"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if "results" in data and data["results"]:
                medication_info = data["results"][0]
                return medication_info
        return None
    while True:
      medication_name = input("Enter the medication name: ")
      medication_info = fetch_medication_info(medication_name)
      if medication_info:
        print(f"Medication Name: {medication_info['openfda']['brand_name'][0]}")
        print(f"Manufacturer: {medication_info['openfda']['manufacturer_name'][0]}")

        while True:
            print("\nHello and welcome, how can I help you today?")
            print("\nSelect the type of information you'd like to know:")
            print("1. Dosage Information")
            print("2. Allergy Information")
            print("3. General Information/Interactions")
            print("4. Go back to Medication Selection")
            print("5. Exit")

            info_choice = input("Enter your choice: ")

            if info_choice == "1":
                if "dosage_and_administration" in medication_info:
                    print("Dosage and Administration:")
                    for dosage in medication_info["dosage_and_administration"]:
                        print(f"  - {dosage}")
                else:
                    print("Dosage information not available.")

            elif info_choice == "2":
                if "warnings" in medication_info:
                    print("Allergy Information:")
                    for warning in medication_info["warnings"]:
                        print(f"  - {warning}")
                else:
                    print("Allergy information not available.")

            elif info_choice == "3":
                # Display general information or interactions
                if "indications_and_usage" in medication_info:
                    print("General Information:")
                    for indication in medication_info["indications_and_usage"]:
                        print(f"  - {indication}")
                else:
                    print("General information not available.")

                if "drug_interactions" in medication_info:
                    print("\nDrug Interactions:")
                    for interaction in medication_info["drug_interactions"]:
                        print(f"  - {interaction}")
                else:
                    print("Drug interactions information not available.")

            elif info_choice == "4":
                break  # Exit the medication information loop and return to main menu

            elif info_choice == "5":
                return False
            else:
                print("Invalid choice.")

            more_info = input("Would you like more info? (yes/no): ")
      if more_info.lower() == "no":
                    break

    else:
        print("Medication not found.")
        return False


# Feedback
def feedback_improvement():
    # Sentiment Analysis using VADER
    def analyze_sentiment(feedback):
        sia = SentimentIntensityAnalyzer()
        sentiment_scores = sia.polarity_scores(feedback)

        # Categorize sentiment based on compound score
        if sentiment_scores['compound'] >= 0.05:
            return "Positive"
        elif sentiment_scores['compound'] <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    def store_improvement(suggestion, sentiment):
        # Load existing improvements from JSON file
        try:
            with open("improvements.json", "r") as f:
                improvements = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            improvements = []

        # Add the new suggestion and sentiment
        feedback_data = {
            "suggestion": suggestion,
            "sentiment": sentiment
        }
        improvements.append(feedback_data)

        # Write the updated improvements to the JSON file
        with open("improvements.json", "w") as f:
            json.dump(improvements, f, indent=4)

    def store_rating(rating):
        # Load existing ratings from JSON file
        try:
            with open("ratings.json", "r") as f:
                ratings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            ratings = []

        # Add the new rating
        ratings.append(rating)

        # Write the updated ratings to the JSON file
        with open("ratings.json", "w") as f:
            json.dump(ratings, f, indent=4)
    print("Thank you for providing feedback!")
    while True:
        print("\nFeedback/Improvement Options:")
        print("1. Need further assistance (email/call pharmacy support)")
        print("2. Rate our service (1-10)")
        print("3. Review our service")
        print("4. Exit")


        feedback_choice = input("Enter your choice: ")

        if feedback_choice == "1":
            # Implement the email/call functionality here
            print("You selected: Need further assistance.")
            print("For further assistance call us toll-free at 1-866-640-3800 or send an email to pharmacysupport@well.ca")
            print('Monday-Friday: 9am - 10pm EST')
            print('Saturday: 9am - 4pm EST')
            print('Sunday: 10am - 5pm EST')
            break
        elif feedback_choice == "2":
            rating = input("How would you rate our service (1-10)? ")
            store_rating(rating)
            # You can process the rating and take actions accordingly
            print(f"You rated our service: {rating}")
            break

        elif feedback_choice == "3":
            improvement = input("How was your experience using our service? ")
            sentiment = analyze_sentiment(improvement)
            print(f"Feedback sentiment: {sentiment}")
            # Store the improvement suggestion in a JSON file
            store_improvement(improvement,sentiment)
            print("Thank you for your input!")
            break

        elif feedback_choice == "4":
            return False
            break  # Return to the welcome menu

        else:
            print("Invalid choice.")

    return True
# Main pharmacy chatbot function
def pharmacy_chatbot():
    print("Welcome to the Pharmacy Chatbot!")
    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            if user_login():
                username = input("Enter your username again for verification: ")
                break
            else:
                continue
        elif choice == "2":
            if user_registration():
                username = input("Enter your username again for verification: ")
                break
            else:
                continue
        elif choice == "3":
            print("Thank you for using the pharmacy chatbot. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please choose a valid option.")

    print(f"Welcome, {username}!")
    while True:
        print("\nWelcome menu options:")
        print("1. Medication Order")
        print("2. Prescription Management")
        print("3. Medication Information Index")
        print("4. Feedback/Improvement")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            prescription_ordering()
        elif choice == "2":
            prescription_management()
        elif choice == "3":
            medication_information()
        elif choice == "4":
            feedback_improvement()
        elif choice == "5":
            print("Thank you for using the pharmacy chatbot. Goodbye!")
            exit()
            break
        else:
            print("Invalid choice. Please choose a valid option.")

# Call the main function
pharmacy_chatbot()
