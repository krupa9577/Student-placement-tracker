students = []

while True:
    print("Student placement tracker")
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Placement Statistics")
    print("5. Exit")
    choice = input("enter your choice: ")
    if choice == "1":
        print ("\n Add Student")
        Name = input("enter your name: ")  # How to take user input
        USN = input("enter your USN: ")
        Department = input("enter your department: ")
        CGPA = float(input("enter your CGPA: "))
        backlogs = int(input("Enter number of active backlogs: "))
        #How to store student information using dictionary(it will store key value pairs)
        student = {
            "Name": Name,
            "USN": USN,
            "Department": Department,
            "CGPA": CGPA,
            "backlogs": backlogs
            }
        students.append(student) #add the students to the list
        print("\nStudent Added Successfully!")
        if CGPA >= 7.0 and backlogs == 0: # How to use if,else statement for decision making
            print("Status : Eligible for placement")
        else:
            print("Not eligible for placement")
    elif choice == "2":

        print("\nStudent List")

        for student in students:
            print("Name       :", student["Name"])
            print("USN        :", student["USN"])
            print("Department :", student["Department"])
            print("CGPA       :", student["CGPA"])
            print("Backlogs   :", student["backlogs"])


    elif choice == "3":

        search_usn = input("Enter USN to search: ")

        found = False

        for student in students:
            if student["USN"] == search_usn:

                print("\nStudent Found!")
                print("Name       :", student["Name"])
                print("USN        :", student["USN"])
                print("Department :", student["Department"])
                print("CGPA       :", student["CGPA"])

                found = True
                break

        if found == False:
            print("Student not found.")

    
    elif choice == "4":

        print("\n===== Placement Statistics =====")

        total_students = len(students)

        if total_students == 0:
            print("No student records available.")

        else:
            eligible_students = 0
            total_cgpa = 0

            for student in students:
                total_cgpa = total_cgpa + student["CGPA"]

                backlogs = student.get("backlogs", 0)

                if student["CGPA"] >= 7.0 and backlogs == 0:
                    eligible_students = eligible_students + 1

            not_eligible = total_students - eligible_students

            average_cgpa = total_cgpa / total_students

            eligibility_percentage = (
                eligible_students / total_students
            ) * 100

            print("Total Students:", total_students)
            print("Eligible Students:", eligible_students)
            print("Not Eligible Students:", not_eligible)
            print("Average CGPA:", round(average_cgpa, 2))
            print(
                "Eligibility Percentage:",
                round(eligibility_percentage, 2), "%"
            )

    elif choice == "5":

        print("Thank you for using Student Placement Tracker!")
        break


    

