# NAVIGATION FLOW (from Figma Prototype)

# NAVIGATION FLOW — BioAI Hub

## 1. GLOBAL ROUTING STRUCTURE

### Public Routes (No Authentication Required)

- `/` → Home (Landing)
- `/explore` → Explore Resources (public)
- `/resources/:id` → Resource Detail (public view)
- `/resources/:id/versions/:versionId` → Specific Version View (public)

### Authenticated Routes (Login Required)

- `/publish` → Publish Resource
- `/resources/:id/edit` → Edit Resource (owner/admin only)
- `/profile` → My Profile
- `/profile/:id` → Public Profile View
- `/notifications` → User Notifications

### Admin Privileged Actions

- Validate any resource version
- Edit any resource
- Delete any resource


---

# 2. PUBLIC FLOW

## Start: Home (/)

User state: Not authenticated (default)

Actions:

- Click "Explore Resources"
  → Redirect to `/explore`

- Click "Publish Resource"
  → Redirect to `/login`
  → After login → `/publish`

- Click "Sign In"
  → Redirect to `/login`

- Click Featured Resource
  → Redirect to `/resources/:id`


---

# 3. EXPLORE FLOW (Public)

Route: `/explore`

User state:
- Anonymous OR Authenticated

Capabilities:

- Search resources
- Filter by type
- Open Resource Detail

Actions:

- Click Resource Card
  → `/resources/:id`

- Click "+ Publish Resource"
  → If not authenticated → `/login`
  → If authenticated → `/publish`

Notes:
- Explore is fully readable without login.
- Interaction actions require authentication.


---

# 4. RESOURCE DETAIL FLOW

Route: `/resources/:id`

User state variations:

## A) Anonymous User

Allowed:
- View description
- View tags
- View author
- View metrics
- View versions
- View discussion (read-only)

Blocked:
- Upvote
- Reuse
- Edit
- Delete
- Validate
- Start Discussion

CTA behavior:
- Show "Sign in to interact"

---

## B) Authenticated User (Not Owner)

Allowed:
- Upvote (1 per user)
- Reuse (fork)
- Start discussion
- Comment

Blocked:
- Edit
- Delete
- Validate (unless Admin)

---

## C) Owner

Allowed:
- Edit resource
- Delete resource
- Reuse
- Upvote
- View version history

Behavior:
- Editing creates new version if previous version was validated.
- Validation remains tied to validated version only.

---

## D) Admin

Allowed:
- Edit any resource
- Delete any resource
- Validate any version
- Override validation state

---

# 5. REUSE (FORK) FLOW

Precondition: User must be authenticated.

Route Trigger:
- Click "Reuse This Resource"

System Behavior:

1. Create new Resource:
   - owner = current user
   - derived_from_resource_id
   - derived_from_version_id

2. Create initial ResourceVersion for the new resource.

3. Redirect to:
   → `/resources/:newId/edit`

User then:
- Edits content
- Publishes version
- Requests validation

Traceability:
- New resource shows "Derived from: [Original Resource]"
- Original resource may show "Forked X times" (optional MVP)


---

# 6. PUBLISH FLOW

Route: `/publish`

Precondition:
- User authenticated

Steps:

1. Fill form:
   - Title
   - Description
   - Resource Type
   - Status (Sandbox / Request Validation)
   - GitHub link (optional)
   - Tags

2. Click "Publish"

Outcomes:

- Success:
  → Create Resource
  → Create Version v1
  → Redirect to `/resources/:id`

- Validation error:
  → Stay on page
  → Show inline errors

- Backend error:
  → Toast error message


---

# 7. EDIT FLOW

Route: `/resources/:id/edit`

Precondition:
- Owner or Admin

Behavior:

If last version is NOT validated:
- Update creates new draft version

If last version IS validated:
- Create new version (vNext)
- Status = Sandbox / Pending Validation
- Previous validated version remains validated

After save:
→ Redirect to `/resources/:id`
→ Show banner:
  "New version created. Validation required."


---

# 8. DELETE FLOW

Precondition:
- Owner or Admin

Behavior:
- Soft delete recommended
- Remove from Explore listings
- Keep audit trail

After delete:
→ Redirect to `/explore`


---

# 9. UPVOTE FLOW

Precondition:
- User authenticated

Rules:
- 1 vote per user per resource
- Toggle optional (define later)

On success:
- Increment vote count
- Trigger notification to resource owner (optional MVP)


---

# 10. VALIDATION FLOW

Precondition:
- Admin (or future reviewer role)

Route:
- Action from Resource Detail

Behavior:
- Validation tied to specific version
- Change status to "Validated"
- Create notification for resource owner


---

# 11. PROFILE FLOW

Routes:

- `/profile` (own profile)
- `/profile/:id` (public profile)

Sections:
- Reputation
- Contributions
- Validations made
- Total impact
- Published resources
- Validated resources

Actions:
- Click resource → `/resources/:id`


---

# 12. NOTIFICATIONS FLOW

Route: `/notifications`

Precondition:
- User authenticated

Types (MVP):

- Resource validated
- New version created (owner notification optional)
- New upvote (optional MVP)
- Fork created from your resource

States:
- Unread
- Read
- Empty state
- Error loading


---

# 13. GLOBAL BEHAVIOR

- Sidebar persists across authenticated routes.
- Active route highlighted.
- Unauthorized access → Redirect to `/login`
- After login → Return to intended route.
- Versioning is per ResourceVersion.
- Validation is per version, not per resource.

