
from flask.views import MethodView
from flask_smorest import Blueprint
from app.constants.lookups import ROLES
from app.schemas.report_schema import ProjectReportSchema
from app.services.reports_service import getProjectReports, getTimesheetReports
from app.utils.helpers import authorize, getErrorMessage, getSuccessMessage, tokenValidation

blp = Blueprint(
	"Reports APIs",
	__name__,
	description="Reports-related APIs",
)


@blp.route("/projects")
class ProjectReport(MethodView):
	@blp.arguments(ProjectReportSchema)

	@tokenValidation
	@authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])

	def post(self, args):
		try:

			projects, error = getProjectReports(self.orgId, args.get("user_codes"))

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Project reports fetched successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/timesheet")
class TimesheetReport(MethodView):

	@tokenValidation
	@authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])

	def post(self):
		try:

			timesheetsReport, error = getTimesheetReports(1)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Timesheet reports fetched successfully",
				timesheetsReport,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


