/**
 * Lightweight session helpers.
 *
 * In production replace the base64 encoding with a proper JWT signed with
 * NEXTAUTH_SECRET (e.g. using the `jose` library).
 */

import type { UserRole } from "@/types";

const COOKIE_NAME = "medpilot_session";
// 8 hours
const MAX_AGE = 60 * 60 * 8;

interface SessionPayload {
  role: UserRole;
  userId: string;
  name: string;
}

/** Encode a session payload into a base64 cookie value */
export function encodeSession(payload: SessionPayload): string {
  return btoa(encodeURIComponent(JSON.stringify(payload)));
}

export function decodeSession(value: string): SessionPayload {
  return JSON.parse(decodeURIComponent(atob(value)));
}

/** Set the session cookie (client-side) */
export function setSessionCookie(payload: SessionPayload): void {
  document.cookie = [
    `${COOKIE_NAME}=${encodeSession(payload)}`,
    `Max-Age=${MAX_AGE}`,
    "Path=/",
    "SameSite=Strict",
    // Add `Secure` in production
  ].join("; ");
}

/** Clear the session cookie */
export function clearSessionCookie(): void {
  document.cookie = `${COOKIE_NAME}=; Max-Age=0; Path=/`;
}
