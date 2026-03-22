/**
 * Next.js Middleware — Route Protection
 * ─────────────────────────────────────────────────────────────────────────────
 * Runs on every request before the page renders.
 *
 * Rules:
 *   /doctor/*  → requires role === "doctor"
 *   /patient/* → requires role === "patient"
 *   /auth/*    → public (always accessible)
 *   /api/*     → public (auth handled by the API itself)
 *
 * Auth state is read from the "medpilot-auth" cookie that Zustand persist
 * writes to localStorage. Because middleware runs on the Edge runtime
 * (no localStorage access), we use a lightweight session cookie instead.
 *
 * Flow:
 *   1. On login, `src/app/auth/login/page.tsx` sets a signed session cookie.
 *   2. Middleware reads the cookie and checks the role.
 *   3. Unauthenticated → redirect /auth/login
 *   4. Wrong role      → redirect to the correct dashboard
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { type NextRequest, NextResponse } from "next/server";
import { decodeSession } from "./lib/utils/session";

/** Cookie name — must match what the login page sets */
const SESSION_COOKIE = "medpilot_session";

interface SessionPayload {
  role: "doctor" | "patient";
}

/** Minimal cookie parser (no JWT in demo — swap for real JWT verify in prod) */
function parseSession(req: NextRequest): SessionPayload | null {
  const raw = req.cookies.get(SESSION_COOKIE)?.value;
  if (!raw) return null;
  try {
    return decodeSession(raw) as SessionPayload;
  } catch {
    return null;
  }
}

export function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Always allow public routes
  if (
    pathname.startsWith("/auth") ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon")
  ) {
    return NextResponse.next();
  }

  const session = parseSession(req);

  // Not authenticated → login
  if (!session) {
    const loginUrl = req.nextUrl.clone();
    loginUrl.pathname = "/auth/login";
    return NextResponse.redirect(loginUrl);
  }

  // Doctor trying to access patient routes (or vice versa) → redirect
  if (pathname.startsWith("/doctor") && session.role !== "doctor") {
    const redirect = req.nextUrl.clone();
    redirect.pathname = "/patient/chat";
    return NextResponse.redirect(redirect);
  }

  if (pathname.startsWith("/patient") && session.role !== "patient") {
    const redirect = req.nextUrl.clone();
    redirect.pathname = "/doctor/scribe";
    return NextResponse.redirect(redirect);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static  (static files)
     * - _next/image   (image optimization)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
