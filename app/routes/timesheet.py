import base64
from flask.views import MethodView
from flask_smorest import Blueprint
from app.constants.lookups import ROLES
from app.schemas.timesheet_schema import (
	CreateTimesheetEntrySchema,
	DeleteTimesheetEntrySchema,
	GetTimesheetSchema,
	HolidayCreationSchema,
	HolidayListSchema,
	ReviewTimesheetSchema,
	SearchTimesheetSchema,
	UpdateTimesheetsSchema,
)
from app.services.timesheet_service import (
	copyTimesheetEntry,
	createHoliday,
	createTimesheetEntry,
	createTimesheetsForAllUsers,
	deleteTimesheetEntry,
	downloadTimesheets,
	getAllTimesheets,
	getHolidays,
	getTimesheetByCode,
	getUserTimesheets,
	reviewTimesheet,
	updateTimesheets,
)
from app.utils.helpers import (
	authorize,
	getErrorMessage,
	getSuccessMessage,
	tokenValidation,
)

blp = Blueprint(
	"Timesheet APIs",
	__name__,
	description="Timesheet-related APIs",
)


@blp.route("/holiday/search")
class GetHolidayList(MethodView):
	@blp.doc(description="Retrieve the list of all Holidays organization specific")
	@blp.arguments(HolidayListSchema, location="query")
	@tokenValidation
	@authorize([ROLES["SUPER_ADMIN"], ROLES["HR"]])
	def get(self, requestObj):

		try:

			holidays, error = getHolidays(self.orgId, requestObj["year"])

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Holidays list fetched successfully",
				holidays,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/create-holiday")
class CreateProjects(MethodView):
	@blp.doc(description="Create a new holiday organization specific")
	@blp.arguments(HolidayCreationSchema)
	@tokenValidation
	@authorize(["Super Admin", "HR"])
	def post(self, projectData):
		try:
			holiday, error = createHoliday(self.orgId, self.userId, projectData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Holiday created successfully",
				holiday,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/search")
class GetTimesheets(MethodView):
	@blp.doc(description="Retrieve the list of all users timesheets")
	@blp.arguments(SearchTimesheetSchema)
	@tokenValidation
	@authorize(["ALL"])
	def post(self, timesheetData):
		try:

			timesheets, error = getAllTimesheets(
				self.orgId,
				self.userId,
				self.userRole,
				timesheetData,
				page=timesheetData["page"],
				per_page=timesheetData["per_page"],
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet list fetched successfully",
				timesheets,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/download")
class DownloadTimesheets(MethodView):
	@blp.doc(description="Download the list of all users timesheets")
	@blp.arguments(SearchTimesheetSchema)
	@tokenValidation
	@authorize(["ALL"])
	def post(self, timesheetData):
		try:

			output, error = downloadTimesheets(
				self.orgId, self.userId, self.userRole, timesheetData
			)

			encoded = base64.b64encode(output.getvalue()).decode('utf-8')

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"File created successfully",
				encoded,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/user/search")
class GetUserTimesheets(MethodView):

	@blp.doc(description="Retrieve the list of current user timesheets")
	@blp.arguments(SearchTimesheetSchema)
	@tokenValidation
	@authorize(["ALL"])
	def post(self, timesheetData):
		try:

			timesheets, error = getUserTimesheets(
				self.orgId,
				self.userId,
				self.userRole,
				timesheetData,
				page=timesheetData["page"],
				per_page=timesheetData["per_page"],
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet list fetched successfully",
				timesheets,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/details")
class GetTimesheet(MethodView):
	@blp.doc(description="Retrieve the details of a specific timesheet")
	@blp.arguments(GetTimesheetSchema, location="query")
	@tokenValidation
	@authorize(["ALL"])
	def get(self, timesheetData):
		try:

			timesheetCode = (
				timesheetData["timesheet_code"]
				if "timesheet_code" in timesheetData
				else None
			)
			timesheet, error = getTimesheetByCode(
				self.userId,
				self.orgId,
				timesheetCode,
				self.userRole,
				timesheetData["action"],
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet fetched successfully",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/copy-details")
class CopyTimesheetDetails(MethodView):
	@blp.doc(description="Copy from previous timesheet to current timesheet")
	@blp.arguments(GetTimesheetSchema)
	@tokenValidation
	@authorize(["ALL"])
	def post(self, timesheetData):
		try:

			timesheet, error = copyTimesheetEntry(
				self.userId,
				self.orgId,
				timesheetData["timesheet_code"],
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet copied successfully",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/create-entry")
class CreateTimesheetEntry(MethodView):
	@blp.doc(description="Create new timesheet entry")
	@blp.arguments(CreateTimesheetEntrySchema)
	@tokenValidation
	@authorize(["ALL"])
	def post(self, timesheetEntryData):
		try:
			timesheet, error = createTimesheetEntry(
				self.userId, self.orgId, timesheetEntryData
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet fetched successfully",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/create-timesheet")
class CreateTimesheet(MethodView):
	@blp.doc(description="Create new timesheet run by cron")
	# @blp.arguments(CreateTimesheetEntrySchema)
	# @tokenValidation
	# @authorize(["ALL"])
	def post(self):
		try:
			timesheet, error = createTimesheetsForAllUsers()

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/update")
class UpdateTimesheet(MethodView):
	@blp.doc(description="Update timesheet entries")
	@blp.arguments(UpdateTimesheetsSchema)
	@tokenValidation
	@authorize(["ALL"])
	def put(self, timesheetData):
		try:
			timesheet, error = updateTimesheets(
				self.userId, timesheetData, self.userRole
			)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet fetched successfully",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/review")
class ReviewTimesheet(MethodView):
	@blp.doc(description="Update timesheet status by reviewing it")
	@blp.arguments(ReviewTimesheetSchema)
	@tokenValidation
	@authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"], ROLES["EMPLOYEE"]])
	def post(self, timesheetData):
		try:
			timesheet, error = reviewTimesheet(self.userId, self.userRole, timesheetData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				timesheet,
				"",
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/delete-entry")
class DeleteTimesheetEntry(MethodView):
	@blp.doc(description="Delete specific timesheet entry")
	@blp.arguments(DeleteTimesheetEntrySchema, location="query")
	@tokenValidation
	@authorize([ROLES["EMPLOYEE"], ROLES["SUPER_ADMIN"], ROLES["MANAGER"], ROLES["HR"]])
	def delete(self, timesheetEntryData):
		try:
			timesheet, error = deleteTimesheetEntry(self.userId, timesheetEntryData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet entry deleted successfully",
				timesheet,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


