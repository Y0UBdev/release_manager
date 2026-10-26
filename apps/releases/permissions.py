
READER = "Reader"
AUTHOR = "Author"
APPROVER = "Approver"
EXECUTOR = "Executor"

ROLES = {
    READER:   ["view_release"],
    AUTHOR:   ["view_release", "add_release", "change_release", "submit_release"],
    APPROVER: ["view_release", "approve_release"],
    EXECUTOR: ["view_release", "execute_release"],
}