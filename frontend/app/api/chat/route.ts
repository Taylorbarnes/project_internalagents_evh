import { NextResponse } from "next/server"

export async function POST(req: Request) {
  const baseUrl = process.env.BOOKING_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL
  const apiKey = process.env.BOOKING_API_KEY

  if (!baseUrl) {
    return NextResponse.json({ success: false, error: "Missing BOOKING_API_URL" }, { status: 500 })
  }

  try {
    const body = await req.json()
    const res = await fetch(`${baseUrl.replace(/\/$/, "")}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}),
      },
      body: JSON.stringify(body),
    })

    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Upstream error" }, { status: 502 })
  }
}


