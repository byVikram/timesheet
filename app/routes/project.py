
from flask.views import MethodView
from flask_smorest import Blueprint
from app.schemas.project_schema import GetTasksSchema, ProjectCreationSchema, ProjectDetailsSchema, TaskCreationSchema
from app.services.project_service import createProject, createTask, getProjectDetails, getProjects, getTasks, updateProject
from app.utils.helpers import authorize, getErrorMessage, getSuccessMessage, tokenValidation

blp = Blueprint(
	"Project APIs",
	__name__,
	description="Project-related APIs",
)


@blp.route("/search")
class GetProjectList(MethodView):

	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def get(self):
		try:

			projects, error = getProjects(self.orgId)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Projects list fetched successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/details")
class GetProjectDetails(MethodView):

	@blp.arguments(ProjectDetailsSchema, location="query")
	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def get(self, projectData):
		try:

			projects, error = getProjectDetails(projectData['project_code'])

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Projects details fetched successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500



@blp.route("/create-project")
class CreateProjects(MethodView):

	@blp.arguments(ProjectCreationSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def post(self, projectData):
		try:
			projects, error = createProject(self.orgId, self.userId, projectData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Projects created successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500
		

@blp.route("/update-project")
class UpdateProject(MethodView):

	@blp.arguments(ProjectCreationSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR'])

	def put(self, projectData):
		try:
			projects, error = updateProject(self.orgId, projectData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Projects updated successfully",
				projects,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/create-task")
class CreateTask(MethodView):

	@blp.arguments(TaskCreationSchema)
	@tokenValidation
	@authorize(['Super Admin', 'HR', 'Manager'])

	def post(self, taskData):
		try:
			task, error = createTask(taskData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Tasks added successfully",
				task,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500


@blp.route("/task/search")
class ListTask(MethodView):

	@blp.arguments(GetTasksSchema, location="query")
	@tokenValidation
	@authorize(['ALL'])

	def get(self, taskData):
		try:
			tasks, error = getTasks(taskData)

			if error:
				return getErrorMessage(error), 400

			return getSuccessMessage(
				"Tasks fetched successfully",
				tasks,
			)

		except Exception as e:
			return getErrorMessage(str(e)), 500

