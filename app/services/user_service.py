
from app.extensions import db
from app.models import User, UserRole, Project, UserProject
from app.models.timesheets import TimesheetStatus
from app.models.users import Organization
from app.services.common_service import getIdFromCode


from app.utils.helpers import (
    generateRefreshToken,
    generateToken,
    hashPassword,
    paginateQuery,
    verifyPassword,
)


def userLogin(email, password):
    """
    Authenticate a user by email and password.
    Generates access/refresh tokens and returns user info.
    """

    user = User.query.filter_by(email=email).first()

    if not user:
        return None, "User not found"

    accessToken = generateToken(user.code, user.role.code, user.organization.code)
    refreshToken = generateRefreshToken(user.code)

    data = {
        "access_token": accessToken,
        "refresh_token": refreshToken,
        "user": {
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.name if user.role else None,
        },
    }

    if verifyPassword(user.password, password) is False:
        return None, "Incorrect password"

    return data, None


def getUserAssignedRole(userCode):
    """
    Retrieve the role assigned to a user using their unique code.
    Will be called on every API from decorator
    """

    try:
        role_name = (
            db.session.query(UserRole.name, User.id, Organization.id.label("org_id"))
            .join(User, User.role_id == UserRole.id)
            .join(Organization, User.org_id == Organization.id)
            .filter(User.code == userCode)
            .first()
        )


        if not role_name:
            return None, None, "Role not found or user not found"

        return role_name.name, role_name.id, role_name.org_id, None

    except Exception as e:
        return None, None, None, str(e)


def getUserRoles():
    """
    Fetch a list of all available roles except SUPER_ADMIN.
    Returns role code, name, and description.
    """

    try:
        # roles = UserRole.query.all()
        SUPER_ADMIN_CODE = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

        roles = UserRole.query.filter(UserRole.code != SUPER_ADMIN_CODE).all()

        roleList = []

        for role in roles:
            roleList.append(
                {
                    "code": role.code,
                    "name": role.name,
                    "description": role.description,
                }
            )

        return roleList, None

    except Exception as e:
        return None, str(e)


def createUser(org_code, user_data):
    """
    Create a new user with the provided user_data dict.
    Validates role, org, email uniqueness, username uniqueness.
    """

    try:
        orgId, error1 = getIdFromCode(Organization, org_code)
        roleId, error2 = getIdFromCode(UserRole, user_data["role_code"])

        if error1 or error2:
            return None, error1 or error2

        if User.query.filter_by(email=user_data["email"]).first():
            return {"status": "error", "message": "Email already exists"}, 400

        if User.query.filter_by(username=user_data["username"]).first():
            return {"status": "error", "message": "Username already exists"}, 400

        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=hashPassword(user_data["password"]),
            org_id=orgId,
            role_id=roleId,
            full_name=user_data["full_name"],
        )
        db.session.add(new_user)
        db.session.commit()

        if not new_user.id:
            return None, "User creation failed"

        newUserData = {
            "user_code": new_user.code,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "is_active": new_user.is_active,
        }

        return newUserData, None

    except Exception as e:
        db.session.rollback()
        return None, str(e)


def resetUserPassword(userData):
    """
    Change password for a user. Requires old password verification.
    Returns updated user info dict on success, or (None, error_message) on failure.
    """

    try:
        user = User.query.filter_by(email=userData["email"]).first()
        if not user:
            return None, "User with this email does not exist"

        if not userData["new_password"] == userData["confirm_password"]:
            return None, "Mismatch in New password and Confirm password"

        # Check if old password matches
        if not verifyPassword(user.password, userData["old_password"]):
            return None, "Old password is incorrect"

        # Hash and update new password
        user.password = hashPassword(userData["new_password"])
        db.session.commit()

        updatedUserData = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
        }

        return updatedUserData, None

    except Exception as e:
        db.session.rollback()
        return None, str(e)


def getUsers(page=1, per_page=10, showAll=False):
    """
    Retrieve a paginated list of users.
    Includes metadata: page, per_page, total, total_pages.
    """
    try:

        # query = User.query.order_by(User.created_at.desc())
        query = (
            db.session.query(
                User.code,
                User.full_name,
                User.email,
                User.is_active,
                User.created_at,
                User.updated_at,
                Organization.name.label("org_name"),
                UserRole.name.label("role_name"),
            )
            .outerjoin(Organization, User.org_id == Organization.id)
            .outerjoin(UserRole, User.role_id == UserRole.id)
            # .order_by(User.created_at.desc())
        )

        if not showAll:

            users, meta = paginateQuery(query, page, per_page)
            userList = []

            for user in users:
                userList.append(
                    {
                        "code": user.code,
                        "name": user.full_name,
                        "email": user.email,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "org_name": user.org_name,
                        "role": user.role_name,
                    }
                )

            return {"users": userList, "meta": meta}, None

        else:
            users = query.all()
            userList = []

            for user in users:
                userList.append(
                    {
                        "code": user.code,
                        "name": user.full_name,
                        "email": user.email,
                        "is_active": user.is_active,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "org_name": user.org_name,
                        "role": user.role_name,
                    }
                )

            return userList, None

    except Exception as e:
        return None, str(e)


# def manageTimeEntry(action, user_code, data):
#     """
#     Unified function for time entry operations.

#     action:
#         - "clockin": Create a new time entry
#         - "clockout": Close the active time entry

#     data:
#         - lat (optional)
#         - lng (optional)
#         - notes (optional)
#     """
#     try:
#         # Validate user
#         userId, error = getIdFromCode(User, user_code)
#         if error:
#             return None, error

#         # CLOCK IN ---------------------------------------------
#         if action == "clockin":

#             # Check if user already clocked in
#             open_entry = TimeEntry.query.filter_by(user_id=userId, clock_out=None).first()
#             if open_entry:
#                 return None, "User has already Logged in"

#             entry = TimeEntry(
#                 user_id=userId,
#                 clock_in=datetime.utcnow(),
#                 clock_in_lat=data.get("lat"),
#                 clock_in_lng=data.get("lng"),
#                 notes=data.get("notes")
#             )

#             db.session.add(entry)
#             db.session.commit()

#             return "Success", None

#         # CLOCK OUT --------------------------------------------
#         elif action == "clockout":

#             # Get active entry
#             entry = TimeEntry.query.filter_by(user_id=userId, clock_out=None).first()
#             if not entry:
#                 return None, "No active clock-in found"

#             entry.clock_out = datetime.utcnow()
#             entry.clock_out_lat = data.get("lat")
#             entry.clock_out_lng = data.get("lng")

#             if data.get("notes"):
#                 entry.notes = data.get("notes")

#             db.session.commit()

#             return "Clock-out successful", None

#         # INVALID ACTION ----------------------------------------
#         else:
#             return None, "Invalid action parameter"

#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return None, str(e)

#     except Exception as e:
#         return None, str(e)


# def getUserTimeReport(user_id, start_date, end_date):
#     """
#     Returns daily work hours for a user from start_date to end_date.
#     If no clock-in, hours = 0
#     """
#     # Step 1: Create a dict of all days in range
#     num_days = (end_date - start_date).days + 1
#     daily_hours = OrderedDict()
#     for i in range(num_days):
#         day = start_date + timedelta(days=i)
#         daily_hours[day] = 0  # default 0 hours

#     # Step 2: Query all time entries in that date range
#     entries = TimeEntry.query.filter(
#         TimeEntry.user_id == user_id,
#         TimeEntry.clock_in >= datetime.combine(start_date, datetime.min.time()),
#         TimeEntry.clock_in <= datetime.combine(end_date, datetime.max.time())
#     ).all()

#     # Step 3: Aggregate hours per day
#     for entry in entries:
#         day = entry.clock_in.date()
#         if entry.clock_out:
#             hours = (entry.clock_out - entry.clock_in).total_seconds() / 3600
#         else:
#             hours = 0
#         daily_hours[day] += hours

#     # Step 4: Return as list of dicts
#     result = [{"date": day, "hours_worked": round(hours, 2)} for day, hours in daily_hours.items()]
#     return result


def getUserProjects(userCode):
    """
    Retrieve all active projects assigned to a user.
    Uses UserProject mapping table.
    """

    try:

        userId, error = getIdFromCode(User, userCode)
        if error:
            return None, "Invalid User"

        projects = (
            Project.query.join(UserProject, UserProject.project_id == Project.id)
            .filter(
                UserProject.user_id == userId, Project.active, UserProject.is_active
            )
            .all()
        )

        projectList = []

        for project in projects:
            projectList.append(
                {
                    "code": project.code,
                    "name": project.name,
                    "description": project.description,
                }
            )

        return projectList, None

    except Exception as e:
        return None, str(e)


def assignProject(authorUserId, projectData):
    """
    Assign a project to a user.
    Prevents duplicate assignments.
    Logs who created/updated the assignment.
    """

    try:

        userId, error2 = getIdFromCode(User, projectData["user_code"])
        projectId, error3 = getIdFromCode(Project, projectData["project_code"])

        if error2 or error3:
            return None, error2 or error3

        if UserProject.query.filter_by(user_id=userId, project_id=projectId).first():
            return None, "Project already exists"

        userProject = UserProject(
            user_id=userId,
            project_id=projectId,
            created_by=authorUserId,
            updated_by=authorUserId,
        )
        db.session.add(userProject)
        db.session.commit()

        if not userProject.id:
            return None, "Project creation failed"

        return True, None

    except Exception as e:
        db.session.rollback()
        return None, str(e)



def lookup():
    """
    Retrieve all lookup values needed.
    """

    try:

        timesheetStatus = TimesheetStatus.query.all()

        timesheetStatusList = []


        for ts in timesheetStatus:
            timesheetStatusList.append(
                {
                    "code": ts.code,
                    "name": ts.name,
                }
            )

        return {"timesheet_status": timesheetStatusList}, None

    except Exception as e:
        return None, str(e)
