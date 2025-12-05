
from flask.views import MethodView
from flask_smorest import Blueprint
from app.schemas.timesheet_schema import GetTimesheetSchema, HolidayCreationSchema, ReviewTimesheetSchema, UpdateTimesheetSchema, UpdateTimesheetsSchema
from app.services.timesheet_service import createHoliday, getHolidays, getOrCreateTimesheet, getTimesheets, reviewTimesheet, updateTimesheet
from app.utils.helpers import authorize, getSuccessMessage, tokenValidation

blp = Blueprint(
	"Timesheet APIs",
	__name__,
	description="Timesheet-related APIs",
)


@blp.route("/holiday/search")
class GetHolidayList(MethodView):

	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def get(self):

		holidays, error = getHolidays(self.orgCode)

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Holidays list fetched successfully",
			holidays,
		)


@blp.route("/search")
class GetTimesheets(MethodView):

	@tokenValidation
	@authorize(['Super Admin', 'HR', 'Candidate'])

	def get(self):

		timesheets, error = getTimesheets(self.orgCode, self.userCode, self.userRole)

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Timesheet list fetched successfully",
			timesheets,
		)


@blp.route("/create-holiday")
class CreateProjects(MethodView):

	@blp.arguments(HolidayCreationSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def post(self, projectData):
		try:
			holiday, error = createHoliday(self.orgCode, self.userCode, projectData)

			if error:
				return {"status": "error", "message": error}, 400

			return getSuccessMessage(
				"Holiday created successfully",
				holiday,
			)

		except Exception as e:
			return {"status": "error", "message": str(e)}, 500


@blp.route("/get-timesheet")
class GetTimesheet(MethodView):

	@blp.arguments(GetTimesheetSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR', 'Manage', 'Candidate'])

	def post(self, timesheetData):
		try:
			# def getOrCreateTimesheet(userCode, project_id=None, comment=None):
			timesheet, error = getOrCreateTimesheet(self.userCode, timesheetData)

			if error:
				return {"status": "error", "message": error}, 400

			return getSuccessMessage(
				"Timesheet fetched successfully",
				timesheet,
			)

		except Exception as e:
			return {"status": "error", "message": str(e)}, 500


@blp.route("/update-timesheet")
class UpdateTimesheet(MethodView):

	@blp.arguments(UpdateTimesheetsSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR', 'Manage', 'Candidate'])

	def post(self, timesheetData):
		try:
			# def getOrCreateTimesheet(userCode, project_id=None, comment=None):
			timesheet, error = updateTimesheet(self.userCode, timesheetData)

			if error:
				return {"status": "error", "message": error}, 400

			return getSuccessMessage(
				"Timesheet fetched successfully",
				timesheet,
			)

		except Exception as e:
			return {"status": "error", "message": str(e)}, 500


@blp.route("/review")
class ReviewTimesheet(MethodView):

	@blp.arguments(ReviewTimesheetSchema)
	@tokenValidation
	@authorize(['Super Admin','HR', 'Manager'])

	def post(self, timesheetData):
		try:
			# def getOrCreateTimesheet(userCode, project_id=None, comment=None):
			timesheet, error = reviewTimesheet(self.userCode, timesheetData)

			if error:
				return {"status": "error", "message": error}, 400

			return getSuccessMessage(
				"",
				timesheet,
			)

		except Exception as e:
			return {"status": "error", "message": str(e)}, 500
