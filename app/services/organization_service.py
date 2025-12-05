from app.models import Organization
from app.extensions import db
from app.utils.helpers import paginateQuery


def getOrganization(page=1, per_page=10):
    try:

        query = (
            db.session.query(
                Organization.code,
                Organization.name,
                Organization.is_active,
                Organization.created_at,
                Organization.updated_at
            )
        )

        orgs, meta = paginateQuery(query, page, per_page)

        orgList = [{
                    "code": org.code,
                    "name": org.name,
                    "is_active": org.is_active,
                    "created_at": org.created_at,
                    "updated_at": org.updated_at,
                } for org in orgs]


        return {"organizations": orgList, "meta": meta}, None

    except Exception as e:
        return None, str(e)


def registerOrganization(name, email):

    if Organization.query.filter_by(email=email).first():
        return None, "Email already exists"

    if Organization.query.filter_by(name=name).first():
        return None, "Organization name already exists"

    org = Organization(name=name, email=email)
    db.session.add(org)
    db.session.commit()

    if not org.id:
        return None, "Organization registration failed"

    return org, None
