from flask.views import MethodView
from flask_smorest import Blueprint

from app.services.organization_service import getOrganization, registerOrganization
from app.schemas.organization_schema import GetOrgSchema, OrgRegisterSchema
from app.utils.helpers import (
    authorize,
    getErrorMessage,
    getSuccessMessage,
    tokenValidation,
)

blp = Blueprint(
    "Org APIs",
    __name__,
    description="Organization-related APIs",
)


@blp.route("/list")
class GetOrganizationList(MethodView):

    @blp.arguments(GetOrgSchema)
    @tokenValidation
    @authorize(["Super Admin"])
    def get(self, requestObj):

        try:

            orgData, error = getOrganization(
                page=requestObj["page"], per_page=requestObj["per_page"]
            )

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Organization list fetched successfully",
                orgData,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500


@blp.route("/register")
class RegisterOrganization(MethodView):
    @blp.arguments(OrgRegisterSchema)

    @tokenValidation
    @authorize(['Super Admin'])
    def post(self, org_data):

        try:

            org, error = registerOrganization(org_data["name"], org_data["email"])

            if error:
                return getErrorMessage(error), 400

            return getSuccessMessage(
                "Organization created successfully",
                org,
            )

        except Exception as e:
            return getErrorMessage(str(e)), 500
