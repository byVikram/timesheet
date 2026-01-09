
from datetime import datetime
from app.constants.lookups import DB_ROLE_ID, EMAIL_SUBJECTS, ROLES, TIMESHEET_STATUS
from app.models.timesheets import Timesheet
from app.extensions import db
from app.models.users import User
from app.utils.helpers import sendEmailFromTemplate



def sendEmailsToDraftTimesheets():
    try:

        now = datetime.utcnow()

        if now.weekday() == 4 and now.hour == 11:
            draftTimesheets = (
                db.session.query(
                    User.full_name,
                    User.email,
                ).join(
                    Timesheet, Timesheet.user_id == User.id,
                ).filter(
                    Timesheet.status == TIMESHEET_STATUS['DRAFT'],
                    User.role_id.in_([DB_ROLE_ID["MANAGER"], DB_ROLE_ID["EMPLOYEE"]]),
                ).all()
            )

            for row in draftTimesheets:
                email_data = {"email" : row.email, "name": row.full_name}
                sendEmailFromTemplate("app/templates/employee_weekly_reminder.html", EMAIL_SUBJECTS["WEEKLY_REMINDER"], email_data)

            return True, None

        else:
            return None, "Skipped: Not scheduled Time"

    except Exception as e:
        return None, str(e)
