TIMESHEET_STATUS = {
    "DRAFT": 1,
    "PENDING_APPROVAL": 2,
    "APPROVED": 3,
    "REJECTED": 4,
    "CANCEL": 5,
    "LOCKED": 6,
    "IN_PROGRESS": 7,
    "PARTIAL_APPROVE": 8,
    "PARTIAL_REJECT": 9,
}

TIMESHEET_APPROVE_REJECT_VARIANT = {"APPROVE" "REJECT"}


ROLES = {
    "SUPER_ADMIN": "Super Admin",
    "HR": "HR",
    "MANAGER": "Manager",
    "EMPLOYEE": "Employee",
}

DB_ROLE_ID = {
    "SUPER_ADMIN":1,
    "HR":2,
    "MANAGER":3,
    "EMPLOYEE":4
}


EMAIL_SUBJECTS = {
    "WELCOME":"Welcome to Stellar IT Solutions",
    "WEEKLY_REMINDER":"Gentle Reminder: Weekly Timesheet Due",
    "SECOND_REMINDER":"Timesheet Submission Required - Action Needed",
    "THIRD_REMINDER":"Final Reminder: Submit Your Timesheet Today",
}