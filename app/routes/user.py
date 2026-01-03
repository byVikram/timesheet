from flask.views import MethodView
from flask_smorest import Blueprint
from app.constants.lookups import ROLES
from app.schemas.user_schema import (
    ManageUserProjectSchema,
    GetUserDetailsSchema,
    GetUsersSchema,
    ResetPasswordSchema,
    UserCodeSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserResponseSchema,
)
from app.services.user_service import (
    createUser,
    getUserDetails,
    getUserProjects,
    getUserRoles,
    getUsers,
    lookup,
    manageUserProject,
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
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
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
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
    def post(self, user_data):
        """
        Create a new user
        """

        try:
            org_code = user_data.get("org_code", self.orgCode)
            new_user, error = createUser(org_code, user_data)

            print(error,"++error")

            if error:
                return getErrorMessage(str(error)), 400

            return getSuccessMessage("User created successfully", new_user), 200

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/search")
class GetUserList(MethodView):

    @blp.arguments(GetUsersSchema)
    @tokenValidation
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
    def post(self, requestObj):

        try:
            usersData, error = getUsers(
                requestObj.get("variant", "all"), page=requestObj["page"], per_page=requestObj["per_page"]
            )

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Users list fetched successfully",
                usersData,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500

@blp.route("/details")
class GetUserDetails(MethodView):

    @blp.arguments(GetUserDetailsSchema)
    @tokenValidation
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
    def post(self, requestObj):

        try:
            usersData, error = getUserDetails(requestObj.get("user_code"))

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Users data fetched successfully",
                usersData,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/projects")
class GetUserProjects(MethodView):

    @blp.arguments(UserCodeSchema, location="query")
    @blp.doc(description="Retrieve the list of projects assigned to a specific user")
    @tokenValidation
    @authorize(['ALL'])
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


@blp.route("/manage-user-project")
class ManageUserProject(MethodView):

    @blp.arguments(ManageUserProjectSchema)
    @blp.doc(description="Manage Project user Relationship")
    @tokenValidation
    @authorize([ROLES["SUPER_ADMIN"], ROLES["HR"], ROLES["MANAGER"]])
    def post(self, projectData):

        try:
            userProject, error = manageUserProject(self.userId, projectData)

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Project user updated successfully",
                userProject,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/lookup")
class Lookup(MethodView):

    @blp.doc(description="Lookup data for users")
    @tokenValidation
    @authorize(['ALL'])
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

