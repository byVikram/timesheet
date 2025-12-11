from flask.views import MethodView
from flask_smorest import Blueprint
from app.constants.lookups import ROLES
from app.schemas.user_schema import (
    AssignProjectSchema,
    GetUsersSchema,
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
    lookup,
    resetUserPassword,
    userLogin,
)
from app.utils.helpers import (
    authorize,
    getErrorMessage,
    getSuccessMessage,
    tokenValidation,
)

blp = Blueprint(
    "User APIs",
    __name__,
    description="User-related APIs",
)


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):

        try:
            token, error = userLogin(user_data["email"], user_data["password"])

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage("User Logged in successfully", token)

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/reset-password")
class ResetPassword(MethodView):
    @blp.arguments(ResetPasswordSchema)
    def post(self, userData):
        """
        Reset user Password
        """
        try:
            reset, error = resetUserPassword(userData)

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage("User password reset successful", reset)

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/roles")
class GetUserRoles(MethodView):

    @tokenValidation
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"]])
    def get(self):

        try:
            roles, error = getUserRoles()

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Users roles fetched successfully",
                roles,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/create-user")
class RegisterUser(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserResponseSchema)
    @tokenValidation
    @authorize(["Super Admin", "HR"])
    def post(self, user_data):
        """
        Create a new user
        """

        try:
            org_code = user_data.get("org_code", self.orgCode)
            new_user, error = createUser(org_code, user_data)

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage("User created successfully", new_user)

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/search")
class GetUserList(MethodView):

    @blp.arguments(GetUsersSchema)
    @tokenValidation
    @authorize(["Super Admin", "HR", "Manager"])
    def post(self, requestObj):

        try:
            usersData, error = getUsers(
                page=requestObj["page"], per_page=requestObj["per_page"]
            )

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Users list fetched successfully",
                usersData,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/projects")
class GetUserProjects(MethodView):

    @blp.arguments(UserCodeSchema, location="query")
    @blp.doc(description="Retrieve the list of projects assigned to a specific user")
    @tokenValidation
    @authorize(["Super Admin", "HR", "Manager", "Employee"])
    def get(self, userData):

        try:
            user_code = userData.get("user_code", self.userCode)
            projects, error = getUserProjects(user_code)

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Projects list fetched successfully",
                projects,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/assign-project")
class AssignProject(MethodView):

    @blp.arguments(AssignProjectSchema)
    @blp.doc(description="Retrieve the list of projects assigned to a specific user")
    @tokenValidation
    @authorize(["Super Admin", "HR", "Manager"])
    def post(self, projectData):

        try:
            userProject, error = assignProject(self.userId, projectData)

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Record created successfully",
                userProject,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/lookup")
class Lookup(MethodView):

    @blp.doc(description="Lookup data for users")
    @tokenValidation
    @authorize(["Super Admin", "HR", "Manager", "Employee"])
    def get(self):

        try:
            lookupData, error = lookup()

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Lookup data fetched successfully",
                lookupData,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500

