"use client"

import { useState } from "react"
import axios from "axios"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function Home() {
  const [category, setCategory] = useState("economics")
  const [minutes, setMinutes] = useState(5)
  const [audio, setAudio] = useState(false)
  const [loading, setLoading] = useState(false)
  const [digest, setDigest] = useState(null)

  const categories = ["economics", "sports", "politics", "technology", "general"]
  const timeOptions = [5, 10, 20, 30, 60]

  async function fetchDigest() {
    setLoading(true)
    setDigest(null)
    try {
      const res = await axios.post("http://localhost:8000/api/digest", {
        category,
        minutes,
        language: "en",
        audio,
      })
      setDigest(res.data)
    } catch (err) {
      console.error(err)
      alert("Error fetching digest - check backend logs")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container mx-auto max-w-3xl px-4 py-8">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight text-balance">QuickDigest</h1>
        <p className="text-muted-foreground mt-1">Get a concise news digest tailored to your time.</p>
      </header>

      {/* Controls */}
      <Card className="mb-6">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl">Preferences</CardTitle>
          <CardDescription>Choose a category, set your time, and optionally include audio.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">

            {/* Category */}
            <div className="flex flex-col gap-2">
              <span className="text-sm font-medium leading-none">Category</span>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger id="category" aria-label="Select category">
                  <SelectValue placeholder="Pick a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((c) => (
                    <SelectItem key={c} value={c}>
                      {c[0].toUpperCase() + c.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Time */}
            <div className="flex flex-col gap-2">
              <span className="text-sm font-medium leading-none">Time</span>
              <Select value={String(minutes)} onValueChange={(v) => setMinutes(Number.parseInt(v))}>
                <SelectTrigger id="minutes" aria-label="Select minutes">
                  <SelectValue placeholder="Select time" />
                </SelectTrigger>
                <SelectContent>
                  {timeOptions.map((t) => (
                    <SelectItem key={t} value={String(t)}>
                      {t} min
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Audio Switch */}
            <div className="flex items-center justify-between rounded-md border p-3 md:col-span-2">
              <div className="flex flex-col">
                <span className="text-sm font-medium leading-none">Listen?</span>
                <span className="text-muted-foreground text-sm">Include a generated audio version</span>
              </div>

              {/* ✅ Custom Toggle Switch */}
              <button
                type="button"
                role="switch"
                aria-checked={audio}
                onClick={() => setAudio(!audio)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 ${
                  audio ? "bg-primary" : "bg-muted"
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-background transition-transform duration-300 ${
                    audio ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </div>
        </CardContent>

        <CardFooter className="justify-end">
          <Button onClick={fetchDigest} disabled={loading}>
            {loading ? "Preparing..." : "Get Digest"}
          </Button>
        </CardFooter>
      </Card>

      {/* Results */}
      {digest && (
        <section aria-live="polite" aria-busy={loading} className="space-y-4">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">
              {digest.category[0].toUpperCase() + digest.category.slice(1)} — {digest.minutes} min digest
            </h2>
          </div>

          {digest.audio_url && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Audio</CardTitle>
                <CardDescription>Listen to this digest while you work.</CardDescription>
              </CardHeader>
              <CardContent>
                <audio controls src={`http://localhost:8000${digest.audio_url}`} className="w-full">
                  Your browser does not support the audio element.
                </audio>
              </CardContent>
            </Card>
          )}

          <ul className="grid gap-4">
            {digest.summaries.map((s, i) => (
              <li key={i}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xl text-pretty">
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-sm"
                      >
                        {s.title}
                      </a>
                    </CardTitle>
                    <CardDescription className="text-sm">
                      <span>{s.source}</span>
                      <span className="px-2">—</span>
                      <time aria-label="Published date">{s.published}</time>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-pretty">{s.summary}</p>
                  </CardContent>
                  <CardFooter className="justify-end">
                    <Button variant="secondary" asChild>
                      <a href={s.url} target="_blank" rel="noreferrer">
                        Read full story
                      </a>
                    </Button>
                  </CardFooter>
                </Card>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}
