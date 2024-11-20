import requests
from bs4 import BeautifulSoup
import time
import winsound
import os
import smtplib
from email.mime.text import MIMEText

def get_course_info(url):
    # Fetch HTML content
    response = requests.get(url)
    html_content = response.text

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract information about open classes
    open_classes = []

    for section in soup.find_all('div', class_='section delivery-f2f'):
        # Extract section details
        section_id = section.find('span', class_='section-id').text.strip()
        instructor = section.find('span', class_='section-instructor').text.strip()
        total_seats = section.find('span', class_='total-seats-count').text.strip()
        open_seats = section.find('span', class_='open-seats-count').text.strip()

        # Check if the class has open seats
        if int(open_seats) > 0:
            open_classes.append({
                'section_id': section_id,
                'instructor': instructor,
                'total_seats': total_seats,
                'open_seats': open_seats
            })

    return open_classes

def play_notification_sound():
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)  

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  

def send_email(subject, body):
    # Email configuration
    sender_email = "thelegobrick122@gmail.com"  
    receiver_email = "marissa22c@gmail.com"
    password = "bhhi yhbj kueu kfpb" 

    # Create the email content
    message = MIMEText(body)
    message["Subject"] = "Test"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == "__main__":
    class_name = "CMSC330"
    sectionId = ""
    termId = "202501"
    # URL for CMSC132 course, Spring 2023
    course_url = 'https://app.testudo.umd.edu/soc/search?courseId=MATH240&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on'

    previous_open_classes = []

    while True:
        clear_screen()
        open_classes_info = get_course_info(course_url)

        # Check for new open seats
        new_open_seats = [course for course in open_classes_info if course not in previous_open_classes]
        if new_open_seats:
            play_notification_sound()
            print("New open seats found!")
            
            # Send email notification
            subject = "New Open Seats Found!"
            body = "\n".join([f"Section ID: {course['section_id']}\nInstructor: {course['instructor']}\nTotal Seats: {course['total_seats']}\nOpen Seats: {course['open_seats']}\n" for course in new_open_seats])
            send_email(subject, body)

        # Print information about open classes
        if open_classes_info:
            for class_info in open_classes_info:
                print(f"Section ID: {class_info['section_id']}")
                print(f"Instructor: {class_info['instructor']}")
                print(f"Total Seats: {class_info['total_seats']}")
                print(f"Open Seats: {class_info['open_seats']}")
                print("\n")
        else:
            print("No open classes found.")

        previous_open_classes = open_classes_info

        # Wait for 30 seconds before fetching again
        time.sleep(30)
