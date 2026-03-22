import { redirect } from "next/navigation";

// The root always redirects to login.
// After login, the server action / middleware routes by role.
export default function RootPage() {
  redirect("/auth/login");
}
