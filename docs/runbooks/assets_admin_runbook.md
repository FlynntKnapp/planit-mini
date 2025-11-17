# Assets Admin Runbook

**App:** `assets`  
**Audience:** Project maintainers, admins, and power users  
**Admin URLs (default):**
- Form Factors: `/admin/assets/formfactor/`
- Operating Systems (OS): `/admin/assets/os/`
- Applications: `/admin/assets/application/`
- Projects: `/admin/assets/project/`
- Assets: `/admin/assets/asset/`

This runbook describes how to manage asset-related data in the Django admin and the intended workflows.

---

## 1. Domain Overview

### 1.1. Workspace (from `core`)
Assets and projects belong to a **Workspace** (defined in `core.models.Workspace`).  
Think of a workspace as a “tenant” or “environment” boundary (e.g., *Home Lab*, *Client A*, *Production*).

- `Project.workspace` → which workspace the project belongs to.
- `Asset.workspace` → which workspace the asset belongs to.

### 1.2. Projects

**Model:** `assets.models.Project`

Represents a logical grouping of assets (e.g., *Pi Cluster*, *Media Server*, *Home Automation*).

Key fields:
- `workspace` – required. ForeignKey to `Workspace`.
- `name` – human-readable name.
- `description` – optional text details.
- `slug` – URL-friendly identifier, unique within a workspace.

Uniqueness:
- `(workspace, slug)` is unique.  
  Two workspaces can have the same project slug, but a single workspace cannot have two projects with the same slug.

### 1.3. Assets

**Model:** `assets.models.Asset`

Represents individual pieces of hardware (Pi, servers, laptops) and their software.

Key fields:
- `workspace` – required. ForeignKey to `Workspace`.
- `project` – optional. ForeignKey to `Project`. Use this to group assets into a project.
- `name` – human-readable asset name.
- `kind` – type of asset (choices):
  - `PI` – Raspberry Pi
  - `SRV` – Server
  - `LAP` – Laptop
- `form_factor` – optional ForeignKey to `FormFactor` (e.g., *Mini-tower*, *1U rackmount*).
- `os` – optional ForeignKey to `OS`.
- `applications` – ManyToMany to `Application`.
- `location` – free-form text (e.g., *rack 1U3*, *office desk*, *living room*).
- `purchase_date` / `warranty_expires` – optional dates.
- `notes` – free-form notes (maintenance history, serial numbers, etc.).

### 1.4. Form Factors

**Model:** `assets.models.FormFactor`

Basic catalog of physical form factors.

Fields:
- `name` – display name.
- `slug` – unique slug, auto-populated from `name` in the admin.

### 1.5. Operating Systems (OS)

**Model:** `assets.models.OS`

Represents operating systems you install on assets.

Fields:
- `name` – e.g., *Raspberry Pi OS*, *Ubuntu Server*.
- `version` – optional (e.g., *24.04*, *Bookworm*).
- `slug` – unique slug, auto-populated from `name`.

### 1.6. Applications

**Model:** `assets.models.Application`

Represents software/services installed on assets.

Fields:
- `name` – e.g., *Home Assistant*, *Plex*, *PostgreSQL*.
- `version` – optional.
- `slug` – unique slug, auto-populated from `name`.

---

## 2. Admin: FormFactor

**Admin class:** `FormFactorAdmin`  
**URL:** `/admin/assets/formfactor/`

### 2.1. What you see

- **List columns (`list_display`)**:
  - `name`
  - `slug`

- **Search fields**:
  - `name`

- **Slug behavior**:
  - `prepopulated_fields = {"slug": ("name",)}`  
    When creating/editing, the `slug` will auto-fill from `name`.

### 2.2. Usage

- Create a **FormFactor** when you introduce a new physical category of hardware:
  - Examples: *Raspberry Pi 4 Model B*, *NUC*, *1U Rack Server*, *Laptop 15"*.
- Use the same `FormFactor` across multiple assets to make filtering/reporting easier later.

### 2.3. Conventions

- `name`: human-readable, capitalized.
- `slug`: auto-generated; only edit if you really need a specific slug. It must be unique.

---

## 3. Admin: OS

**Admin class:** `OSAdmin`  
**URL:** `/admin/assets/os/`

### 3.1. What you see

- **List columns**:
  - `name`
  - `version`
  - `slug`

- **Filters (`list_filter`)**:
  - `name` – filter by OS name.

- **Search fields**:
  - `name`
  - `version`

- **Slug behavior**:
  - `prepopulated_fields = {"slug": ("name",)}`

### 3.2. Usage

- Add one entry per OS “family + major version” you care about.
  - Example rows:
    - *Raspberry Pi OS* / *Bookworm*
    - *Ubuntu Server* / *24.04*
    - *Debian* / *12*
- Attach an OS to each asset that actually runs that OS. If unknown, you can leave `os` blank on the asset.

### 3.3. Conventions

- `name`: OS family (*Ubuntu Server*, *Raspberry Pi OS*, *Debian*).
- `version`: version label clearly identifying that OS line (*22.04 LTS*, *Bookworm*).

---

## 4. Admin: Application

**Admin class:** `ApplicationAdmin`  
**URL:** `/admin/assets/application/`

### 4.1. What you see

- **List columns**:
  - `name`
  - `version`
  - `slug`

- **Search fields**:
  - `name`
  - `version`

- **Slug behavior**:
  - `prepopulated_fields = {"slug": ("name",)}`

### 4.2. Usage

- Add entries for software/services you care about tracking across assets:
  - *Home Assistant*, *Plex*, *NGINX*, *PostgreSQL*, *Redis*, etc.
- Attach them to assets via the `applications` field (ManyToMany).

### 4.3. Conventions

- Avoid duplicating the same application with slightly different names.
  - Good: `Home Assistant` / `2025.2`
  - Less ideal: `home-assistant` and `Home Assistant` as separate rows.
- Use `version` when you care about tracking it; otherwise leave blank.

---

## 5. Admin: Project

**Admin class:** `ProjectAdmin`  
**URL:** `/admin/assets/project/`

### 5.1. What you see

- **List columns**:
  - `name`
  - `workspace`
  - `slug`

- **Filters (`list_filter`)**:
  - `workspace`

- **Search fields**:
  - `name`
  - `description`
  - `slug`

- **Slug behavior**:
  - `prepopulated_fields = {"slug": ("name",)}`

- **Field behavior**:
  - `raw_id_fields = ("workspace",)`
    - In the admin form, `workspace` is selected via a raw ID widget.  
      Use the magnifying-glass lookup to search.

- **Ordering**:
  - `ordering = ("workspace", "name")`

### 5.2. Usage

Typical workflow:

1. Ensure the corresponding **Workspace** exists (via `core` admin).
2. In **Projects** admin:
   - Click “Add Project”.
   - Choose `workspace` (using the raw ID lookup).
   - Fill `name`, `description`.
   - `slug` will auto-populate; adjust only if needed.
3. Save the project, then link assets to it (on the Asset admin page).

Projects are optional for assets: an asset may belong directly to a workspace without a project.

### 5.3. Gotchas

- `(workspace, slug)` must be unique.
  - If you see a validation error about duplicate slug, change it to something like `pi-cluster-primary` vs `pi-cluster-backup`.
- Changing `workspace` on a project effectively “moves” all associated assets to a different logical grouping (if you also update them). Be cautious.

---

## 6. Admin: Asset

**Admin class:** `AssetAdmin`  
**URL:** `/admin/assets/asset/`

### 6.1. What you see

- **List columns (`list_display`)**:
  - `name`
  - `workspace`
  - `project`
  - `kind`
  - `form_factor`
  - `os`
  - `location`
  - `purchase_date`
  - `warranty_expires`

- **Filters (`list_filter`)**:
  - `workspace`
  - `kind`
  - `form_factor`
  - `os`
  - `location`
  - `purchase_date`
  - `warranty_expires`

- **Search fields**:
  - `name`
  - `location`
  - `notes`
  - `workspace__name`
  - `project__name`

- **Field behavior**:
  - `raw_id_fields = ("workspace", "project", "form_factor", "os")`
    - Use magnifying-glass lookup for these relations when editing.
  - `filter_horizontal = ("applications",)`
    - Applications attached to the asset are managed with a dual-list selector.

- **Date behavior**:
  - `date_hierarchy = "purchase_date"`
    - Across the top of the changelist, you can drill down by year/month/day based on `purchase_date`.

- **Performance**:
  - `list_select_related = ("workspace", "project", "form_factor", "os")`
    - Admin prefetches these relationships to reduce queries on the changelist page.

- **Ordering**:
  - `ordering = ("workspace", "name")`

### 6.2. Typical workflows

#### 6.2.1. Adding a new asset

1. Make sure supporting catalog items exist:
   - **Workspace** (core admin).
   - Optional: **Project**, **FormFactor**, **OS**, **Application** entries.
2. Go to `/admin/assets/asset/add/`.
3. Choose **Workspace** (lookup).
4. Optionally choose **Project** (lookup).
5. Set **name**, **kind**, **form_factor**, **os`.
6. Set **location**, **purchase_date**, **warranty_expires` (if known).
7. Add notes as needed (maintenance info, serial numbers, etc.).
8. Save.
9. After saving, use the **Applications** horizontal filter to assign installed applications.

#### 6.2.2. Updating software installed on an asset

1. Edit the asset.
2. Use the horizontal **Applications** selector to add/remove applications.
3. Optionally update the OS version by editing the OS record (if your OS model uses version) and/or linking the asset to a newer OS entry.

#### 6.2.3. Finding assets quickly

- Use **filters**:
  - Filter by `workspace` to isolate a tenant/environment.
  - Filter by `kind` to see all Pis, servers, or laptops.
  - Filter by `form_factor` to find all 1U servers, etc.
- Use **search**:
  - Search by `name` (asset names).
  - Search by `location` (rack, room, etc.).
  - Search by `notes` (serial numbers or custom tags).
  - Search by related workspace/project names (`workspace__name`, `project__name`).

#### 6.2.4. Warranty review

- Use filters on `warranty_expires` and the **date hierarchy** on `purchase_date`:
  - Filter “warranty_expires” by a particular year or blank to find assets without warranty info.
  - Navigate via date hierarchy to see assets purchased in specific periods.

---

## 7. Operational Tips & Conventions

1. **Workspaces first**  
   Always create/update **Workspace** entries (in `core` admin) before projects and assets. It’s the top-level container.

2. **Catalog hygiene (FormFactor/OS/Application)**  
   Keep catalogs clean:
   - Avoid duplicate names with different casing/spelling.
   - Prefer “family + version” pattern (e.g., *Ubuntu Server* / *22.04 LTS*).

3. **Slug stability**  
   - Let admin auto-populate slugs.
   - Avoid editing slugs once in active use to prevent confusion in URLs, scripts, or any references that rely on them.

4. **Using raw ID fields**  
   - The magnifying glass next to `workspace`, `project`, `form_factor`, and `os` opens a popup search.
   - This is more efficient than long dropdowns when you have many records.

5. **Performance and list views**  
   - `list_select_related` is already configured to avoid N+1 queries for common foreign keys.
   - If the list view becomes slow with many assets, prefer filtering by `workspace` or `kind` to narrow results.

---

## 8. Troubleshooting

### 8.1. “This slug already exists” errors

- For **Project**:
  - Remember `(workspace, slug)` must be unique.
  - Change the slug for the new project (`pi-cluster-primary`, `pi-cluster-backup`).

- For `FormFactor`, `OS`, `Application`:
  - `slug` is globally unique.
  - If you get a conflict, adjust the name/slug slightly (e.g., `ubuntu-server-22-04-lts`).

### 8.2. Asset cannot be linked to a Project

- Make sure the `Project.workspace` matches the `Asset.workspace`.
- If they differ, either:
  - Move the project to the asset’s workspace (if appropriate), or
  - Move the asset to the project’s workspace, or
  - Create a project in the correct workspace.

### 8.3. “Why can’t I see my workspace in the dropdown?”

- On the asset/project forms, `workspace` uses a **raw ID** widget:
  - Click the magnifying glass.
  - Search for the workspace by name.
- If it truly doesn’t exist, you need to add it in the **core** admin for `Workspace`.

---

## 9. Change Management

When modifying admin behavior:

- For small tweaks (e.g., adding a new `list_filter`):
  - Update `assets/admin.py`.
  - Run tests (including admin tests, if present).
- For field or model changes:
  - Update `assets/models.py`.
  - Generate and run migrations.
  - Review this runbook and update any sections that reference changed fields or workflows.

Keep this runbook updated alongside changes to `assets/models.py` and `assets/admin.py`.
