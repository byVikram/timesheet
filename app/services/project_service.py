from app.models import Project, User, Task
from app.models.users import UserProject
from app.services.common_service import getIdFromCode
from app.extensions import db
from app.utils.helpers import formatDatetime


def getProjects(orgId):
    """
    Retrieve all projects for a given organization.

    :param org_id: Organization code or ID
    :return: Tuple (list of projects, error message)
    """

    try:

        projects = Project().query.filter_by(org_id=orgId).all()

        projectList = []

        for project in projects:
            projectList.append(
                {
                    "code": project.code,
                    "name": project.name,
                    "description": project.description,
                    "start_date": formatDatetime(project.start_date, "%d %b %Y"),
                    "end_date": formatDatetime(project.end_date,"%d %b %Y"),
                    "active": project.active,
                }
            )

        return projectList, None

    except Exception as e:
        return None, str(e)


def getProjectDetails(projectCode):
    """

    """

    try:

        project = Project().query.filter_by(code=projectCode).first()



        if not project:
            return None, "Invalid project_code"

        # users = UserProject().join(User, User.id == UserProject.user_id).query.filter_by(project_id=project.id).all()
        users = db.session.query(
                    User.full_name,
                    User.code,
                    UserProject.is_active
                ).join(UserProject, User.id == UserProject.user_id)\
                .filter(UserProject.project_id == project.id)\
                .all()



        userList = []

        if users:

            for user in users:
                userList.append({
                    "name":user.full_name,
                    "code":user.code,
                    "is_active":user.is_active
                })


        projectData = {
            "name" : project.name,
            "manager_name": project.created_by_user.full_name,
            "manager_code": project.created_by_user.code,
            "description":project.description,
            "start_date":project.start_date,
            "end_date":project.end_date,
            "active":project.active,
            "user_list":userList
        }
        return projectData, None

    except Exception as e:
        return None, str(e)


def createProject(orgId, userId, projectData):
    """
    Create a new project within an organization.

    :param orgId: ID of the organization
    :param userId: ID of the user creating the project
    :param projectData: Dict containing project details
        Expected keys: name, description, start_date, end_date, active, manager_code
    :return: Tuple (created project data, error message)
    """

    try:

        mangerId, error3 = getIdFromCode(User, projectData["manager_code"])

        if error3:
            return None, error3

        if Project.query.filter_by(org_id=orgId, name=projectData["name"]).first():
            return None, "Project already exists"

        project = Project(
            name=projectData["name"],
            org_id=orgId,
            description=projectData.get("description"),
            start_date=projectData.get("start_date"),
            end_date=projectData.get("end_date"),
            active=projectData.get("active", True),
            manager_id=mangerId,
            created_by=userId,
        )
        db.session.add(project)
        db.session.commit()

        if not project.id:
            return None, "Project creation failed"

        data = {
            "code": project.code,
            "name": project.name,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "active": project.active,
        }

        return data, None

    except Exception as e:
        return None, str(e)



def updateProject(orgId, projectData):
    """

    """

    try:

        mangerId, error3 = getIdFromCode(User, projectData["manager_code"])

        if error3:
            return None, error3

        project =  Project.query.filter_by(code=projectData['project_code']).first()

        if not project:
            return None, "Project does not exist"


        project.description = projectData.get("description")
        project.start_date = projectData.get("descristart_dateption")
        project.end_date = projectData.get("end_date")
        project.active = projectData.get("active", True)
        project.manager_id = mangerId

        db.session.commit()

        if not project.id:
            return None, "Project creation failed"

        data = {
            "code": project.code,
            "name": project.name,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "active": project.active,
        }

        return data, None

    except Exception as e:
        return None, str(e)



def createTask(taskData):
    try:

        projectId, error = getIdFromCode(Project, taskData["project_code"])

        if error:
            return None, error

        existingTask = Task.query.filter_by(name=taskData["name"], project_id=projectId).first()

        if existingTask:
            return None, "Same task exist for this Project"

        task = Task(
            project_id=projectId,
            name=taskData["name"],
            description=taskData["description"],
        )

        db.session.add(task)
        db.session.commit()

        if not task.id:
            return None, "Task creation failed"

        data = {"code": task.code, "name": task.name, "description": task.description}

        return data, None

    except Exception as e:
        return None, str(e)


def getTasks(projectData):
    try:

        projectId, error = getIdFromCode(Project, projectData["project_code"])

        if error:
            return None, error

        tasks = Task().query.filter_by(project_id=projectId).all()

        taskList = []

        for task in tasks:
            taskList.append(
                {
                    "code": task.code,
                    "name": task.name,
                    "description": task.description,
                }
            )

        return taskList, None

    except Exception as e:
        return None, str(e)
