from datetime import datetime, timedelta

from app.constants.lookups import DB_ROLE_ID, EMAIL_SUBJECTS, TIMESHEET_STATUS
from app.models.timesheets import ReminderTypeEnum, Timesheet, TimesheetReminder
from app.extensions import db
from app.models.users import User
from app.utils.helpers import sendEmailFromTemplate


def sendEmailsToDraftTimesheets():
    try:
        now = datetime.utcnow()

        if now.weekday() == 4:
            draftTimesheets = (
                db.session.query(
                    User.full_name,
                    User.email,
                    Timesheet.id,
                    Timesheet.week_start == now.date() - timedelta(days=now.weekday()),
                )
                .join(
                    Timesheet,
                    Timesheet.user_id == User.id,
                )
                .filter(
                    Timesheet.status == TIMESHEET_STATUS["DRAFT"],
                    User.role_id.in_([DB_ROLE_ID["MANAGER"], DB_ROLE_ID["EMPLOYEE"]]),

                    # FIXME: Remove the bottom lines
                    # Timesheet.status == TIMESHEET_STATUS["PARTIAL_REJECT"],
                    # User.role_id.in_([DB_ROLE_ID["SUPER_ADMIN"]]),
                )
                .all()
            )

            # for row in draftTimesheets:
            #     email_data = {"email" : row.email, "name": row.full_name}
            #     sendEmailFromTemplate("app/templates/employee_weekly_reminder.html", EMAIL_SUBJECTS["WEEKLY_REMINDER"], email_data)

            emails_sent = 0
            for ts in draftTimesheets:
                # Check if reminder already sent today
                existing_reminder = TimesheetReminder.query.filter(
                    TimesheetReminder.timesheet_id == ts.id,
                    TimesheetReminder.reminder_type == ReminderTypeEnum.GENTLE,
                    # db.func.date(TimesheetReminder.sent_at) == now.date(),
                ).first()
                if existing_reminder:
                    continue  # Skip if already sent today

                # Send email
                email_data = {"email": ts.email, "name": ts.full_name}
                sendEmailFromTemplate(
                    "app/templates/employee_weekly_reminder.html",
                    EMAIL_SUBJECTS["WEEKLY_REMINDER"],
                    email_data,
                )

                # Log reminder
                reminder = TimesheetReminder(
                    timesheet_id=ts.id, reminder_type=ReminderTypeEnum.GENTLE
                )
                db.session.add(reminder)
                emails_sent += 1

            db.session.commit()

            return {"emails_sent": emails_sent}, None

        else:
            return None, "Skipped: Not scheduled Time"

    except Exception as e:
        return None, str(e)


def sendSecondReminderToDraftTimesheets():
    try:
        now = datetime.utcnow()

        if now.weekday() == 1:
            draftTimesheets = (
                db.session.query(
                    User.full_name,
                    User.email,
                    Timesheet.id,
                    Timesheet.week_start == now.date() - timedelta(weeks=1),
                )
                .join(
                    Timesheet,
                    Timesheet.user_id == User.id,
                )
                .filter(
                    Timesheet.status == TIMESHEET_STATUS["DRAFT"],
                    User.role_id.in_([DB_ROLE_ID["MANAGER"], DB_ROLE_ID["EMPLOYEE"]]),

                    # FIXME: Remove the bottom lines
                    # Timesheet.status == TIMESHEET_STATUS["PARTIAL_REJECT"],
                    # User.role_id.in_([DB_ROLE_ID["SUPER_ADMIN"]]),
                )
                .all()
            )

            # for row in draftTimesheets:
            #     email_data = {"email" : row.email, "name": row.full_name}
            #     sendEmailFromTemplate("app/templates/employee_weekly_reminder.html", EMAIL_SUBJECTS["WEEKLY_REMINDER"], email_data)

            emails_sent = 0
            for ts in draftTimesheets:
                # Check if reminder already sent today
                existing_reminder = TimesheetReminder.query.filter(
                    TimesheetReminder.timesheet_id == ts.id,
                    TimesheetReminder.reminder_type == ReminderTypeEnum.SECOND,
                    # db.func.date(TimesheetReminder.sent_at) == now.date(),
                ).first()
                if existing_reminder:
                    continue  # Skip if already sent today

                # Send email
                email_data = {"email": ts.email, "name": ts.full_name}
                sendEmailFromTemplate(
                    "app/templates/employee_second_reminder.html",
                    EMAIL_SUBJECTS["SECOND_REMINDER"],
                    email_data,
                )

                # Log reminder
                reminder = TimesheetReminder(
                    timesheet_id=ts.id, reminder_type=ReminderTypeEnum.SECOND
                )
                db.session.add(reminder)
                emails_sent += 1

            db.session.commit()

            return {"emails_sent": emails_sent}, None

        else:
            return None, "Skipped: Not scheduled Time"

    except Exception as e:
        return None, str(e)
