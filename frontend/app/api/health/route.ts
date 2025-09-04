import { NextResponse } from "next/server"

export async function GET() {
  const baseUrl = process.env.BOOKING_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL
  if (!baseUrl) {
    return NextResponse.json({ error: "Missing BOOKING_API_URL" }, { status: 500 })
  }

  try {
    const res = await fetch(`${baseUrl.replace(/\/$/, "")}/health`)
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (error) {
    return NextResponse.json({ error: "Upstream unreachable" }, { status: 502 })
  }
}


