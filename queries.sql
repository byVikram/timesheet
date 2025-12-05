

INSERT INTO user_roles (code, name, description)
VALUES
    ('5d5f9f52-7ac1-4c1c-b9a1-2e6d2eb8f441', 'Super Admin', 'Has full system access and administrative privileges'),
    ('d2e3a9f8-8c23-4f02-9bc2-b658b9c74820', 'HR', 'Handles employee onboarding, policies, and HR operations'),
    ('1c94ab84-b39e-4fd3-8ce4-638d58d52b48', 'Manager', 'Responsible for leading teams and approving timesheets'),    
    ('8fb71f98-16cd-4410-9e8c-f131bbf78b3f', 'Candidate', 'External user applying for job roles');


INSERT INTO timesheet_status (code, name, description) VALUES
('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Draft', 'Timesheet is created but not yet submitted for approval.'),
('c9bf9e57-1685-4c89-bafb-ff5af830be8a', 'Pending Approval', 'Timesheet has been submitted and is awaiting manager approval.'),
('3fa85f64-5717-4562-b3fc-2c963f66afa6', 'Approved', 'Timesheet has been reviewed and approved by the manager.'),
('9a8b7c6d-5e4f-4312-b3a1-1c2d3e4f5a6b', 'Rejected', 'Timesheet has been reviewed and rejected. Employee may need to correct and resubmit.'),
('7f3c1e4b-2d9a-4e5f-8b2c-3a1d4f6e7b8c', 'Cancelled', 'Timesheet has been cancelled and will not be processed.'),
('2b1c3d4e-5f6a-7b8c-9d0e-1f2a3b4c5d6e', 'Locked', 'Timesheet is locked and cannot be edited.'),
('8c7d6e5f-4a3b-2c1d-0e9f-8b7a6c5d4e3f', 'In Progress', 'Timesheet is being filled out but not yet finalized.');
