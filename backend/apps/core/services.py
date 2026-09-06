"""Audit logging helper.

Writes concise, sensitive-free audit records for important administrative
actions. Kept intentionally small so it can be swapped for a full audit
service / SIEM later without touching call sites.
"""
import logging

audit_logger = logging.getLogger("voice.audit")


def audit(user, action, detail=None):
    if user is None or not user.is_authenticated:
        actor = "anonymous"
    else:
        actor = f"{user.email} ({getattr(user, 'role', '?')})"
    audit_logger.info("action=%s actor=%s detail=%s", action, actor, detail or "-")