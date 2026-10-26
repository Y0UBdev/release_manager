from models import Release

ALLOWED_TRANSITIONS = {
    # Author
    Release.Status.DRAFT:     {Release.Status.SUBMITTED, Release.Status.CANCELLED},
    Release.Status.SUBMITTED: {Release.Status.APPROVED, Release.Status.REJECTED, Release.Status.CANCELLED},
    Release.Status.CANCELLED: set(),
    
    # Approver
    Release.Status.APPROVED:  set(),
    Release.Status.REJECTED:  set(),
}