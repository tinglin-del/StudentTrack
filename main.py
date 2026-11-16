
from drafter import *
from dataclasses import dataclass
from datetime import date, timedelta

set_website_title("StudentTrack")
set_site_information(
    author="Ting Lin",
    description="Track assignments",
    sources="",
    planning=["plan.pdf", "design.pdf"],
    links=[]
)
hide_debug_information()

@dataclass
class Assignment:
    """Store information about one school assignment."""
    name: str
    class_name: str
    due_date: str
    completed: bool


@dataclass
class State:
    """Store all information used by StudentTrack."""
    assignments: list[Assignment]
    classes: list[str]
    student_name: str
    selected_class: str
    show_completed: bool


def is_overdue(assignment: Assignment) -> bool:
    """Check whether an unfinished assignment is overdue."""
    if assignment.completed:
        return False

    try:
        due = date.fromisoformat(assignment.due_date)
        return due < date.today()
    except ValueError:
        return False


def navigation() -> list:
    """Create the navigation buttons used throughout the site."""
    return [
        Button("Home", "index"),
        Button("All Assignments", "all_assignments"),
        Button("Add Assignment", "add_assignment"),
        Button("Classes", "classes"),
        Button("Completed Work", "completed_work"),
        Button("Statistics", "statistics"),
        Button("Profile", "profile"),
        HorizontalRule()
    ]


@route
def index(state: State) -> Page:
    """Display the main StudentTrack dashboard."""
    completed_count = 0
    overdue_count = 0
    upcoming_count = 0

    for assignment in state.assignments:
        if assignment.completed:
            completed_count += 1
        elif is_overdue(assignment):
            overdue_count += 1
        else:
            upcoming_count += 1

    total = len(state.assignments)

    return Page(state, [
        Header("StudentTrack"),
        "Welcome, " + state.student_name + "!",
        Header("Your Dashboard", 2),
        "Total assignments: " + str(total),
        "Completed assignments: " + str(completed_count),
        "Upcoming assignments: " + str(upcoming_count),
        "Overdue assignments: " + str(overdue_count),
        HorizontalRule(),
        Header("Quick Actions", 2),
        Button("View All Assignments", "all_assignments"),
        Button("Add an Assignment", "add_assignment"),
        Button("View Statistics", "statistics"),
        HorizontalRule(),
        "Use the navigation buttons below to explore StudentTrack.",
        *navigation()
    ])


@route
def all_assignments(state: State) -> Page:
    """Display assignments and their completion status."""
    content = [
        Header("All Assignments"),
        "Selected class: " + state.selected_class,
        CheckBox("show_completed", state.show_completed),
        " Show completed assignments",
        Button("Apply Filter", "update_filter"),
        Button("Show All Classes", "show_all"),
        HorizontalRule()
    ]

    found = False

    for position, assignment in enumerate(state.assignments):
        if (state.selected_class == "All Classes"
                or assignment.class_name == state.selected_class):

            if assignment.completed and not state.show_completed:
                continue

            found = True
            content.append(Header(assignment.name, 3))
            content.append("Class: " + assignment.class_name)
            content.append("Due date: " + assignment.due_date)

            if assignment.completed:
                content.append("Status: Completed")
            elif is_overdue(assignment):
                content.append("Status: OVERDUE")
            else:
                content.append("Status: Not completed")

            if not assignment.completed:
                content.append(
                    Button(
                        "Mark Complete",
                        "mark_complete",
                        {"position": position}
                    )
                )

            content.append(
                Button(
                    "Delete",
                    "delete_assignment",
                    {"position": position}
                )
            )
            content.append(HorizontalRule())

    if not found:
        content.append("No assignments to display.")

    content.extend(navigation())
    return Page(state, content)


@route
def add_assignment(state: State) -> Page:
    """Display the form for creating a new assignment."""
    if len(state.classes) == 0:
        return Page(state, [
            Header("Add an Assignment"),
            "You need to add a class first.",
            Button("Add a Class", "classes"),
            Button("Home", "index")
        ])

    return Page(state, [
        Header("Add an Assignment"),
        "Enter the assignment name:",
        TextBox("name"),
        "Choose a class:",
        SelectBox("class_name", state.classes),
        "Enter the due date (YYYY-MM-DD):",
        TextBox("due_date", placeholder="YYYY-MM-DD"),
        Button("Save Assignment", "save_assignment"),
        Button("Cancel", "index"),
        *navigation()
    ])


@route
def save_assignment(
    state: State,
    name: str,
    class_name: str,
    due_date: str
) -> Page:
    """Validate and save a new assignment."""
    if name.strip() == "" or due_date.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            "Please enter an assignment name and due date.",
            Button("Try Again", "add_assignment")
        ])

    try:
        date.fromisoformat(due_date)
    except ValueError:
        return Page(state, [
            Header("Invalid Date"),
            "Please enter the date in YYYY-MM-DD format.",
            Button("Try Again", "add_assignment")
        ])

    new_assignment = Assignment(
        name.strip(),
        class_name,
        due_date,
        False
    )

    state.assignments.append(new_assignment)
    return index(state)


@route
def mark_complete(state: State, position: int) -> Page:
    """Mark a selected assignment as completed."""
    if 0 <= position < len(state.assignments):
        state.assignments[position].completed = True

    return all_assignments(state)


@route
def delete_assignment(state: State, position: int) -> Page:
    """Delete a selected assignment."""
    if 0 <= position < len(state.assignments):
        state.assignments.pop(position)

    return all_assignments(state)


@route
def classes(state: State) -> Page:
    """Display all classes and allow users to add classes."""
    content = [
        Header("My Classes"),
        "Your current classes:"
    ]

    for class_name in state.classes:
        content.append(
            Button(
                class_name,
                "view_class",
                {"class_name": class_name}
            )
        )

    content.extend([
        HorizontalRule(),
        Header("Add a New Class", 2),
        TextBox("new_class"),
        Button("Add Class", "save_class"),
        *navigation()
    ])

    return Page(state, content)


@route
def save_class(state: State, new_class: str) -> Page:
    """Add a new class to the student's class list."""
    new_class = new_class.strip()

    if new_class == "":
        return Page(state, [
            Header("Missing Class Name"),
            "Please enter a class name.",
            Button("Try Again", "classes")
        ])

    if new_class in state.classes:
        return Page(state, [
            Header("Class Already Exists"),
            "This class is already in your list.",
            Button("Back to Classes", "classes")
        ])

    state.classes.append(new_class)
    return classes(state)


@route
def view_class(state: State, class_name: str) -> Page:
    """Show assignments belonging to a selected class."""
    state.selected_class = class_name
    return all_assignments(state)


@route
def show_all(state: State) -> Page:
    """Reset the class filter to show every class."""
    state.selected_class = "All Classes"
    return all_assignments(state)


@route
def update_filter(state: State, show_completed: bool) -> Page:
    """Update whether completed assignments are displayed."""
    state.show_completed = show_completed
    return all_assignments(state)


@route
def completed_work(state: State) -> Page:
    """Display assignments that have been completed."""
    content = [
        Header("Completed Work"),
        "Here are your finished assignments:",
        HorizontalRule()
    ]

    found = False

    for assignment in state.assignments:
        if assignment.completed:
            found = True
            content.append(assignment.name)
            content.append("Class: " + assignment.class_name)
            content.append("Due date: " + assignment.due_date)
            content.append(HorizontalRule())

    if not found:
        content.append("You have not completed any assignments yet.")

    content.extend(navigation())
    return Page(state, content)


@route
def statistics(state: State) -> Page:
    """Display assignment totals and academic progress."""
    total = len(state.assignments)
    completed = 0
    overdue = 0

    for assignment in state.assignments:
        if assignment.completed:
            completed += 1
        elif is_overdue(assignment):
            overdue += 1

    if total > 0:
        percentage = completed / total * 100
    else:
        percentage = 0

    return Page(state, [
        Header("Assignment Statistics"),
        "Total assignments: " + str(total),
        "Completed assignments: " + str(completed),
        "Overdue assignments: " + str(overdue),
        "Completion progress: " + str(round(percentage, 1)) + "%",
        *navigation()
    ])


@route
def profile(state: State) -> Page:
    """Display the student's profile settings."""
    return Page(state, [
        Header("My Profile"),
        "Current name: " + state.student_name,
        "Enter a new name:",
        TextBox("new_name", state.student_name),
        Button("Update Name", "update_profile"),
        *navigation()
    ])


@route
def update_profile(state: State, new_name: str) -> Page:
    """Update the student's name."""
    if new_name.strip() != "":
        state.student_name = new_name.strip()

    return index(state)


# Initial website information and sample assignments
today = date.today()

initial_state = State(
    assignments=[
        Assignment(
            "Biology Lab Report",
            "Biology",
            (today + timedelta(days=2)).isoformat(),
            False
        ),
        Assignment(
            "Math Homework",
            "Math",
            (today + timedelta(days=1)).isoformat(),
            False
        ),
        Assignment(
            "Chemistry Worksheet",
            "Chemistry",
            today.isoformat(),
            True
        )
    ],
    classes=["Math", "Biology", "Chemistry"],
    student_name="Student",
    selected_class="All Classes",
    show_completed=False
)

start_server(initial_state)

