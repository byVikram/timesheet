from flask.views import MethodView
from flask_smorest import Blueprint
# from app.models.users import Organization, User
# from app.extensions import db
from app.services.organization_service import getOrganization, registerOrganization
from app.schemas.organization_schema import OrgRegisterSchema
from app.utils.helpers import authorize, getSuccessMessage, tokenValidation

blp = Blueprint(
	"Org APIs",
	__name__,
	description="Organization-related APIs",
)


@blp.route("/list")
class GetOrganizationList(MethodView):

	@tokenValidation
	@authorize(['Super Admin'])
	def get(self):

		orgData, error = getOrganization()

		if error:
			return {"status": "error", "message": error}, 400


		return getSuccessMessage(
			"Organization list fetched successfully",
			orgData,
		)


@blp.route("/register")
class RegisterOrganization(MethodView):
	@blp.arguments(OrgRegisterSchema)

	# @tokenValidation
	# @authorize(['Super Admin'])
	def post(self, org_data):

		org, error = registerOrganization(org_data["name"], org_data["email"])

		if error:
			return {"status": "error", "message": error}, 400

		return {
			"status": "success",
			"message": "Organization registered successfully",
			"organization_id": org.code,
		}
