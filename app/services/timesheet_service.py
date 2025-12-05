from datetime import datetime, timedelta
from app.constants.lookups import TIMESHEET_STATUS
from app.models import Holiday, Organization, TimesheetStatus, Timesheet
from app.models.projects import Project, Task
from app.models.timesheets import TimesheetHistory
from app.models.users import User
from app.services.common_service import getIdFromCode
from app.extensions import db
from sqlalchemy.orm import joinedload

from app.utils.helpers import paginateQuery


def getHolidays(org_id):
	try:

		orgId, error = getIdFromCode(Organization, org_id)

		if error:
			return None, error

		holidays = Holiday.query.filter_by(org_id=orgId).all()

		holidayList = []

		for holiday in holidays:
			holidayList.append(
				{
					"code": holiday.code,
					"name": holiday.name,
					"description": holiday.description,
					"date": holiday.date,
				}
			)

		return holidayList, None

	except Exception as e:
		return None, str(e)


def getTimesheets(org_id, user_id, role, page=1, per_page=10):
	try:

		orgId, error = getIdFromCode(Organization, org_id)
		userId, error = getIdFromCode(User, user_id)

		print(userId,role,"userId")

		if error:
			return None, error



		query = (
			db.session.query(
				Timesheet.code,
				Timesheet.week_start,
				Timesheet.week_end,
				Project.name.label("project_name"),
				Task.name.label("task_name"),
				User.full_name.label("user_name"),
			)
			.outerjoin(Project, Project.id == Timesheet.project_id)
			.outerjoin(Task, Task.id == Timesheet.task_id)
			.outerjoin(User, User.id == Timesheet.user_id)
			# .group_by(User.full_name, Timesheet.week_start, Timesheet.week_end)
		)

		# if role == "Super Admin":
		# 	query = query.filter(User.org_id == orgId)
		if role == "HR":
			query = query.filter(User.org_id == orgId)

		elif role == "Candidate":
			print("here")
			query = query.filter(User.id == userId)

		allTimesheets, meta = paginateQuery(query, page, per_page)
		timesheetList = []

		for timsheet in allTimesheets:
			timesheetList.append(
				{
					# "code": timsheet.code,
					"timesheet_code": timsheet.code,
					"project_name" : timsheet.project_name,
					"task_name" : timsheet.task_name,
					"user_name" : timsheet.user_name,
					"week_start" : timsheet.week_start.isoformat(),
					"week_end" : timsheet.week_end.isoformat()
		# 			"employee_name": timesheet.user.full_name,
				}
			)

		return {"timesheet": timesheetList, "meta": meta}, None

	except Exception as e:
		return None, str(e)


def createHoliday(orgCode, userCode, holidayData):
	try:

		orgId, error1 = getIdFromCode(Organization, orgCode)
		userId, error2 = getIdFromCode(User, userCode)

		if error1 or error2:
			return None, error1 or error2

		if Holiday.query.filter_by(org_id=orgId, date=holidayData["date"]).first():
			return None, "Holiday already exists"

		holiday = Holiday(
			name=holidayData["name"],
			org_id=orgId,
			description=holidayData.get("description"),
			date=holidayData["date"],
			created_by=userId,
		)
		db.session.add(holiday)
		db.session.commit()

		if not holiday.id:
			return None, "Project creation failed"

		data = {
			"code": holiday.code,
			"name": holiday.name,
			"description": holiday.description,
			"date": holiday.date,
		}

		return data, None

	except Exception as e:
		return None, str(e)


def getOrCreateTimesheet(userCode, timesheetData):
	"""
	Fetch all timesheets for a user for the current week.
	If project_id is provided, create a timesheet for that project if it doesn't exist.
	"""

	today = datetime.utcnow().date()
	week_start = today - timedelta(days=today.weekday())
	week_end = week_start + timedelta(days=6)

	userId, error1 = getIdFromCode(User, userCode)

	if timesheetData.get("project_code"):
		projectId, error2 = getIdFromCode(Project, timesheetData.get("project_code"))

		taskId, error3 = getIdFromCode(Task, timesheetData.get("task_code"))

		if error1 or error2 or error3:
			return None, error1 or error2 or error3

		# If project_id is provided, create timesheet if not exists
		if projectId and taskId:
			timesheet = Timesheet.query.filter_by(
				user_id=userId,
				project_id=projectId,
				task_id=taskId,
				week_start=week_start,
				week_end=week_end,
			).first()

			if not timesheet:
				# Fetch user organization
				user = User.query.get(userId)

				holidays = Holiday.query.filter(
					Holiday.org_id == user.org_id,
					Holiday.date >= week_start,
					Holiday.date <= week_end,
				).all()
				holiday_dates = {h.date for h in holidays}

				# Prepare 7-day time_records
				time_records = []
				for i in range(7):
					day = week_start + timedelta(days=i)
					time_records.append(
						{
							"date": day.isoformat(),
							"hours": 0,
							"note": "",
							"is_weekend": day.weekday() >= 5,
							"is_holiday": day in holiday_dates,
						}
					)

				draft_status = TimesheetStatus.query.filter_by(name="Draft").first()

				timesheet = Timesheet(
					user_id=userId,
					project_id=projectId,
					task_id=taskId,
					week_start=week_start,
					week_end=week_end,
					time_records=time_records,
					status=draft_status.id,
					comment=timesheetData.get("comment"),
				)

				db.session.add(timesheet)
				db.session.commit()

	print("hello")
	# Fetch all timesheets for the user for this week
	user_timesheets = Timesheet.query.filter(
		Timesheet.user_id == userId,
		Timesheet.week_start == week_start,
		Timesheet.week_end == week_end,
	).all()

	print(user_timesheets, "user_timesheets")

	result = []
	for ts in user_timesheets:

		task = Task.query.filter(Task.id == ts.task_id).first()

		print(ts.history)
		historyList = []

		for history in ts.history:
			historyList.append(
				{
					"history_id" : history.id,
					"old_status": history.old_status_obj.name,
					"new_status": history.new_status_obj.name,
					"user" : history.changed_by_user.full_name,
					"time" : history.created_at
				}
			)

		result.append(
			{
				"timesheet_code": ts.code,
				"task_code": task.code if task else None,
				"task_name": task.name if task else None,
				"project_code": ts.project.code if ts.project else None,
				"project_name": ts.project.name if ts.project else None,
				"week_start": ts.week_start.isoformat(),
				"week_end": ts.week_end.isoformat(),
				"time_records": ts.time_records,  # assuming this is already JSON-serializable
				"status": ts.status_obj.name,
				"comment": ts.comment,
				"history": historyList,
			}
		)

	return result, None


# def updateTimesheet(userCode, timesheetData):
# 	"""
# 	Update hours and notes for a user's timesheet for a specific project and task.
# 	Expects timesheetData to contain:
# 									- project_code
# 									- task_code
# 									- time_records: list of {"date": "YYYY-MM-DD", "hours": float, "note": str}
# 									- comment (optional)
# 	"""

# 	userId, error = getIdFromCode(User, userCode)
# 	if error:
# 		return None, error

# 	projectId, error = getIdFromCode(Project, timesheetData.get("project_code"))

# 	if error:
# 		return None, error

# 	taskId, error = getIdFromCode(Task, timesheetData.get("task_code"))
# 	if error:
# 		return None, error

# 	if not (projectId and taskId):
# 		return None, "Project and Task codes are required"

# 	today = datetime.utcnow().date()
# 	week_start = today - timedelta(days=today.weekday())
# 	week_end = week_start + timedelta(days=6)

# 	# Fetch the existing timesheet
# 	timesheet = Timesheet.query.filter_by(
# 		user_id=userId,
# 		project_id=projectId,
# 		task_id=taskId,
# 		week_start=week_start,
# 		week_end=week_end,
# 	).first()

# 	if not timesheet:
# 		return None, "Timesheet not found for the given project and task"

# 	# Update time_records
# 	updated_records = timesheetData.get("time_records", [])

# 	for record in timesheet.time_records:
# 		for updated in updated_records:

# 			if str(record["date"]) == str(updated["date"]):
# 				record["hours"] = updated.get("hours", record["hours"])
# 				record["note"] = updated.get("note", record["note"])

# 	Timesheet.query.filter_by(id=timesheet.id).update(
# 		{"time_records": timesheet.time_records}
# 	)

# 	db.session.commit()

# 	# Prepare response
# 	task = Task.query.get(taskId)
# 	response = {
# 		"timesheet_code": timesheet.code,
# 		"task_code": task.code if task else None,
# 		"task_name": task.name if task else None,
# 		"project_code": timesheet.project.code if timesheet.project else None,
# 		"project_name": timesheet.project.name if timesheet.project else None,
# 		"week_start": timesheet.week_start.isoformat(),
# 		"week_end": timesheet.week_end.isoformat(),
# 		"time_records": timesheet.time_records,
# 		"status": timesheet.status_obj.name,
# 		"comment": timesheet.comment,
# 	}

# 	return response, None

def updateTimesheets(userCode, timesheetsData):
    """
    Update hours and notes for multiple timesheets for a user.
    Expects timesheetsData to be a list of timesheet objects containing:
        - project_code
        - task_code
        - time_records: list of {"date": "YYYY-MM-DD", "hours": float, "note": str}
        - comment (optional)
    """
    userId, error = getIdFromCode(User, userCode)
    if error:
        return None, error

    responses = []

    for timesheetData in timesheetsData:
        projectId, error = getIdFromCode(Project, timesheetData.get("project_code"))
        if error:
            responses.append({"error": f"Project code {timesheetData.get('project_code')} not found"})
            continue

        taskId, error = getIdFromCode(Task, timesheetData.get("task_code"))
        if error:
            responses.append({"error": f"Task code {timesheetData.get('task_code')} not found"})
            continue

        if not (projectId and taskId):
            responses.append({"error": "Project and Task codes are required"})
            continue

        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Fetch the existing timesheet
        timesheet = Timesheet.query.filter_by(
            user_id=userId,
            project_id=projectId,
            task_id=taskId,
            week_start=week_start,
            week_end=week_end,
        ).first()

        if not timesheet:
            responses.append({"error": "Timesheet not found for the given project and task"})
            continue

        # Update time_records
        updated_records = timesheetData.get("time_records", [])
        for record in timesheet.time_records:
            for updated in updated_records:
                if str(record["date"]) == str(updated["date"]):
                    record["hours"] = updated.get("hours", record["hours"])
                    record["note"] = updated.get("note", record["note"])

        # Update comment if provided
        if "comment" in timesheetData:
            timesheet.comment = timesheetData["comment"]

        Timesheet.query.filter_by(id=timesheet.id).update(
            {"time_records": timesheet.time_records, "comment": timesheet.comment}
        )
        db.session.commit()

        # Prepare response
        task = Task.query.get(taskId)
        response = {
            "timesheet_code": timesheet.code,
            "task_code": task.code if task else None,
            "task_name": task.name if task else None,
            "project_code": timesheet.project.code if timesheet.project else None,
            "project_name": timesheet.project.name if timesheet.project else None,
            "week_start": timesheet.week_start.isoformat(),
            "week_end": timesheet.week_end.isoformat(),
            "time_records": timesheet.time_records,
            "status": timesheet.status_obj.name,
            "comment": timesheet.comment,
        }
        responses.append(response)

    return responses, None



def reviewTimesheet(userCode, timesheetData):
	try:
		# Extract action (approve / reject)
		action = timesheetData["action"]

		if action not in ["submit","cancel","approve", "reject"]:
			return None, "Invalid action."

		# Get user ID from code
		userId, error = getIdFromCode(User, userCode)

		if error:
			return None, error

		# Find timesheet
		timesheet = Timesheet.query.filter_by(
			code=timesheetData["timesheet_code"]
		).first()
		if not timesheet:
			return None, "Invalid timesheet code"

		old_status = timesheet.status

		if action == "submit":
			if timesheet.status == TIMESHEET_STATUS["DRAFT"]:
				timesheet.status = TIMESHEET_STATUS["PENDING_APPROVAL"]

				history = TimesheetHistory(
					timesheet_id=timesheet.id,
					old_status=old_status,
					new_status=timesheet.status,
					changed_by=userId,
					comment=timesheetData.get("comment"),
				)
				db.session.add(history)
				db.session.commit()
				return "Timesheet submitted successfully", None

			return None, "Timesheet not able to submit"

		if action == "cancel":
			if timesheet.status == TIMESHEET_STATUS["PENDING_APPROVAL"]:
				timesheet.status = TIMESHEET_STATUS["CANCEL"]

				history = TimesheetHistory(
					timesheet_id=timesheet.id,
					old_status=old_status,
					new_status=timesheet.status,
					changed_by=userId,
					comment=timesheetData.get("comment"),
				)
				db.session.add(history)
				db.session.commit()
				return "Timesheet cancelled successfully", None

			return None, "Timesheet not able to cancel"

		# Authorization check
		if timesheet.project.manager_id != userId:
			return None, "Not authorized to review this timesheet"

		# Status must be pending
		if timesheet.status != TIMESHEET_STATUS["PENDING_APPROVAL"]:
			return None, "Timesheet is not pending approval"



		# Process action
		if action == "approve":
			timesheet.status = TIMESHEET_STATUS["APPROVED"]
		else:  # action == 'reject'
			timesheet.status = TIMESHEET_STATUS["REJECTED"]

		timesheet.approver_id = userId
		timesheet.review_comment = timesheetData.get("comment")  # optional
		# db.session.commit()

		history = TimesheetHistory(
			timesheet_id=timesheet.id,
			old_status=old_status,
			new_status=timesheet.status,
			changed_by=userId,
			comment=timesheetData.get("comment"),
		)
		db.session.add(history)

		db.session.commit()

		return f"Timesheet {action}d successfully", None

	except Exception as e:
		db.session.rollback()
		return None, str(e)
