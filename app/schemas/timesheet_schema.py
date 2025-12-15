from marshmallow import Schema, fields, validate


class HolidayCreationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    date = fields.Date(required=True)
    description = fields.Str(required=False, validate=validate.Length(min=6))


class SearchTimesheetSchema(Schema):
    page = fields.Integer()
    per_page = fields.Integer()
    timesheet_status = fields.Str()
    user_name = fields.Str()
    user_code = fields.Str()


# class GetTimesheetSchema(Schema):
#     project_code = fields.Str()
#     comment = fields.Str()
#     task_code = fields.Str()


class GetTimesheetSchema(Schema):
    timesheet_code = fields.Str()


class CreateTimesheetEntrySchema(Schema):
    timesheet_code = fields.Str(required=True)
    project_code = fields.Str(required=True)
    task_code = fields.Str(required=True)


class DeleteTimesheetEntrySchema(Schema):
    timesheet_entry_code = fields.Str(required=True)


class TimeRecordSchema(Schema):
    date = fields.Date(required=True)
    hours = fields.Float(required=True, validate=validate.Range(min=0))
    note = fields.Str(allow_none=True)


class UpdateTimesheetSchema(Schema):
    # project_code = fields.Str(required=True)
    # task_code = fields.Str(required=True)
    timesheet_entry_code = fields.Str(required=True)
    comment = fields.Str(allow_none=True)
    time_records = fields.List(fields.Nested(TimeRecordSchema), required=True)

    # New schema for a list of timesheets


class UpdateTimesheetsSchema(Schema):
    timesheets = fields.List(fields.Nested(UpdateTimesheetSchema), required=True)


class ReviewTimesheetSchema(Schema):
    timesheet_code = fields.Str(required=True)
    timesheet_entry_code = fields.Str()
    action = fields.Str(
        required=True,
        validate=validate.OneOf(["submit", "cancel", "approve", "reject"]),
    )
    comment = fields.Str()
