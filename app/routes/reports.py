
from flask.views import MethodView
from flask_smorest import Blueprint
from app.schemas.project_schema import GetTasksSchema, ProjectCreationSchema, TaskCreationSchema
from app.services.project_service import createProject, createTask, getProjects, getTasks
from app.services.reports_service import getProjectReports
from app.utils.helpers import authorize, getErrorMessage, getSuccessMessage, tokenValidation

blp = Blueprint(
	"Reports APIs",
	__name__,
	description="Reports-related APIs",
)


@blp.route("/projects")
class GetUserList(MethodView):

	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def get(self):
		try:

			projects, error = getProjectReports(self.orgId)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Project reports fetched successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


