from datetime import datetime, timedelta
from sqlalchemy import Case, desc, func
from app.constants.lookups import TIMESHEET_STATUS
from app.models import Holiday, TimesheetStatus, Timesheet
from app.models.projects import Project, Task
from app.models.timesheets import TimesheetEntry, TimesheetHistory
from app.models.users import User
from app.services.common_service import getIdFromCode
from app.extensions import db

from app.utils.helpers import formatDatetime, paginateQuery


def getHolidays(orgId):
	"""
	Fetch all holidays for the given organization.

	Args:
																	orgId (int): Organization ID.

	Returns:
																	(list, error): A list of holidays or an error message.
	"""

	try:

		holidays = Holiday.query.filter_by(org_id=orgId).all()

		holidayList = [
			{
				"code": h.code,
				"name": h.name,
				"description": h.description,
				"date": h.date,
			}
			for h in holidays
		]

		return holidayList, None

	except Exception as e:
		return None, str(e)


def getUserTimesheets(orgId, userId, role, timesheetData, page=1, per_page=10):
	"""
	Fetch paginated timesheet records with filtering based on role and input data.

	Args:
																	orgId (int): Organization ID (required for HR role).
																	userId (int): User ID (required for Employee role).
																	role (str): User role ("Super Admin", "HR", "Employee").
																	timesheetData (dict): Filter parameters.
																	page (int): Pagination page number.
																	per_page (int): Items per page.

	Returns:
																	dict, error: Returns response dict or error string.
	"""

	try:

		query = (
			db.session.query(
				Timesheet.code,
				Timesheet.week_start,
				Timesheet.week_end,
				TimesheetStatus.name.label("timesheet_status"),
				User.full_name.label("user_name"),
				func.coalesce(func.sum(TimesheetEntry.hours), 0).label("total_hours"),
			)
			.outerjoin(User, User.id == Timesheet.user_id)
			.outerjoin(TimesheetStatus, TimesheetStatus.id == Timesheet.status)
			.outerjoin(TimesheetEntry, TimesheetEntry.timesheet_id == Timesheet.id)
			.group_by(
				Timesheet.code,
				Timesheet.week_start,
				Timesheet.week_end,
				TimesheetStatus.name,
				User.full_name,
			)
			.order_by(desc(Timesheet.week_start))
		)

		query = query.filter(User.id == userId)

		if timesheetData.get("timesheet_status"):
			query = query.filter(
				TimesheetStatus.code == timesheetData["timesheet_status"]
			)

		# if timesheetData.get("user_name"):
		# 	query = query.filter(
		# 		User.full_name.ilike(f"%{timesheetData['user_name']}%")
		# 	)

		allTimesheets, meta = paginateQuery(query, page, per_page)
		timesheetList = []

		timesheetList = [
			{
				"total_hours": item.total_hours,
				"timesheet_code": item.code,
				"user_name": item.user_name,
				"week_start": formatDatetime(item.week_start),
				"week_end": formatDatetime(item.week_end),
				"timesheet_status": item.timesheet_status,
			}
			for item in allTimesheets
		]

		return {"timesheet": timesheetList, "meta": meta}, None

	except Exception as e:
		return None, str(e)


def getAllTimesheets(orgId, userId, role, timesheetData, page=1, per_page=10):
	"""
	Fetch paginated timesheet records with filtering based on role and input data.

	Args:
		orgId (int): Organization ID (required for HR role).
		userId (int): User ID (required for Employee role).
		role (str): User role ("Super Admin", "HR", "Employee").
		timesheetData (dict): Filter parameters.
		page (int): Pagination page number.
		per_page (int): Items per page.

	Returns:
		dict, error: Returns response dict or error string.
	"""

	try:

		status_priority = {
			"Pending Approval": 0,
			"Partially Approved": 0,
			"Partially Rejected": 0,
			"Approved": 1,
			"Rejected": 2,
			"Draft": 3,
		}

		query = (
			db.session.query(
				Timesheet.code,
				Timesheet.week_start,
				Timesheet.week_end,
				TimesheetStatus.name.label("timesheet_status"),
				User.full_name.label("user_name"),
				func.coalesce(func.sum(TimesheetEntry.hours), 0).label("total_hours"),
			)
			.outerjoin(User, User.id == Timesheet.user_id)
			.outerjoin(TimesheetStatus, TimesheetStatus.id == Timesheet.status)
			.join(TimesheetEntry, TimesheetEntry.timesheet_id == Timesheet.id)
			.join(Project, TimesheetEntry.project_id == Project.id)
			.group_by(
				Timesheet.code,
				Timesheet.week_start,
				Timesheet.week_end,
				TimesheetStatus.name,
				User.full_name,
			)
			.order_by(
				Case(
					*[
						(TimesheetStatus.name == status, priority)
						for status, priority in status_priority.items()
					],
					else_=99,
				),
			)
		)

		print(role,"role")

		if role == "HR":
			query = query.filter(User.org_id == orgId)

		if role == "Manager":
			print("Manager")
			query = query.filter(Project.manager_id == userId)

		elif role == "Employee":
			query = query.filter(User.id == userId)

		if timesheetData.get("timesheet_status"):
			query = query.filter(
				TimesheetStatus.code == timesheetData["timesheet_status"]
			)

		if timesheetData.get("search"):
			query = query.filter(User.full_name.ilike(f"%{timesheetData['search']}%"))

		if timesheetData.get("user_code"):
			query = query.filter(User.code == timesheetData["user_code"])

		sort_columns = {
			"user_name": User.full_name,
			"week_start": Timesheet.week_start,
			"week_end": Timesheet.week_end,
			"status": Timesheet.status,
		}

		sort_by = timesheetData.get("sort_by")
		sort_direction = timesheetData.get("sort_direction", "asc").lower()

		if sort_by in sort_columns:
			column = sort_columns[sort_by]

			# Use func.lower for string columns (like full_name)
			# if sort_by == "user_name":
			# 	column = func.lower(column)

			# Apply ascending or descending
			if sort_direction == "desc":
				query = query.order_by(column.desc())
			else:
				query = query.order_by(column.asc())

		allTimesheets, meta = paginateQuery(query, page, per_page)
		timesheetList = []

		timesheetList = [
			{
				"total_hours": item.total_hours,
				"timesheet_code": item.code,
				"user_name": item.user_name,
				"week_start": formatDatetime(item.week_start),
				"week_end": formatDatetime(item.week_end),
				"timesheet_status": item.timesheet_status,
			}
			for item in allTimesheets
		]

		return {"timesheet": timesheetList, "meta": meta}, None

	except Exception as e:
		return None, str(e)


def createHoliday(orgId, userId, holidayData):
	try:

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


def getTimesheetByCode(userId, orgId, timesheet_code, userRole):
	"""
	Fetch a timesheet by code and return all its entries along with history, project, task, etc.
	"""

	# userId, error = getIdFromCode(User, userCode)

	if not timesheet_code:
		return {"timesheet_data": [], "timesheet_status": None}, None

	# Fetch the timesheet
	timesheet = Timesheet.query.filter_by(code=timesheet_code).first()

	# PREVIOUS timesheet
	prevTimesheet = (
		Timesheet.query.filter(
			Timesheet.user_id == timesheet.user_id,
			Timesheet.week_end < timesheet.week_start,
		)
		.order_by(Timesheet.week_end.desc())
		.limit(1)
		.first()
	)

	# NEXT timesheet
	nextTimesheet = (
		Timesheet.query.filter(
			Timesheet.user_id == timesheet.user_id,
			Timesheet.week_start > timesheet.week_end,
		)
		.order_by(Timesheet.week_start.asc())
		.limit(1)
		.first()
	)

	if not timesheet:
		return None, f"Timesheet with code {timesheet_code} not found"

	if timesheet.user_id != userId and userRole not in ["HR", "Super Admin", "Manager"]:
		return None, "Not authorized to view particular timesheet"

	result = []

	holidays = Holiday.query.filter(
		Holiday.org_id == orgId,
		Holiday.date >= timesheet.week_start,
		Holiday.date <= timesheet.week_end,
	).all()
	holiday_dates = {h.date for h in holidays}

	historyList = []

	for entry in timesheet.entries:
		print(entry,"entry")

		if userRole == "Manager":

			print(entry.project.manager_id, userId,"entry.project.manager_id")
			if entry.project.manager_id != userId:
				continue

		for history in entry.history:
			print(history, "history")
			new_status = history.new_status_obj.name if history.new_status_obj else None

			if new_status == TIMESHEET_STATUS["CANCEL"]:
				new_status = "Recall"

			historyList.append(
				{
					"history_id": history.id,
					"project_name":entry.project.name,
					"old_status": (
						history.old_status_obj.name if history.old_status_obj else None
					),
					"new_status": new_status,
					"user": (
						history.changed_by_user.full_name
						if history.changed_by_user
						else None
					),
					"date": formatDatetime(history.created_at, "%d/%m/%Y %I:%M %p"),
				}
			)

		for i, e in enumerate(entry.time_records):
			day = timesheet.week_start + timedelta(days=i)
			# if entry.status != TIMESHEET_STATUS["DRAFT"]:
			e["is_editable"] = (
				timesheet.user_id == userId
				and entry.status in [TIMESHEET_STATUS["DRAFT"], TIMESHEET_STATUS["REJECTED"]]
			)
			e["is_holiday"] = day in holiday_dates

		result.append(
			{
				"timesheet_code": timesheet.code,
				"timesheet_entry_code": entry.code,
				"task_code": entry.task.code if entry.task else None,
				"task_name": entry.task.name if entry.task else None,
				"project_code": entry.project.code if entry.project else None,
				"project_name": entry.project.name if entry.project else None,
				"week_start": timesheet.week_start.isoformat(),
				"week_end": timesheet.week_end.isoformat(),
				# "week_start": formatDatetime(timesheet.week_start),
				# "week_end": formatDatetime(timesheet.week_end),
				"time_records": entry.time_records,
				"status": entry.status_obj.name if entry.status_obj else None,
				"comment": None,
				
				"can_delete": (
					userRole == "Employee" and entry.status == TIMESHEET_STATUS["DRAFT"]
				),
				"can_approve": (
					userRole == "Manager"
					and entry.project.manager_id == userId
					and entry.status == TIMESHEET_STATUS["PENDING_APPROVAL"]
				),
				"can_reject": (
					userRole == "Manager"
					and entry.project.manager_id == userId
					and entry.status == TIMESHEET_STATUS["PENDING_APPROVAL"]
				),
			}
		)

	timesheetStatus = timesheet.status_obj.name if timesheet.status_obj else None

	return {
		"timesheet_data": result,
		"history": historyList,
		"timesheet_status": timesheetStatus,
		"week_start": formatDatetime(timesheet.week_start),
		"week_end": formatDatetime(timesheet.week_end),
		"previous_timesheet_code": (prevTimesheet.code if prevTimesheet else None),
		"next_timesheet_code": nextTimesheet.code if nextTimesheet else None,
	}, None


def createTimesheetEntry(userId, orgId, timesheetEntryData):
	"""
	Create a TimesheetEntry under a given timesheet for the specified project and task.
	Returns the created or existing entry.
	"""
	try:
		timesheetId, timesheet_error = getIdFromCode(
			Timesheet, timesheetEntryData["timesheet_code"]
		)

		# Fetch timesheet
		timesheet = Timesheet.query.get(timesheetId)
		if not timesheet:
			return (
				None,
				f"Timesheet with id {timesheetEntryData['timesheet_id']} not found",
			)

		if timesheet.user_id != userId:
			return None, "Not authorized to add entry"

		# Get project and task IDs from codes
		projectId, project_error = getIdFromCode(
			Project, timesheetEntryData["project_code"]
		)
		taskId, task_error = getIdFromCode(Task, timesheetEntryData["task_code"])

		if project_error or task_error or timesheet_error:
			return None, project_error or task_error or timesheet_error

		# Check if entry already exists
		existing_entry = TimesheetEntry.query.filter_by(
			timesheet_id=timesheet.id, project_id=projectId, task_id=taskId
		).first()

		if existing_entry:
			return "Entry exist for project and period", None

		# Fetch user organization for holidays
		# user = timesheet.user

		holidays = Holiday.query.filter(
			Holiday.org_id == orgId,
			Holiday.date >= timesheet.week_start,
			Holiday.date <= timesheet.week_end,
		).all()
		holiday_dates = {h.date for h in holidays}

		# Prepare 7-day time_records
		time_records = []
		for i in range(7):
			day = timesheet.week_start + timedelta(days=i)
			time_records.append(
				{
					"date": day.isoformat(),
					"hours": 0,
					"note": "",
					"is_weekend": day.weekday() >= 5,
					"is_holiday": day in holiday_dates,
					"is_editable": True,
				}
			)

		# Create the entry
		entry = TimesheetEntry(
			timesheet_id=timesheet.id,
			project_id=projectId,
			task_id=taskId,
			status=TIMESHEET_STATUS["DRAFT"],
			hours=0,
			time_records=time_records,
			approver_id=None,
		)

		db.session.add(entry)
		db.session.commit()

		return {"code": entry.code}, None

	except Exception as e:
		db.session.rollback()
		return None, str(e)


def createTimesheetsForAllUsers():
	try:
		today = datetime.utcnow().date()
		week_start = today - timedelta(days=today.weekday())  # Monday
		week_end = week_start + timedelta(days=6)  # Sunday

		# Fetch all user IDs
		users = User.query.with_entities(User.id).all()
		user_ids = [u.id for u in users]

		# Fetch existing timesheets for this week
		existing_ts = (
			Timesheet.query.filter(
				Timesheet.user_id.in_(user_ids),
				Timesheet.week_start == week_start,
				Timesheet.week_end == week_end,
			)
			.with_entities(Timesheet.user_id)
			.all()
		)
		existing_user_ids = set([u.user_id for u in existing_ts])

		# Prepare only new timesheets
		timesheet_data = [
			{
				"user_id": uid,
				"week_start": week_start,
				"week_end": week_end,
				"status": TIMESHEET_STATUS["DRAFT"],
			}
			for uid in user_ids
			if uid not in existing_user_ids
		]

		if timesheet_data:
			db.session.bulk_insert_mappings(Timesheet, timesheet_data)
			db.session.commit()

		return f"Created {len(timesheet_data)} new timesheets successfully", None

	except Exception as e:
		db.session.rollback()
		return None, str(e)


def deleteTimesheetEntry(userId, timesheetEntryData):
	"""
	Delete a TimesheetEntry by its code if it is in DRAFT status.
	"""

	try:

		entry = TimesheetEntry.query.filter_by(
			code=timesheetEntryData["timesheet_entry_code"]
		).first()

		if not entry:
			return (
				None,
				f"TimesheetEntry with code {timesheetEntryData['timesheet_entry_code']} not found",
			)

		if entry.timesheet.user_id != userId:
			return None, "Not authorized to delete particular timesheet entry"

		if entry.status != TIMESHEET_STATUS["DRAFT"]:
			return None, "Only DRAFT timesheet entries can be deleted"

		db.session.delete(entry)
		db.session.commit()

		return "Timesheet entry deleted successfully", None

	except Exception as e:
		db.session.rollback()
		return None, str(e)


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


def updateTimesheets(userId, timesheetsData, userRole="Employee"):
	"""
	Update hours and notes for multiple timesheet entries for a user.
	Expects timesheetsData to be a list of objects containing:
			- project_code
			- task_code
			- time_records: list of {"date": "YYYY-MM-DD", "hours": float, "note": str}
			- comment (optional, applies to the Timesheet)
	"""

	responses = []

	for entryData in timesheetsData["timesheets"]:
		# project_code = entryData.get("project_code")
		# task_code = entryData.get("task_code")

		# Get project and task IDs
		# projectId, project_error = getIdFromCode(Project, project_code) if project_code else (None, None)
		# taskId, task_error = getIdFromCode(Task, task_code) if task_code else (None, None)

		# if project_error or task_error:
		# 	responses.append({"error": project_error or task_error})
		# 	continue

		# if not (projectId and taskId):
		# 	responses.append({"error": "Project and Task codes are required"})
		# 	continue

		# Fetch the timesheet for this user and week
		# timesheet = Timesheet.query.filter_by(
		# 	user_id=userId,
		# 	week_start=week_start,
		# 	week_end=week_end
		# ).first()

		# if not timesheet:
		# 	responses.append({"error": f"Timesheet not found for user for this week"})
		# 	continue

		# print(timesheet,"timesheet")

		# Fetch or create TimesheetEntry
		entry = TimesheetEntry.query.filter_by(
			code=entryData["timesheet_entry_code"]
		).first()

		timesheet = entry.timesheet

		if timesheet.user_id != userId and userRole not in ["HR", "Super Admin"]:
			return None, "Not authorized to update particular timesheet"

		# if not entry:
		# 	print("creating entry")
		# 	entry, _ = createTimesheetEntry(timesheet.id, project_code, task_code)

		# Update time_records safely
		updated_records = entryData.get("time_records", [])
		if not isinstance(updated_records, list):
			responses.append({"error": "time_records must be a list of objects"})
			continue

		updated_records_map = {str(r["date"]): r for r in updated_records}

		total_hours = 0

		for i, record in enumerate(entry.time_records):
			date_str = str(record["date"])
			if date_str in updated_records_map:
				entry.time_records[i]["hours"] = updated_records_map[date_str].get(
					"hours", record["hours"]
				)
				entry.time_records[i]["note"] = updated_records_map[date_str].get(
					"note", record["note"]
				)

			total_hours += entry.time_records[i]["hours"]

		TimesheetEntry.query.filter_by(id=entry.id).update(
			{"time_records": entry.time_records, "hours": total_hours}
		)
		db.session.commit()

		if timesheetsData["action"] == "submit":
			TimesheetEntry.query.filter_by(id=entry.id).update(
				{"status": TIMESHEET_STATUS["PENDING_APPROVAL"]}
			)
			db.session.commit()

			data = {
				"action": "submit",
				"timesheet_code": timesheetsData["timesheet_code"],
			}

			reviewTimesheet(userId, data)

		# Prepare response
		response = {
			"timesheet_code": timesheet.code,
			"task_code": entry.task.code if entry.task else None,
			"task_name": entry.task.name if entry.task else None,
			"project_code": entry.project.code if entry.project else None,
			"project_name": entry.project.name if entry.project else None,
			"week_start": timesheet.week_start.isoformat(),
			"week_end": timesheet.week_end.isoformat(),
			"time_records": entry.time_records,
			"status": timesheet.status_obj.name if timesheet.status_obj else None,
			# "comment": timesheet.comment,
		}
		responses.append(response)

	return responses, None


def reviewTimesheet(userId, timesheetData):
	try:
		# Extract action (approve / reject)
		action = timesheetData["action"]

		if action not in ["submit", "cancel", "approve", "reject"]:
			return None, "Invalid action."

		# Find timesheet

		# if "timesheet_code" in timesheetData:
		timesheet = Timesheet.query.filter_by(
			code=timesheetData["timesheet_code"]
		).first()

		if not timesheet:
			return None, "Invalid timesheet code"

		timesheetEntries = timesheet.entries
		
		notApprovedCount = sum(1 for entry in timesheetEntries if entry.status != 3)
		canApproveTimesheet = notApprovedCount == 1		# Flag to change the timesheet entru to approve



		# canApproveTimesheet = all(entry.status == 3 for entry in timesheetEntries)

		if (
			"timesheet_entry_code" in timesheetData
			and timesheetData["timesheet_entry_code"]
		):
			timesheetEntry = TimesheetEntry.query.filter_by(
				code=timesheetData["timesheet_entry_code"]
			).first()

			# This part of code will be used if Manager is trying to approve/reject single timesheet entry

			if not timesheetEntry:
				return None, "Invalid timesheet_entry_code"

		if action == "submit":
			if timesheet.status == TIMESHEET_STATUS["DRAFT"]:
				timesheet.status = TIMESHEET_STATUS["PENDING_APPROVAL"]

				for entry in timesheetEntries:

					history = TimesheetHistory(
						timesheet_entry_id=entry.id,
						old_status=entry.status,
						new_status=timesheet.status,
						changed_by=userId,
						comment=timesheetData.get("comment"),
					)
					entry.status = timesheet.status
					db.session.add(history)
					db.session.commit()

				return "Timesheet submitted successfully", None

			return None, "Timesheet not able to submit"

		if action == "cancel":
			if timesheet.status == TIMESHEET_STATUS["PENDING_APPROVAL"]:
				timesheet.status = TIMESHEET_STATUS["DRAFT"]

				for entry in timesheetEntries:
					# print(entry,"entry")

					history = TimesheetHistory.query.filter_by(
						timesheet_entry_id=entry.id
					).all()

					# history = TimesheetHistory(
					# 	timesheet_entry_id=entry.id,
					# 	old_status=entry.status,
					# 	new_status=timesheet.status,
					# 	changed_by=userId,
					# 	comment=timesheetData.get("comment"),
					# )
					entry.status = timesheet.status
					for h in history:
						db.session.delete(h)

					db.session.commit()

				return "Timesheet cancelled successfully", None

			return None, "Timesheet not able to cancel"

		# Authorization check
		if timesheetEntry.project.manager_id != userId:
			return None, "Not authorized to review this timesheet"

		# Status must be pending
		if timesheetEntry.status != TIMESHEET_STATUS["PENDING_APPROVAL"]:
			return None, "Timesheet entry is not pending approval"

		if action == "approve":
			# Need to approve Timesheet entry not the timesheet and make timsheet status to partial approve
			timesheetEntry.status = TIMESHEET_STATUS["APPROVED"]
			# timesheetEntry.approver_id = userId
			timesheet.status = (
				TIMESHEET_STATUS["APPROVED"]
				if canApproveTimesheet
				else TIMESHEET_STATUS["PARTIAL_APPROVE"]
			)

		else:
			# Need to reject Timesheet entry not the timesheet and make timsheet status to partial reject
			timesheetEntry.status = TIMESHEET_STATUS["REJECTED"]
			timesheet.status = TIMESHEET_STATUS["PARTIAL_REJECT"]

		timesheetEntry.approver_id = userId
		# timesheet.review_comment = timesheetData.get("comment")  # optional
		# db.session.commit()

		history = TimesheetHistory(
			timesheet_entry_id=timesheetEntry.id,
			old_status=timesheetEntry.status,
			new_status=timesheet.status,
			changed_by=userId,
			comment=timesheetData.get("comment"),
		)
		db.session.add(history)

		db.session.commit()

		print(action, "action")

		return f"Timesheet {action}d successfully", None

	except Exception as e:
		db.session.rollback()
		return None, str(e)
