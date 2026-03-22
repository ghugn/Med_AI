// All runtime configuration lives here.
// Components import from @/config, never from process.env directly.

export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",

  /** When true, services return mock data instead of hitting real endpoints */
  mockApi: process.env.NEXT_PUBLIC_MOCK_API === "true",

  features: {
    imageUpload: process.env.NEXT_PUBLIC_ENABLE_IMAGE_UPLOAD === "true",
  },

  api: {
    scribe:   "/api/scribe",
    reminder: "/api/reminder",
    chat:     "/api/chat",
  },

  schemaVersion: "0.1",
} as const;
