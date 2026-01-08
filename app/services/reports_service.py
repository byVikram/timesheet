from datetime import datetime, timedelta
from sqlalchemy import distinct, func
# from app.constants.lookups import TIMESHEET_STATUS
from app.models import Project, User, Task
from app.models.timesheets import Timesheet, TimesheetEntry, TimesheetStatus
from app.extensions import db


def getProjectReports(orgId, userCodes, startDate=None, endDate=None):
    """
    Retrieve a comprehensive set of reports for a given organization.

    :param orgId: Organization ID
    :return: Dictionary with different report sections or error message
    """
    try:
        # ----- Project-level summary -----

        # Start date needs to be weeks first date i.e monday
        if startDate:
            startDate = startDate - timedelta(days=startDate.weekday())

        if endDate:
            endDate = endDate + timedelta(days=6 - endDate.weekday())

        project_summary = (
            db.session.query(
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                func.count(distinct(Task.id)).label("num_tasks"),
                func.sum(TimesheetEntry.hours).label("total_hours"),
            )
            .join(TimesheetEntry, TimesheetEntry.project_id == Project.id)
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .join(TimesheetStatus, TimesheetEntry.status == TimesheetStatus.id)
            .join(Task, Task.id == TimesheetEntry.task_id)
            .join(User, User.id == Timesheet.user_id)
            .filter(
                Project.org_id == orgId,
                User.code.in_(userCodes),
                Timesheet.week_start >= startDate if startDate else True,
                Timesheet.week_start <= endDate if endDate else True,
                # TimesheetStatus.id == TIMESHEET_STATUS["APPROVED"]
            )
            .group_by(Project.id, Project.name)
        )

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
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .join(TimesheetStatus, TimesheetEntry.status == TimesheetStatus.id)
            .join(Task, Task.id == TimesheetEntry.task_id)
            .join(User, User.id == Timesheet.user_id)
            .filter(
                Project.org_id == orgId,
                User.code.in_(userCodes),
                Timesheet.week_start >= startDate if startDate else True,
                Timesheet.week_start <= endDate if endDate else True,
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
                Timesheet.week_start >= startDate if startDate else True,
                Timesheet.week_start <= endDate if endDate else True,
                # TimesheetStatus.id == TIMESHEET_STATUS["APPROVED"],
            )
            .group_by(User.full_name, User.id)
            .all()
        )

        employee_summary_list = [
            {
                "user_full_name": e.user_full_name,
                "total_hours": float(e.total_hours),
            }
            for e in employee_summary
        ]

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

def getTimesheetReports(weeks_ago):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_ago)

        weekly_data = (
            db.session.query(
                Timesheet.week_start.label("week"),
                TimesheetStatus.name.label("status"),
                func.count(Timesheet.id).label("count"),
                func.coalesce(func.sum(TimesheetEntry.hours), 0).label("total_hours"),
            )
            .join(TimesheetStatus, Timesheet.status == TimesheetStatus.id)
            .outerjoin(TimesheetEntry, Timesheet.id == TimesheetEntry.timesheet_id)
            .filter(Timesheet.week_start >= start_date.date())
            .group_by(Timesheet.week_start, TimesheetStatus.name)
            .order_by(Timesheet.week_start.desc(), TimesheetStatus.name)
            .all()
        )

        weeks = {}
        for row in weekly_data:
            week_key = row.week.isoformat()

            if week_key not in weeks:
                weeks[week_key] = {
                    "week_start": week_key,
                    "statuses": {},
                    "total_timesheets": 0,
                }

            weeks[week_key]["statuses"][row.status] = {
                "count": row.count,
                "hours": float(row.total_hours),
            }

            weeks[week_key]["total_timesheets"] += row.count

        return list(weeks.values()), None

    except Exception as e:
        return None, str(e)
