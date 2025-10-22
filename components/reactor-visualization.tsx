"use client"

import { useEffect, useRef, useState } from "react"

interface ReactorVisualizationProps {
  parameters: Record<string, Record<string, number>>
}

interface Particle {
  progress: number
  path: "primary-hot" | "primary-cold" | "secondary"
}

export default function ReactorVisualization({ parameters }: ReactorVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [mounted, setMounted] = useState(false)
  const particlesRef = useRef<Particle[]>([])
  const animationFrameRef = useRef<number | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      const container = canvas.parentElement
      if (container) {
        canvas.width = container.clientWidth
        canvas.height = container.clientHeight
      }
    }
    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    // Initialize particles
    if (particlesRef.current.length === 0) {
      for (let i = 0; i < 40; i++) {
        particlesRef.current.push({
          progress: Math.random(),
          path: "primary-hot",
        })
      }
      for (let i = 0; i < 40; i++) {
        particlesRef.current.push({
          progress: Math.random(),
          path: "primary-cold",
        })
      }
      for (let i = 0; i < 30; i++) {
        particlesRef.current.push({
          progress: Math.random(),
          path: "secondary",
        })
      }
    }

    if (!ctx.roundRect) {
      ctx.roundRect = function (x: number, y: number, w: number, h: number, r: number) {
        this.beginPath()
        this.moveTo(x + r, y)
        this.lineTo(x + w - r, y)
        this.arcTo(x + w, y, x + w, y + r, r)
        this.lineTo(x + w, y + h - r)
        this.arcTo(x + w, y + h, x + w - r, y + h, r)
        this.lineTo(x + r, y + h)
        this.arcTo(x, y + h, x, y + h - r, r)
        this.lineTo(x, y + r)
        this.arcTo(x, y, x + r, y, r)
        this.closePath()
      }
    }

    const drawReactorVessel = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.beginPath()
      ctx.moveTo(-60 * scale, -100 * scale)
      ctx.lineTo(-60 * scale, 80 * scale)
      ctx.arc(0, 80 * scale, 60 * scale, Math.PI, 0, false)
      ctx.lineTo(60 * scale, -100 * scale)
      ctx.arc(0, -100 * scale, 60 * scale, 0, Math.PI, false)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      ctx.strokeStyle = "#666666"
      ctx.lineWidth = 1
      for (let i = -40; i <= 40; i += 5) {
        ctx.beginPath()
        ctx.moveTo(i * scale, -80 * scale)
        ctx.lineTo(i * scale, 60 * scale)
        ctx.stroke()
      }

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(0, -100 * scale, 60 * scale, 0, Math.PI, false)
      ctx.stroke()

      ctx.beginPath()
      ctx.arc(0, 80 * scale, 60 * scale, Math.PI, 0, false)
      ctx.stroke()

      ctx.fillStyle = "#3a3a3a"
      ctx.fillRect(60 * scale, -10 * scale, 30 * scale, 20 * scale)
      ctx.strokeRect(60 * scale, -10 * scale, 30 * scale, 20 * scale)

      ctx.restore()
    }

    const drawReactorCoolantPump = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.fillStyle = "#3a3a3a"
      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2

      ctx.beginPath()
      ctx.arc(0, 0, 30 * scale, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 1
      for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(Math.cos(angle) * 20 * scale, Math.sin(angle) * 20 * scale)
        ctx.stroke()
      }

      ctx.fillStyle = "#2a2a2a"
      ctx.fillRect(-15 * scale, -50 * scale, 30 * scale, 40 * scale)
      ctx.strokeRect(-15 * scale, -50 * scale, 30 * scale, 40 * scale)

      ctx.restore()
    }

    const drawSteamGenerator = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.beginPath()
      ctx.moveTo(-70 * scale, -150 * scale)
      ctx.lineTo(-70 * scale, 100 * scale)
      ctx.arc(0, 100 * scale, 70 * scale, Math.PI, 0, false)
      ctx.lineTo(70 * scale, -150 * scale)
      ctx.arc(0, -150 * scale, 70 * scale, 0, Math.PI, false)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      ctx.strokeStyle = "#555555"
      ctx.lineWidth = 1
      for (let i = -60; i <= 60; i += 8) {
        for (let j = -130; j <= 80; j += 8) {
          ctx.beginPath()
          ctx.moveTo(i * scale, j * scale)
          ctx.lineTo((i + 4) * scale, (j + 4) * scale)
          ctx.stroke()
        }
      }

      const hotGradient = ctx.createLinearGradient(0, 60 * scale, 0, 100 * scale)
      hotGradient.addColorStop(0, "rgba(255, 100, 0, 0.6)")
      hotGradient.addColorStop(1, "rgba(255, 150, 0, 0.4)")
      ctx.fillStyle = hotGradient
      ctx.fillRect(-65 * scale, 60 * scale, 130 * scale, 40 * scale)

      const transitionGradient = ctx.createLinearGradient(0, 0, 0, 60 * scale)
      transitionGradient.addColorStop(0, "rgba(100, 100, 255, 0.3)")
      transitionGradient.addColorStop(0.5, "rgba(150, 100, 200, 0.3)")
      transitionGradient.addColorStop(1, "rgba(255, 100, 100, 0.4)")
      ctx.fillStyle = transitionGradient
      ctx.fillRect(-65 * scale, 0, 130 * scale, 60 * scale)

      ctx.fillStyle = "rgba(100, 150, 255, 0.3)"
      ctx.fillRect(-65 * scale, -130 * scale, 130 * scale, 130 * scale)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#3a3a3a"
      ctx.fillRect(-15 * scale, -180 * scale, 30 * scale, 30 * scale)
      ctx.strokeRect(-15 * scale, -180 * scale, 30 * scale, 30 * scale)

      ctx.fillRect(-90 * scale, 70 * scale, 20 * scale, 20 * scale)
      ctx.strokeRect(-90 * scale, 70 * scale, 20 * scale, 20 * scale)

      ctx.fillRect(-90 * scale, -20 * scale, 20 * scale, 20 * scale)
      ctx.strokeRect(-90 * scale, -20 * scale, 20 * scale, 20 * scale)

      ctx.restore()
    }

    const drawTurbine = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.fillRect(-80 * scale, -50 * scale, 160 * scale, 100 * scale)
      ctx.strokeRect(-80 * scale, -50 * scale, 160 * scale, 100 * scale)

      ctx.strokeStyle = "#666666"
      ctx.lineWidth = 1
      for (let i = -60; i <= 60; i += 10) {
        ctx.beginPath()
        ctx.moveTo(i * scale, -40 * scale)
        ctx.lineTo((i + 5) * scale, 0)
        ctx.lineTo(i * scale, 40 * scale)
        ctx.stroke()
      }

      ctx.fillStyle = "#555555"
      ctx.fillRect(-90 * scale, -10 * scale, 180 * scale, 20 * scale)
      ctx.strokeRect(-90 * scale, -10 * scale, 180 * scale, 20 * scale)

      ctx.restore()
    }

    const drawCondenser = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.roundRect(-100 * scale, -80 * scale, 200 * scale, 160 * scale, 10 * scale)
      ctx.fill()
      ctx.stroke()

      const waterGradient = ctx.createLinearGradient(0, 40 * scale, 0, 80 * scale)
      waterGradient.addColorStop(0, "rgba(100, 150, 255, 0.6)")
      waterGradient.addColorStop(1, "rgba(80, 130, 255, 0.8)")
      ctx.fillStyle = waterGradient

      ctx.beginPath()
      ctx.moveTo(-100 * scale, 40 * scale)
      for (let i = -100; i <= 100; i += 10) {
        ctx.lineTo(i * scale, (40 + Math.sin(i * 0.1) * 3) * scale)
      }
      ctx.lineTo(100 * scale, 80 * scale)
      ctx.lineTo(-100 * scale, 80 * scale)
      ctx.closePath()
      ctx.fill()

      ctx.restore()
    }

    const drawGenerator = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"
      ctx.fillRect(-50 * scale, -50 * scale, 100 * scale, 100 * scale)
      ctx.strokeRect(-50 * scale, -50 * scale, 100 * scale, 100 * scale)

      ctx.fillStyle = "#ff4444"
      ctx.strokeStyle = "#ff4444"
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(-10 * scale, -30 * scale)
      ctx.lineTo(10 * scale, -5 * scale)
      ctx.lineTo(-5 * scale, -5 * scale)
      ctx.lineTo(15 * scale, 30 * scale)
      ctx.lineTo(-10 * scale, 5 * scale)
      ctx.lineTo(5 * scale, 5 * scale)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      ctx.restore()
    }

    const drawCondensateStorageTank = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#3388ff"
      ctx.fillRect(-80 * scale, -100 * scale, 160 * scale, 200 * scale)
      ctx.strokeRect(-80 * scale, -100 * scale, 160 * scale, 200 * scale)

      ctx.restore()
    }

    const drawPump = (x: number, y: number, scale: number) => {
      ctx.save()
      ctx.translate(x, y)

      ctx.strokeStyle = "#cccccc"
      ctx.lineWidth = 2
      ctx.fillStyle = "#3388ff"
      ctx.beginPath()
      ctx.arc(0, 0, 25 * scale, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      ctx.strokeStyle = "#ffffff"
      ctx.lineWidth = 2
      for (let i = 0; i < 4; i++) {
        const angle = (i / 4) * Math.PI * 2
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(Math.cos(angle) * 15 * scale, Math.sin(angle) * 15 * scale)
        ctx.stroke()
      }

      ctx.restore()
    }

    const drawPipes = (scale: number) => {
      const pipeWidth = 20 * scale

      ctx.strokeStyle = "#ff4444"
      ctx.lineWidth = pipeWidth
      ctx.lineCap = "round"
      ctx.lineJoin = "round"

      ctx.beginPath()
      ctx.moveTo(220 * scale, 350 * scale)
      ctx.lineTo(460 * scale, 350 * scale)
      ctx.stroke()

      ctx.strokeStyle = "#4488ff"
      ctx.beginPath()
      ctx.moveTo(460 * scale, 450 * scale)
      ctx.lineTo(300 * scale, 450 * scale)
      ctx.lineTo(300 * scale, 580 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(300 * scale, 630 * scale)
      ctx.lineTo(300 * scale, 700 * scale)
      ctx.lineTo(220 * scale, 700 * scale)
      ctx.lineTo(220 * scale, 500 * scale)
      ctx.stroke()

      ctx.strokeStyle = "#3388ff"
      ctx.lineWidth = 15 * scale

      ctx.beginPath()
      ctx.moveTo(550 * scale, 180 * scale)
      ctx.lineTo(850 * scale, 180 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(950 * scale, 280 * scale)
      ctx.lineTo(1050 * scale, 280 * scale)
      ctx.lineTo(1050 * scale, 450 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(1050 * scale, 550 * scale)
      ctx.lineTo(1050 * scale, 680 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(1050 * scale, 730 * scale)
      ctx.lineTo(1050 * scale, 800 * scale)
      ctx.lineTo(1250 * scale, 800 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(1250 * scale, 700 * scale)
      ctx.lineTo(1250 * scale, 650 * scale)
      ctx.lineTo(950 * scale, 650 * scale)
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(900 * scale, 650 * scale)
      ctx.lineTo(650 * scale, 650 * scale)
      ctx.lineTo(650 * scale, 500 * scale)
      ctx.stroke()

      ctx.strokeStyle = "#3388ff"
      ctx.setLineDash([10 * scale, 5 * scale])
      ctx.beginPath()
      ctx.moveTo(800 * scale, 850 * scale)
      ctx.lineTo(800 * scale, 700 * scale)
      ctx.lineTo(900 * scale, 700 * scale)
      ctx.stroke()
      ctx.setLineDash([])
    }

    const drawLabels = (scale: number) => {
      ctx.fillStyle = "#cccccc"
      ctx.font = `bold ${13 * scale}px monospace`
      ctx.textAlign = "center"

      // Reactor vessel label - above component
      ctx.fillText("REACTOR VESSEL", 160 * scale, 140 * scale)

      // Reactor coolant pump label - left side
      ctx.textAlign = "left"
      ctx.fillText("REACTOR", 340 * scale, 590 * scale)
      ctx.fillText("COOLANT", 340 * scale, 610 * scale)
      ctx.fillText("PUMP", 340 * scale, 630 * scale)

      // Steam generator label - above component
      ctx.textAlign = "center"
      ctx.fillText("STEAM GENERATOR", 550 * scale, 140 * scale)

      // Main turbine label - above component
      ctx.fillText("MAIN TURBINE", 950 * scale, 140 * scale)

      // Condenser label - below component
      ctx.fillText("CONDENSER", 1050 * scale, 590 * scale)

      // Generator label - right side
      ctx.textAlign = "left"
      ctx.fillText("GENERATOR", 1150 * scale, 280 * scale)

      // Hotwell label - below condenser
      ctx.textAlign = "center"
      ctx.fillText("HOTWELL", 1050 * scale, 620 * scale)

      // Feed pump label - above pump
      ctx.fillText("FEED", 925 * scale, 620 * scale)
      ctx.fillText("PUMP", 925 * scale, 640 * scale)

      // Condensate pump label - right side
      ctx.textAlign = "left"
      ctx.fillText("CONDENSATE", 1090 * scale, 700 * scale)
      ctx.fillText("PUMP", 1090 * scale, 720 * scale)

      // Condensate storage tank label - inside tank (centered)
      ctx.textAlign = "center"
      ctx.fillStyle = "#ffffff"
      ctx.font = `bold ${14 * scale}px monospace`
      ctx.fillText("CONDENSATE", 1250 * scale, 730 * scale)
      ctx.fillText("STORAGE", 1250 * scale, 750 * scale)
      ctx.fillText("TANK", 1250 * scale, 770 * scale)

      // Circulating water label - right side
      ctx.fillStyle = "#cccccc"
      ctx.font = `bold ${13 * scale}px monospace`
      ctx.textAlign = "left"
      ctx.fillText("CIRCULATING", 1150 * scale, 500 * scale)
      ctx.fillText("WATER", 1150 * scale, 520 * scale)

      // Auxiliary feedwater label - below
      ctx.textAlign = "center"
      ctx.fillText("AUXILIARY FEEDWATER", 850 * scale, 880 * scale)

      // Loop labels with background
      ctx.font = `bold ${16 * scale}px monospace`
      ctx.fillStyle = "rgba(42, 42, 42, 0.8)"
      ctx.fillRect(150 * scale, 750 * scale, 200 * scale, 30 * scale)
      ctx.fillStyle = "#ffffff"
      ctx.fillText("PRIMARY LOOP", 250 * scale, 772 * scale)

      ctx.fillStyle = "rgba(42, 42, 42, 0.8)"
      ctx.fillRect(800 * scale, 100 * scale, 250 * scale, 30 * scale)
      ctx.fillStyle = "#ffffff"
      ctx.fillText("SECONDARY LOOP", 925 * scale, 122 * scale)

      ctx.restore()
    }

    const getParticlePosition = (particle: Particle, scale: number) => {
      const t = particle.progress
      let x = 0,
        y = 0

      if (particle.path === "primary-hot") {
        x = 220 * scale + t * (460 * scale - 220 * scale)
        y = 350 * scale
      } else if (particle.path === "primary-cold") {
        if (t < 0.25) {
          const localT = t / 0.25
          x = 460 * scale + localT * (300 * scale - 460 * scale)
          y = 450 * scale
        } else if (t < 0.45) {
          const localT = (t - 0.25) / 0.2
          x = 300 * scale
          y = 450 * scale + localT * (630 * scale - 450 * scale)
        } else if (t < 0.65) {
          const localT = (t - 0.45) / 0.2
          x = 300 * scale
          y = 630 * scale + localT * (700 * scale - 630 * scale)
        } else if (t < 0.8) {
          const localT = (t - 0.65) / 0.15
          x = 300 * scale + localT * (220 * scale - 300 * scale)
          y = 700 * scale
        } else {
          const localT = (t - 0.8) / 0.2
          x = 220 * scale
          y = 700 * scale + localT * (500 * scale - 700 * scale)
        }
      } else {
        if (t < 0.15) {
          const localT = t / 0.15
          x = 550 * scale + localT * (850 * scale - 550 * scale)
          y = 180 * scale
        } else if (t < 0.25) {
          const localT = (t - 0.15) / 0.1
          x = 950 * scale + localT * (1050 * scale - 950 * scale)
          y = 280 * scale
        } else if (t < 0.35) {
          const localT = (t - 0.25) / 0.1
          x = 1050 * scale
          y = 280 * scale + localT * (550 * scale - 280 * scale)
        } else if (t < 0.45) {
          const localT = (t - 0.35) / 0.1
          x = 1050 * scale
          y = 550 * scale + localT * (730 * scale - 550 * scale)
        } else if (t < 0.55) {
          const localT = (t - 0.45) / 0.1
          x = 1050 * scale
          y = 730 * scale + localT * (800 * scale - 730 * scale)
        } else if (t < 0.65) {
          const localT = (t - 0.55) / 0.1
          x = 1050 * scale + localT * (1250 * scale - 1050 * scale)
          y = 800 * scale
        } else if (t < 0.75) {
          const localT = (t - 0.65) / 0.1
          x = 1250 * scale
          y = 800 * scale + localT * (650 * scale - 800 * scale)
        } else if (t < 0.85) {
          const localT = (t - 0.75) / 0.1
          x = 1250 * scale + localT * (900 * scale - 1250 * scale)
          y = 650 * scale
        } else {
          const localT = (t - 0.85) / 0.15
          x = 900 * scale + localT * (650 * scale - 900 * scale)
          y = 650 * scale + localT * (500 * scale - 650 * scale)
        }
      }

      return { x, y }
    }

    // Animation loop
    const animate = () => {
      if (!ctx || !canvas) return

      const scale = Math.min(canvas.width / 1500, canvas.height / 1000)

      ctx.fillStyle = "#1a1a1a"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.save()
      const offsetX = (canvas.width - 1400 * scale) / 2
      const offsetY = (canvas.height - 900 * scale) / 2
      ctx.translate(Math.max(50, offsetX), Math.max(50, offsetY))

      drawPipes(scale)
      drawReactorVessel(160 * scale, 350 * scale, scale)
      drawReactorCoolantPump(300 * scale, 605 * scale, scale)
      drawSteamGenerator(550 * scale, 350 * scale, scale)
      drawTurbine(950 * scale, 280 * scale, scale)
      drawCondenser(1050 * scale, 500 * scale, scale)
      drawGenerator(1050 * scale, 280 * scale, scale)
      drawCondensateStorageTank(1250 * scale, 750 * scale, scale)
      drawPump(925 * scale, 650 * scale, scale)
      drawPump(1050 * scale, 705 * scale, scale)

      drawLabels(scale)

      const flowRate = (parameters.flow?.primaryCoolant || 100) / 100
      particlesRef.current.forEach((particle) => {
        particle.progress += 0.003 * flowRate
        if (particle.progress > 1) particle.progress = 0

        const pos = getParticlePosition(particle, scale)

        ctx.fillStyle =
          particle.path === "primary-hot"
            ? "rgba(255, 100, 100, 0.8)"
            : particle.path === "primary-cold"
              ? "rgba(100, 150, 255, 0.8)"
              : "rgba(80, 180, 255, 0.8)"

        ctx.beginPath()
        ctx.arc(pos.x, pos.y, 4 * scale, 0, Math.PI * 2)
        ctx.fill()
      })

      ctx.restore()

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [mounted, parameters])

  if (!mounted) {
    return (
      <main className="flex-1 flex items-center justify-center bg-[#1a1a1a]">
        <div className="text-muted-foreground font-mono text-sm">Initializing reactor visualization...</div>
      </main>
    )
  }

  return (
    <main className="flex-1 relative bg-[#1a1a1a]">
      <canvas ref={canvasRef} className="w-full h-full" />

      {/* Status Panel */}
      <div className="absolute top-4 left-4 bg-[#2a2a2a]/90 backdrop-blur-sm border border-[#3a3a3a] rounded p-4 space-y-2">
        <div className="text-xs font-mono text-[#888888]">REACTOR STATUS</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#3388ff] animate-pulse" />
            <span className="text-sm font-mono text-[#cccccc]">Power: {parameters.other?.power?.toFixed(1) || 0}%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#ff4444]" />
            <span className="text-sm font-mono text-[#cccccc]">
              Core: {parameters.temperature?.core?.toFixed(1) || 0}°C
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#4444ff]" />
            <span className="text-sm font-mono text-[#cccccc]">
              Flow: {parameters.flow?.primaryCoolant?.toFixed(0) || 0} kg/s
            </span>
          </div>
        </div>
      </div>
    </main>
  )
}
