
import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Student Placement Tracker",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Placement Tracker")
st.write("Manage student records and track placement eligibility.")

# Store records in a CSV file
FILE = "students.csv"

columns = ["Name", "USN", "Department", "CGPA", "Backlogs", "Eligible"]

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=columns)

# Sidebar menu

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Search Student",
        "Import Dataset",
        "Edit Student",
        "Delete Student"
    ]
)
# Dashboard page
if page == "Dashboard":
    st.header("📊 Dashboard Overview")

    total = len(df)

    if total > 0:
        eligible = int(df["Eligible"].astype(str).str.lower().isin(["true", "1"]).sum())
        average_cgpa = pd.to_numeric(df["CGPA"], errors="coerce").mean()
        placement_rate = (eligible / total) * 100
    else:
        eligible = 0
        average_cgpa = 0
        placement_rate = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total)
    col2.metric("Eligible Students", eligible)
    col3.metric("Eligibility Rate", f"{placement_rate:.1f}%")
    col4.metric("Average CGPA", f"{average_cgpa:.2f}")

    st.subheader("Department-wise Student Count")

    if total > 0:
        st.bar_chart(df["Department"].value_counts())
        st.subheader("CGPA Distribution")
        st.bar_chart(df["CGPA"].value_counts().sort_index())
    else:
        st.info("No student records yet. Add students to see dashboard charts.")

# Add student page
elif page == "Add Student":
    st.header("➕ Register a Student")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        usn = st.text_input("USN")
        department = st.selectbox(
            "Department",
            ["ISE", "CSE", "ECE", "EEE", "ME", "Civil", "Other"]
        )
        cgpa = st.number_input(
            "CGPA",
            min_value=0.0,
            max_value=10.0,
            value=7.0,
            step=0.1
        )
        backlogs = st.number_input(
            "Active Backlogs",
            min_value=0,
            step=1
        )

        submitted = st.form_submit_button("Save Student")

    if submitted:
        if not name.strip() or not usn.strip():
            st.error("Please enter both student name and USN.")
        elif df["USN"].astype(str).str.strip().str.lower().eq(usn.strip().lower()).any():
            st.error("This USN already exists.")
        else:
            eligible = cgpa >= 7.0 and backlogs == 0

            new_student = pd.DataFrame([{
                "Name": name.strip(),
                "USN": usn.strip(),
                "Department": department,
                "CGPA": cgpa,
                "Backlogs": int(backlogs),
                "Eligible": eligible
            }])

            updated_df = pd.concat([df, new_student], ignore_index=True)
            updated_df.to_csv(FILE, index=False)

            st.success("Student saved successfully!")
            if eligible:
                st.success("Placement status: Eligible")
            else:
                st.warning("Placement status: Not Eligible")

# View students page
elif page == "View Students":
    st.header("👥 Student Records")

    if not df.empty:
        department_filter = st.selectbox(
            "Filter by Department",
            ["All"] + sorted(df["Department"].dropna().astype(str).unique().tolist())
        )

        filtered_df = df.copy()

        if department_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Department"] == department_filter
            ]

        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            "Download Student Records as CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="student_records.csv",
            mime="text/csv"
        )
    else:
        st.info("No students registered yet.")

# Search student page
elif page == "Search Student":
    st.header("🔍 Search Student")

    search_usn = st.text_input("Enter student USN")

    if st.button("Search"):
        if search_usn.strip():
            result = df[
                df["USN"].astype(str).str.strip().str.lower()
                == search_usn.strip().lower()
            ]

            if not result.empty:
                st.success("Student found!")
                st.dataframe(result, use_container_width=True)
            else:
                st.error("No student found with that USN.")
        else:
            st.warning("Please enter a USN.")

            
# Import dataset page
elif page == "Import Dataset":
    st.header("📂 Import Student Dataset")

    st.write("Upload a CSV or Excel file containing student records.")

    uploaded_file = st.file_uploader(
        "Choose your dataset",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                imported_df = pd.read_csv(uploaded_file)
            else:
                imported_df = pd.read_excel(uploaded_file)

            # Clean column names
            imported_df.columns = (
                imported_df.columns.astype(str).str.strip().str.lower()
            )

            # Match common column names
            imported_df = imported_df.rename(columns={
                "student name": "name",
                "student_name": "name",
                "student usn": "usn",
                "student_id": "usn",
                "roll number": "usn",
                "roll_no": "usn",
                "dept": "department",
                "branch": "department",
                "cgpa": "cgpa",
                "active backlogs": "backlogs",
                "active_backlogs": "backlogs"
            })

            required = ["name", "usn", "department", "cgpa"]

            missing = [
                column for column in required
                if column not in imported_df.columns
            ]

            if missing:
                st.error(
                    f"Missing columns: {', '.join(missing)}. "
                    "Your dataset must contain Name, USN, Department and CGPA."
                )
            else:
                if "backlogs" not in imported_df.columns:
                    imported_df["backlogs"] = 0

                imported_df["name"] = imported_df["name"].fillna("").astype(str).str.strip()
                imported_df["usn"] = imported_df["usn"].fillna("").astype(str).str.strip()
                imported_df["department"] = imported_df["department"].fillna("").astype(str).str.strip()
                imported_df["cgpa"] = pd.to_numeric(
                    imported_df["cgpa"], errors="coerce"
                )
                imported_df["backlogs"] = pd.to_numeric(
                    imported_df["backlogs"], errors="coerce"
                )

                invalid = (
                    imported_df["name"].eq("")
                    | imported_df["usn"].eq("")
                    | imported_df["department"].eq("")
                    | imported_df["cgpa"].isna()
                    | ~imported_df["cgpa"].between(0, 10)
                    | imported_df["backlogs"].isna()
                    | imported_df["backlogs"].lt(0)
                    | (imported_df["backlogs"] % 1 != 0)
                )

                clean_df = imported_df.loc[~invalid].copy()
                clean_df["backlogs"] = clean_df["backlogs"].astype(int)

                clean_df["Eligible"] = (
                    (clean_df["cgpa"] >= 7.0)
                    & (clean_df["backlogs"] == 0)
                )

                clean_df = clean_df.rename(columns={
                    "name": "Name",
                    "usn": "USN",
                    "department": "Department",
                    "cgpa": "CGPA",
                    "backlogs": "Backlogs"
                })

                clean_df = clean_df[
                    ["Name", "USN", "Department", "CGPA", "Backlogs", "Eligible"]
                ]

                st.subheader("Dataset Preview")
                st.dataframe(clean_df, use_container_width=True)

                st.write(f"Valid rows: {len(clean_df)}")
                st.write(f"Rows skipped due to invalid data: {int(invalid.sum())}")

                import_mode = st.radio(
                    "How should the dataset be imported?",
                    ["Replace existing records", "Add new records"]
                )

                if st.button("Import Dataset"):
                    if clean_df.empty:
                        st.error("There are no valid student records to import.")
                    else:
                        if import_mode == "Replace existing records":
                            final_df = clean_df.drop_duplicates(
                                subset=["USN"], keep="last"
                            )
                        else:
                            combined = pd.concat(
                                [df, clean_df], ignore_index=True
                            )
                            final_df = combined.drop_duplicates(
                                subset=["USN"], keep="last"
                            )

                        final_df.to_csv(FILE, index=False)
                        st.success(
                            f"Successfully imported {len(final_df) - len(df) if import_mode == 'Add new records' else len(final_df)} records, "
                            "with duplicate USNs resolved."
                        )
                        st.info("Open Dashboard or View Students to see the records.")

        except Exception as e:
            st.error(f"Unable to read the dataset: {e}")

            
# Edit Student page
elif page == "Edit Student":
    st.header("✏️ Edit Student Record")

    if df.empty:
        st.info("No student records available to edit.")
    else:
        selected_usn = st.selectbox(
            "Select Student USN",
            df["USN"].astype(str).tolist()
        )

        student = df[
            df["USN"].astype(str) == selected_usn
        ].iloc[0]

        with st.form("edit_student_form"):
            name = st.text_input(
                "Student Name",
                value=str(student["Name"])
            )

            usn = st.text_input(
                "USN",
                value=str(student["USN"])
            )

            departments = [
                "ISE", "CSE", "ECE", "EEE",
                "ME", "Civil", "AI&DS", "AIML", "Other"
            ]

            current_department = str(student["Department"])
            department_options = list(departments)

            if current_department not in department_options:
                department_options.append(current_department)

            department = st.selectbox(
                "Department",
                department_options,
                index=department_options.index(current_department)
            )

            cgpa = st.number_input(
                "CGPA",
                min_value=0.0,
                max_value=10.0,
                value=float(student["CGPA"]),
                step=0.1
            )

            backlogs = st.number_input(
                "Active Backlogs",
                min_value=0,
                value=int(student["Backlogs"]),
                step=1
            )

            save_changes = st.form_submit_button("Save Changes")

        if save_changes:
            if not name.strip() or not usn.strip():
                st.error("Name and USN cannot be empty.")

            elif (
                df["USN"].astype(str).str.strip().str.lower()
                .eq(usn.strip().lower()).sum()
                > int(str(student["USN"]).strip().lower() == usn.strip().lower())
            ):
                st.error("Another student already has this USN.")

            else:
                mask = df["USN"].astype(str) == selected_usn

                df.loc[mask, "Name"] = name.strip()
                df.loc[mask, "USN"] = usn.strip()
                df.loc[mask, "Department"] = department
                df.loc[mask, "CGPA"] = cgpa
                df.loc[mask, "Backlogs"] = int(backlogs)
                df.loc[mask, "Eligible"] = (
                    cgpa >= 7.0 and backlogs == 0
                )

                df.to_csv(FILE, index=False)

                st.success("Student record updated successfully!")
                st.rerun()
                
# Delete Student page
elif page == "Delete Student":
    st.header("🗑️ Delete Student Record")

    if df.empty:
        st.info("No student records available to delete.")
    else:
        selected_usn = st.selectbox(
            "Select Student to Delete",
            df["USN"].astype(str).tolist(),
            key="delete_student_usn"
        )

        student = df[
            df["USN"].astype(str) == selected_usn
        ].iloc[0]

        st.write("### Student Details")
        st.write("**Name:**", student["Name"])
        st.write("**USN:**", student["USN"])
        st.write("**Department:**", student["Department"])
        st.write("**CGPA:**", student["CGPA"])

        st.warning(
            "Deleting this record is permanent unless you have a backup."
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button("Delete Student", type="primary"):
            if confirm:
                df = df[
                    df["USN"].astype(str) != selected_usn
                ]

                df.to_csv(FILE, index=False)

                st.success("Student deleted successfully!")
                st.rerun()
            else:
                st.error("Please confirm before deleting.")




