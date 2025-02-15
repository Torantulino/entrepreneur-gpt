import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

// TODO: Update the protected pages list
const PROTECTED_PAGES = [
  "/monitor",
  "/build",
  "/marketplace/profile",
  "/marketplace/settings",
  "/marketplace/dashboard",
  "/onboarding",
];
const ADMIN_PAGES = ["/admin"];

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const isAvailable = Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  );

  if (!isAvailable) {
    return supabaseResponse;
  }

  try {
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return request.cookies.getAll();
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              request.cookies.set(name, value),
            );
            supabaseResponse = NextResponse.next({
              request,
            });
            cookiesToSet.forEach(({ name, value, options }) =>
              supabaseResponse.cookies.set(name, value, options),
            );
          },
        },
      },
    );

    // IMPORTANT: Avoid writing any logic between createServerClient and
    // supabase.auth.getUser(). A simple mistake could make it very hard to debug
    // issues with users being randomly logged out.

    const {
      data: { user },
      error,
    } = await supabase.auth.getUser();

    // Get the user role
    const userRole = user?.role;
    const url = request.nextUrl.clone();
    const pathname = request.nextUrl.pathname;
    // AUTH REDIRECTS
    // If not logged in and trying to access a protected page, redirect to login
    if (
      (!user &&
        PROTECTED_PAGES.some((page) => {
          const combinedPath = `${page}`;
          // console.log("Checking pathname:", request.nextUrl.pathname, "against:", combinedPath);
          return request.nextUrl.pathname.startsWith(combinedPath);
        })) ||
      ADMIN_PAGES.some((page) => {
        const combinedPath = `${page}`;
        // console.log("Checking pathname:", request.nextUrl.pathname, "against:", combinedPath);
        return request.nextUrl.pathname.startsWith(combinedPath);
      })
    ) {
      // no user, potentially respond by redirecting the user to the login page
      url.pathname = `/login`;
      return NextResponse.redirect(url);
    }
    if (
      user &&
      userRole != "admin" &&
      ADMIN_PAGES.some((page) => request.nextUrl.pathname.startsWith(`${page}`))
    ) {
      // no user, potentially respond by redirecting the user to the login page
      url.pathname = `/marketplace`;
      return NextResponse.redirect(url);
    }

    // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
    // creating a new response object with NextResponse.next() make sure to:
    // 1. Pass the request in it, like so:
    //    const myNewResponse = NextResponse.next({ request })
    // 2. Copy over the cookies, like so:
    //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
    // 3. Change the myNewResponse object to fit your needs, but avoid changing
    //    the cookies!
    // 4. Finally:
    //    return myNewResponse
    // If this is not done, you may be causing the browser and server to go out
    // of sync and terminate the user's session prematurely!
  } catch (error) {
    console.error("Failed to run Supabase middleware", error);
  }

  return supabaseResponse;
}
