from sqlalchemy import distinct, func
from app.constants.lookups import TIMESHEET_STATUS
from app.models import Project, User, Task
from app.models.timesheets import Timesheet, TimesheetEntry, TimesheetStatus
from app.extensions import db
from app.models.users import UserProject


def getProjectReports(orgId, userCodes):
    """
    Retrieve a comprehensive set of reports for a given organization.

    :param orgId: Organization ID
    :return: Dictionary with different report sections or error message
    """
    try:
        # ----- Project-level summary -----

        user_exists = (
            db.session.query(UserProject.id)
            .join(User, User.id == UserProject.user_id)
            .filter(
                UserProject.project_id == Project.id,
                User.code.in_(userCodes)
            )
            .exists()
        )


        project_summary = (
            db.session.query(
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                func.count(distinct(Task.id)).label("num_tasks"),
                func.sum(TimesheetEntry.hours).label("total_hours"),
            )
            .join(TimesheetEntry, TimesheetEntry.project_id == Project.id)
            .join(TimesheetStatus, TimesheetEntry.status == TimesheetStatus.id)
            .join(Task, Task.id == TimesheetEntry.task_id)
            .filter(
                Project.org_id == orgId,
                user_exists,
                # TimesheetStatus.id == TIMESHEET_STATUS["APPROVED"]
            )
            .group_by(Project.id, Project.name)
        )

        print(
            project_summary.statement.compile(
                dialect=db.engine.dialect,
                compile_kwargs={"literal_binds": True}
            )
        )

        project_summary = project_summary.all()


        project_summary_list = [
            {
                "project_name": p.project_name,
                "num_tasks": p.num_tasks,
                "total_hours": float(p.total_hours),
            }
            for p in project_summary
        ]

        # ----- Task-level summary -----
        task_summary = (
            db.session.query(
                Project.name.label("project_name"),
                Task.name.label("task_name"),
                Task.code.label("task_code"),
                func.sum(TimesheetEntry.hours).label("total_hours"),
            )
            .join(TimesheetEntry, TimesheetEntry.project_id == Project.id)
            .join(TimesheetStatus, TimesheetEntry.status == TimesheetStatus.id)
            .join(Task, Task.id == TimesheetEntry.task_id)
            # .join(UserProject, UserProject.project_id == Project.id)
            # .join(User, UserProject.user_id == User.id)
            .filter(
                Project.org_id == orgId,
                # User.code.in_(userCodes),
                user_exists,
                # TimesheetStatus.id == TIMESHEET_STATUS["APPROVED"]
            )
            .group_by(Project.name, Task.name, Task.code)
            .all()
        )

        # Create a list of unique tasks across all projects
        all_tasks = list({t.task_name for t in task_summary})

        # Transform data for grouped bar chart
        task_summary_list = []
        projects = {t.project_name for t in task_summary}

        for project in projects:
            # Initialize dict with project_name
            project_dict = {"project_name": project}
            for task in all_tasks:
                # Find task hours for this project
                t = next(
                    (
                        x
                        for x in task_summary
                        if x.project_name == project and x.task_name == task
                    ),
                    None,
                )
                project_dict[task] = float(t.total_hours) if t else 0
            task_summary_list.append(project_dict)

            # ----- Employee-level summary -----
        employee_summary = (
            db.session.query(
                # Project.name.label("project_name"),
                User.id.label("user_id"),
                User.full_name.label("user_full_name"),
                func.sum(TimesheetEntry.hours).label("total_hours"),
            )
            .select_from(Project)
            .join(TimesheetEntry, TimesheetEntry.project_id == Project.id)
            .join(TimesheetStatus, TimesheetEntry.status == TimesheetStatus.id)
            .join(Timesheet, Timesheet.id == TimesheetEntry.timesheet_id)
            .join(User, User.id == Timesheet.user_id)
            .filter(
                Project.org_id == orgId,
                User.code.in_(userCodes),
                # TimesheetStatus.id == TIMESHEET_STATUS["APPROVED"],
            )
            .group_by(User.full_name, User.id)
            .all()
        )

        employee_summary_list = [
            {
                # "project_name": e.project_name,
                "user_full_name": e.user_full_name,
                "total_hours": float(e.total_hours),
            }
            for e in employee_summary
        ]

        # ----- Weekly trend summary -----
        # weekly_summary = (
        #     db.session.query(
        #         Project.name.label("project_name"),
        #         func.date_format(Timesheet.week_start, "%Y-%u").label("week"),  # Year-Week
        #         func.sum(TimesheetEntry.hours).label("total_hours")
        #     )
        #     .join(TimesheetEntry, TimesheetEntry.project_id == Project.id)
        #     .join(Timesheet, Timesheet.id == TimesheetEntry.timesheet_id)
        #     .filter(Project.org_id == orgId)
        #     .group_by(Project.name, func.date_format(Timesheet.week_start, "%Y-%u"))
        #     .order_by(Project.name, "week")
        #     .all()
        # )

        # weekly_summary_list = [
        #     {
        #         "project_name": w.project_name,
        #         "week": w.week,
        #         "total_hours": float(w.total_hours),
        #     }
        #     for w in weekly_summary
        # ]

        # Combine all reports into one dictionary
        reports = {
            "project_summary": project_summary_list,
            "task_summary": task_summary_list,
            "employee_summary": employee_summary_list,
            # "weekly_summary": weekly_summary_list,
        }

        return reports, None

    except Exception as e:
        return None, str(e)
