import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth_token")?.value;

  // Definimos qué rutas queremos proteger explícitamente en el servidor
  const protectedRoutes = ["/admin", "/messages", "/posts/create"];
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

  if (isProtectedRoute) {
    // Si no hay token, redirigimos a /login incluyendo el parámetro ?next=
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }

    try {
      // Validamos el token contra el backend
      const res = await fetch("https://scouta-production.up.railway.app/api/v1/auth/me", {
        headers: { "Authorization": `Bearer ${token}` },
      });

      if (!res.ok) {
        const loginUrl = new URL("/login", request.url);
        loginUrl.searchParams.set("next", pathname);
        return NextResponse.redirect(loginUrl);
      }

      const user = await res.json();

      // Regla especial para /admin
      if (pathname.startsWith("/admin") && !user.is_superuser) {
        return NextResponse.redirect(new URL("/", request.url));
      }
    } catch (error) {
      // En caso de error de red o backend caído, enviamos a login por seguridad
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("next", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  // Asegúrate de que el matcher incluya todas las rutas que quieres proteger
  matcher: ["/admin/:path*", "/messages/:path*", "/posts/create"],
};