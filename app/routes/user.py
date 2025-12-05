from flask.views import MethodView
from flask_smorest import Blueprint
from app.schemas.user_schema import (
	AssignProjectSchema,
	ResetPasswordSchema,
	UserCodeSchema,
	UserLoginSchema,
	UserRegisterSchema,
	UserResponseSchema,
)
from app.services.user_service import (
	assignProject,
	createUser,
	getUserProjects,
	getUserRoles,
	getUsers,
	resetUserPassword,
	userLogin,
)
from app.utils.helpers import authorize, getSuccessMessage, tokenValidation

blp = Blueprint(
	"User APIs",
	__name__,
	description="User-related APIs",
)


@blp.route("/login")
class UserLogin(MethodView):
	@blp.arguments(UserLoginSchema)
	def post(self, user_data):

		token, error = userLogin(user_data["email"], user_data["password"])

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage("User Logged in successfully", token)


@blp.route("/roles")
class GetUserRoles(MethodView):

	@tokenValidation
	@authorize(["Super Admin", "HR"])
	def get(self):

		roles, error = getUserRoles()

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Users list fetched successfully",
			roles,
		)


@blp.route("/create-user")
class RegisterUser(MethodView):
	@blp.arguments(UserRegisterSchema)  # validate request body
	@blp.response(201, UserResponseSchema)  # serialize response

	@tokenValidation
	@authorize(["Super Admin", "HR"])
	def post(self, user_data):
		"""
		Create a new user
		"""

		org_code = user_data.get('org_code', self.orgCode)
		new_user, error = createUser(org_code, user_data)

		if error:
			print(error)
			return {"status": "error", "message": error}, 400

		return getSuccessMessage("User created successfully", new_user)


@blp.route("/reset-password")
class ResetPassword(MethodView):
	@blp.arguments(ResetPasswordSchema)  # validate request body
	# @blp.response(201, UserResponseSchema)  # serialize response

	# @tokenValidation
	# @authorize(["Super Admin", "HR"])
	def post(self, userData):
		"""
		Create a new user
		"""

		reset, error = resetUserPassword(userData)

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage("User created successfully", reset)


@blp.route("/search")
class GetUserList(MethodView):

	@tokenValidation
	@authorize(["Super Admin", "HR", "Manager"])
	def get(self):

		usersData, error = getUsers()

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Users list fetched successfully",
			usersData,
		)


@blp.route("/projects")
class GetUserProjects(MethodView):

	@blp.arguments(UserCodeSchema, location='query')
	@blp.doc(description="Retrieve the list of projects assigned to a specific user")

	@tokenValidation
	@authorize(["Super Admin", "HR", "Manager", "Candidate"])
	def get(self, userData):

		user_code = userData.get('user_code', self.userCode)
		projects, error = getUserProjects(user_code)


		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Projects list fetched successfully",
			projects,
		)


@blp.route("/assign-project")
class AssignProject(MethodView):

	@blp.arguments(AssignProjectSchema)
	@blp.doc(description="Retrieve the list of projects assigned to a specific user")

	@tokenValidation
	@authorize(["Super Admin", "HR", "Manager"])
	def post(self, projectData):

		userProject, error = assignProject(self.userCode, projectData)

		if error:
			return {"status": "error", "message": error}, 400

		return getSuccessMessage(
			"Record created successfully",
			userProject,
		)

assignProject