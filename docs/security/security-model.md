# Security Model

~~~text
User / API Client
       |
Authentication
       |
Frappe session / API credentials
       |
Role + DocType permissions
       |
Server-side validation
       |
Business operation
       |
Audit / integration logging
~~~

## Controls

### Authentication
Use Frappe-supported authentication/session mechanisms.

### Authorization
Enforce roles, DocType permissions and workflow permissions server-side.

### Data protection
- Keep secrets outside Git.
- Mask credentials/tokens in logs.
- Use TLS for external integrations.
- Restrict production configuration access.

### Input security
Treat API and Webhook data as untrusted input and validate it on the server.

### Auditability
Capture relevant actor, request and transition information.

## Review checklist

- [ ] No credentials in Git
- [ ] Least-privilege roles
- [ ] Server-side permission checks
- [ ] Input validation
- [ ] Secret masking
- [ ] TLS
- [ ] Webhook authenticity
- [ ] Duplicate-event protection
- [ ] Safe error responses
