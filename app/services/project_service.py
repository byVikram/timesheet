from app.models import Project, User, Task
from app.services.common_service import getIdFromCode
from app.extensions import db


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
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "active": project.active,
                }
            )

        return projectList, None

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



def createTask(taskData):
    try:

        projectId, error = getIdFromCode(Project, taskData["project_code"])

        if error:
            return None, error

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
