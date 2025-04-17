import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
import threading

# course checker email password: rfnb bswk hgad xhyt

def get_course_info(url):
    """
    Fetches course information from the given URL.
    """
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

def send_email(subject, body):
    """
    Sends an email notification with the given subject and body.
    """
    # Email configuration
    sender_email = "umdseatalert@gmail.com"  
    receiver_email = "mastejed@gmail.com"
    password = "rfnb bswk hgad xhyt"  # app password

    # Create the email content
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def monitor_course(course_id, section_id, instructor, term_id="202501"):
    """
    Monitors a specific course and sends email notifications if open seats are found.
    """
    # Construct the course URL
    course_url = f'https://app.testudo.umd.edu/soc/search?courseId={course_id}&sectionId={section_id}&termId={term_id}&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor={instructor}&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on'

    previous_open_classes = []

    while True:
        open_classes_info = get_course_info(course_url)

        # Check for new open seats
        new_open_seats = [course for course in open_classes_info if course not in previous_open_classes]
        if new_open_seats:
            # Send email notification
            subject = f"New Open Seats for {course_id}!"
            body = "\n".join([f"Section ID: {course['section_id']}\nInstructor: {course['instructor']}\nTotal Seats: {course['total_seats']}\nOpen Seats: {course['open_seats']}\n" for course in new_open_seats])
            send_email(subject, body)
            print(f"Email sent: {subject}")

        previous_open_classes = open_classes_info

        # Wait for 30 seconds before fetching again
        time.sleep(30)

def send_periodic_status_email():
    """
    Sends an email every 3 hours with the message 'no new classes - everything still running properly'.
    """
    while True:
        time.sleep(10800)  # Wait for 3 hours (3 hours * 60 minutes * 60 seconds)
        subject = "No New Classes - Everything Still Running Properly"
        body = "No new open seats found in the last 3 hours. Everything is running properly."
        send_email(subject, body)
        print(f"Periodic email sent: {subject}")


if __name__ == "__main__":
    # Define the courses to monitor
    courses_to_monitor = [
        {"course_id": "CMSC414", "section_id": "0201", "instructor": "", "term_id": "202508"},
        {"course_id": "CMSC414", "section_id": "0301", "instructor": "", "term_id": "202508"},
        {"course_id": "CMSC436", "section_id": "0101", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0101", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0102", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0103", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0104", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0105", "instructor": "", "term_id": "202508"},
        {"course_id": "ANTH222", "section_id": "0106", "instructor": "", "term_id": "202508"},
        {"course_id": "BSST200", "section_id": "0101", "instructor": "", "term_id": "202508"}

    ]

    # Start monitoring each course in a separate thread
    threads = []
    for course in courses_to_monitor:
        thread = threading.Thread(
            target=monitor_course,
            args=(
                course["course_id"],
                course["section_id"],
                course["instructor"],
                course["term_id"]
            )
        )
        threads.append(thread)
        thread.start()

    periodic_email_thread = threading.Thread(target=send_periodic_status_email)
    periodic_email_thread.start()

    # Keep the main thread alive
    for thread in threads:
        thread.join()