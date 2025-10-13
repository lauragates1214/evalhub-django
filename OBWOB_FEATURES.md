# Features to Adapt for Obwob

## Survey Permissions
**EvalHub:** Simple ownership - only the survey creator can view/edit
**Obwob:** Organisation-wide permissions
- Default: All org members can view/edit surveys
- Optional: Restrict to specific users/teams
- Implementation: Replace `survey.owner != request.user` check with org membership check
- Files to update: `instructors/views.py` (survey_detail, survey_responses, etc.)

**Code pattern in EvalHub:**
```python
if survey.owner != request.user:
    return HttpResponseForbidden()
Will become:
pythonif not user.can_access_survey(survey):
    return HttpResponseForbidden()