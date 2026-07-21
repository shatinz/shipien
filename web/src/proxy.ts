import { NextRequest, NextResponse } from 'next/server';
import { jwtVerify } from 'jose';

const secret = new TextEncoder().encode(
  process.env.JWT_SECRET || 'fallback-secret-change-in-production'
);

const PROTECTED_PATHS = ['/dashboard', '/vpn'];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + '/')
  );

  if (!isProtected) return NextResponse.next();

  const token = request.cookies.get('auth_token')?.value;

  if (!token) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('from', pathname);
    return NextResponse.redirect(loginUrl);
  }

  try {
    await jwtVerify(token, secret);
    return NextResponse.next();
  } catch {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('from', pathname);
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete('auth_token');
    return response;
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/vpn/:path*'],
};
