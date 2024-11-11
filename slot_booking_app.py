import streamlit as st
import datetime
import sqlite3
import random

# Function to create a new booking table in the database (if not exists)
def create_booking_table():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor() 
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            email TEXT,
            booking_date TEXT,
            start_time TEXT,
            end_time TEXT,
            table_number INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Function to get booked slots for a given date
def get_booked_slots(booking_date):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT start_time, end_time, table_number FROM bookings WHERE booking_date = ?", (str(booking_date),))
    booked_slots = c.fetchall()
    conn.close()
    return booked_slots

# Function to add a new booking to the database
def add_booking(name, phone, email, booking_date, start_time, end_time, table_number):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (name, phone, email, booking_date, start_time, end_time, table_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (name, phone, email, str(booking_date), start_time, end_time, table_number))
    conn.commit()
    conn.close()

# Initialize the database and create table if needed
create_booking_table()

# Title for the app
st.title("Goblin's Slot Lock")

# Add a GIF or image (optional)
st.image("https://rarest.org/wp-content/uploads/2022/06/8.-Goblin-Kissing-Trophy.webp", use_container_width=350)

# Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# If logged in, show the booking page
if st.session_state.logged_in:
    # Booking Page
    st.header(f"Hello, {st.session_state.name}, ready to book your slot?")
    
    # Date picker for booking date
    booking_date = st.date_input("Choose a booking date", min_value=datetime.date.today())

    # Get booked slots for the selected date
    booked_slots = get_booked_slots(booking_date)

    # Display available time slots
    available_times = []
    for hour in range(24):  # 24 hours, from 0 (12:00 AM) to 23 (11:00 PM)
        for minute in [0, 30]:  # Add both 00 and 30 minutes
            time_str = f"{hour % 12 if hour % 12 != 0 else 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
            available_times.append(time_str)
    start_time = st.selectbox("Select start time", available_times)
    end_time = st.selectbox("Select end time", available_times)

    # Make sure end time is after start time
    if start_time and end_time:
        start_obj = datetime.datetime.strptime(start_time, "%I:%M %p")
        end_obj = datetime.datetime.strptime(end_time, "%I:%M %p")
        if start_obj >= end_obj:
            st.error("End time must be after start time.")
            st.stop()

    # Table number selection
    table_number = st.selectbox("Choose a table number", [1, 2, 3, 4, 5, 6])

    # Check if the selected time slot is available
    slot_conflict = False
    for booked_start, booked_end, booked_table in booked_slots:
        booked_start_obj = datetime.datetime.strptime(booked_start, "%I:%M %p")
        booked_end_obj = datetime.datetime.strptime(booked_end, "%I:%M %p")

        if table_number == booked_table and (
            (start_obj >= booked_start_obj and start_obj < booked_end_obj) or
            (end_obj > booked_start_obj and end_obj <= booked_end_obj)):
            slot_conflict = True
            break

    if slot_conflict:
        st.error(f"Sorry, Table {table_number} is already booked during this time.")
    else:
        # Random funny messages for lunchtime (between 2:30 PM to 3:00 PM)
        funny_messages = [
            "Sorry, we don't accept bookings between 2:30 PM and 3:00 PM. Goblins need lunch too! :)",
            "Oops! No bookings during lunch hour! Goblins gotta eat! :)",
            "You caught us at lunch! Goblins need their rest! :)",
            "It's our lunchtime! Goblins can't book slots during this time! :)",
            "Looks like it's feeding time for the goblins! Try again later. :)",
            "Lunch hour! Goblins don't work without food! :)",
            "Goblins are off the clock for lunch! No bookings allowed. :)",
            "Sorry, we're busy goblin-ing around! Come back after lunch. :)",
            "Lunchtime break! Goblins need to recharge. Booking unavailable. :)",
            "Hush, it's nap time for the goblins! No slots available right now. :)"
        ]

        # Check if the selected time is between 2:30 PM and 3:00 PM
        if "2:30 PM" <= start_time <= "3:00 PM":
            st.warning(random.choice(funny_messages))
        else:
            # Submit button
            if st.button("Book Slot"):
                # Add booking to the database
                add_booking(st.session_state.name, st.session_state.phone, st.session_state.email, booking_date, start_time, end_time, table_number)
                st.success(f"Booking confirmed for {st.session_state.name} at Table {table_number} from {start_time} to {end_time} on {booking_date}")

# If not logged in, show the login page
else:
    # Login Page
    st.header("Please log in to book a slot!")
    
    name = st.text_input("Enter your name")
    phone = st.text_input("Enter your phone number")
    email = st.text_input("Enter your email address")

    # Register/login button
    if st.button("Register/Login"):
        if name and phone and email:
            st.session_state.name = name
            st.session_state.phone = phone
            st.session_state.email = email
            st.session_state.logged_in = True  # Set login status to True
            st.success(f"Welcome back, {name}!")
        else:
            st.error("Please enter all required fields: name, phone, and email.")
