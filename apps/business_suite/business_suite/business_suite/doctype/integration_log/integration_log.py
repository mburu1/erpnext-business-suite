import frappe
from frappe import _
from frappe.model.document import Document

from business_suite.permissions import ensure_document_permission
from business_suite.utils.validation import require_non_negative
from business_suite.workflow import enforce_transition, record_transition


class IntegrationLog(Document):
    def before_insert(self):
        ensure_document_permission(self, "create")

    def before_save(self):
        if not self.is_new():
            ensure_document_permission(self, "write")
        enforce_transition(self)

    def on_trash(self):
        ensure_document_permission(self, "delete")

    def validate(self):
        self._validate_required_context()
        self._validate_http_status()
        self._validate_duration()
        self._validate_processing_state()

    def after_save(self):
        record_transition(self)

    def _validate_required_context(self):
        if not self.integration_name:
            frappe.throw(_("Integration Name is required."))

        if not self.direction:
            frappe.throw(_("Direction is required."))

        if not self.status:
            frappe.throw(_("Status is required."))

    def _validate_http_status(self):
        if self.http_status is None:
            return

        if self.http_status < 100 or self.http_status > 599:
            frappe.throw(_("HTTP Status must be between 100 and 599."))

    def _validate_duration(self):
        require_non_negative(self.duration_ms, _("Duration"))

    def _validate_processing_state(self):
        if self.status in {"Completed", "Failed"} and not self.processed_at:
            frappe.throw(
                _("Processed At is required when Integration Log status is {0}.").format(
                    self.status
                )
            )

        if self.status == "Failed" and not self.error_code:
            frappe.throw(_("Error Code is required for a failed integration."))

        if self.status == "Completed" and self.error_code:
            frappe.throw(_("Completed integrations cannot contain an Error Code."))
