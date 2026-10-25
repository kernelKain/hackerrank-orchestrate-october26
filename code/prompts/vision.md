Read this Northstar Shop admin screenshot. Copy only values that are visibly printed.

A resource id has one of these prefixes and then digits: account_, search_, support_, analytics_, backup_, export_, cache_, data_flow_, tombstone_, email_delivery_, audit_record_. Ignore order numbers, CS- ticket labels, and FIN- finance labels.

For each visible resource id, copy the email, phone, user id (user_ and digits), and email hash only when they are printed on that same record. Use an empty string when a value is not visible. Do not copy a value from a neighboring row, and do not invent an id from a name.

Set posture to present when the record is shown with stored personal data or an active profile, absent when the screen says it was not found or deleted, redacted when the record remains without direct identifiers, anonymized when it remains and shows no person, and unknown when you cannot tell.

If no resource id of the required form is visible, set nothing_identifiable to true and records to an empty array. An empty field is required when the screen does not show that value.
