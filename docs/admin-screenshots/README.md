# Django Admin Screenshots

This directory contains comprehensive screenshots of the planit-mini Django admin interface, documenting all major models and their admin configurations.

## Screenshot Index

### Core Models (core app)

#### Workspace
- **04-core-workspace-list.png** - Workspace list view showing all workspaces with sortable columns
- **05-core-workspace-detail-with-inline.png** - Workspace detail view with inline Membership management

#### Membership  
- **06-core-membership-list.png** - Membership list with custom filters by role and workspace
- **07-core-membership-detail.png** - Membership detail view showing user-workspace-role relationship

### Assets Models (assets app)

#### FormFactor
- **08-assets-formfactor-list.png** - Form factor list (Tower, Rack Mount, Mini PC, etc.)
- **09-assets-formfactor-detail.png** - Form factor detail view

#### OS (Operating System)
- **10-assets-os-list.png** - Operating system list showing various OS options
- **11-assets-os-detail.png** - OS detail view

#### Application
- **12-assets-application-list.png** - Application list (Docker, PostgreSQL, Redis, etc.)
- **13-assets-application-detail.png** - Application detail view

#### Project
- **14-assets-project-list.png** - Project list showing workspace-scoped projects
- **15-assets-project-detail.png** - Project detail with autocomplete workspace selection

#### Asset (Most Complex)
- **16-assets-asset-list.png** - Asset list with custom columns (warranty_status, next_due_status)
- **17-assets-asset-list-with-filters.png** - Asset list with active workspace filter showing filter sidebar
- **18-assets-asset-detail-media-server.png** - Media Server asset detail showing:
  - WorkOrder inline (showing related work orders)
  - ActivityInstance inline (showing maintenance history)
  - Multiple autocomplete fields

### Work Models (work app)

#### MaintenanceTask
- **19-work-maintenancetask-list.png** - Maintenance task list with workspace and cadence filters
- **20-work-maintenancetask-detail-with-inline.png** - Task detail with inline WorkOrder management

#### WorkOrder (Most Complex)
- **21-work-workorder-list.png** - WorkOrder list with date_hierarchy navigation
- **22-work-workorder-list-with-due-filter.png** - WorkOrder list with custom "Next 7 days" due window filter applied
- **23-work-workorder-detail.png** - WorkOrder detail showing all fields and autocomplete
- **24-work-workorder-bulk-actions.png** - WorkOrder list with 2 items selected showing bulk action dropdown

#### ActivityInstance
- **25-work-activityinstance-list.png** - Activity instance list with date_hierarchy (showing occurred_at dates)
- **26-work-activityinstance-detail.png** - Activity detail showing kind, asset, workspace, and performer

## Key Admin Features Documented

### Custom List Displays
- Asset model: Shows warranty status, next work due status
- WorkOrder model: Shows task, asset, workspace, due date, status, assignments
- Membership model: Shows user, workspace, and role in a clean table

### Filters
- Asset: Multiple filters (workspace, kind, form_factor, os, applications, location, purchase_date, warranty_expires)
- WorkOrder: Custom DueWindowFilter (Overdue, Next 7 days, Next 30 days, Beyond 30 days)
- Membership: Filters by role and workspace

### Inlines
- Workspace detail: Inline Membership management
- Asset detail: Inline WorkOrder and ActivityInstance management
- MaintenanceTask detail: Inline WorkOrder management

### Autocomplete Fields
- Project admin: Autocomplete for workspace selection
- Asset admin: Autocomplete for workspace, project, form_factor, os selections
- WorkOrder admin: Autocomplete for workspace, asset, task, assigned_to, requested_by

### Date Hierarchies
- WorkOrder: date_hierarchy on 'due' field (navigation by month/year)
- ActivityInstance: date_hierarchy on 'occurred_at' field

### Bulk Actions
- WorkOrder: Custom actions to mark as Open/Done/Cancelled (screenshot 24 shows 2 selected items)

## Notes

- All screenshots are full-page captures showing the complete admin interface
- Screenshots were captured with the Django server running at localhost:8000/admin/
- Sample data was created using the create_sample_data.py script
- The admin user was already logged in for all captures
- Timestamps in screenshots reflect January 2026 (server time: UTC-5)
