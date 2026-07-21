import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcryptjs';
import { prisma } from '@/lib/prisma';
import { signToken, setSessionCookie } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const { username, phone, password } = await request.json();

    if (!username || !phone || !password) {
      return NextResponse.json({ error: 'All fields are required' }, { status: 400 });
    }

    if (username.length < 3 || username.length > 32) {
      return NextResponse.json({ error: 'Username must be 3–32 characters' }, { status: 400 });
    }

    const existing = await prisma.user.findUnique({ where: { username } });
    if (existing) {
      return NextResponse.json({ error: 'Username already taken' }, { status: 409 });
    }

    const passwordHash = await bcrypt.hash(password, 12);
    const user = await prisma.user.create({
      data: { username, phone, passwordHash },
    });

    const token = await signToken({ userId: user.id, username: user.username });
    await setSessionCookie(token);

    return NextResponse.json({
      success: true,
      user: { id: user.id, username: user.username },
    });
  } catch (err) {
    console.error('Signup error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
