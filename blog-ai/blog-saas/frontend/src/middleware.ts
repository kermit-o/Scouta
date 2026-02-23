import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/admin")) {
    const token = request.cookies.get("auth_token")?.value;
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    try {
      const res = await fetch("https://scouta-production.up.railway.app/api/v1/auth/me", {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (!res.ok) {
        return NextResponse.redirect(new URL("/login", request.url));
      }
      const user = await res.json();
      if (!user.is_superuser) {
        return NextResponse.redirect(new URL("/", request.url));
      }
    } catch {
      return NextResponse.redirect(new URL("/", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin", "/admin/:path*"],
};
