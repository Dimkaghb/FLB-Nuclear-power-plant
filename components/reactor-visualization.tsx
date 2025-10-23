"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"

interface ReactorVisualizationProps {
  parameters: Record<string, Record<string, number>>
}

interface Particle {
  progress: number
  path: "primary-hot" | "primary-cold" | "secondary-steam" | "secondary-condensate" | "secondary-feedwater"
}

export default function ReactorVisualization({ parameters }: ReactorVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [mounted, setMounted] = useState(false)
  const [canvasTransform, setCanvasTransform] = useState({ scale: 1, offsetX: 0, offsetY: 0 })
  const particlesRef = useRef<Particle[]>([])
  const animationFrameRef = useRef<number | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const toScreenCoords = (x: number, y: number) => {
    return {
      x: x * canvasTransform.scale + canvasTransform.offsetX,
      y: y * canvasTransform.scale + canvasTransform.offsetY,
    }
  }

  useEffect(() => {
    if (!mounted || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const resizeCanvas = () => {
      const container = canvas.parentElement
      if (container) {
        canvas.width = container.clientWidth
        canvas.height = container.clientHeight
      }
    }
    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    if (particlesRef.current.length === 0) {
      // Primary hot leg particles
      for (let i = 0; i < 30; i++) {
        particlesRef.current.push({
          progress: i / 30,
          path: "primary-hot",
        })
      }
      // Primary cold leg particles
      for (let i = 0; i < 30; i++) {
        particlesRef.current.push({
          progress: i / 30,
          path: "primary-cold",
        })
      }
      // Secondary steam line particles
      for (let i = 0; i < 25; i++) {
        particlesRef.current.push({
          progress: i / 25,
          path: "secondary-steam",
        })
      }
      // Secondary condensate return particles
      for (let i = 0; i < 20; i++) {
        particlesRef.current.push({
          progress: i / 20,
          path: "secondary-condensate",
        })
      }
      // Secondary feedwater line particles
      for (let i = 0; i < 25; i++) {
        particlesRef.current.push({
          progress: i / 25,
          path: "secondary-feedwater",
        })
      }
    }

    const roundRect = (x: number, y: number, w: number, h: number, r: number) => {
      ctx.beginPath()
      ctx.moveTo(x + r, y)
      ctx.lineTo(x + w - r, y)
      ctx.arcTo(x + w, y, x + w, y + r, r)
      ctx.lineTo(x + w, y + h - r)
      ctx.arcTo(x + w, y + h, x + w - r, y + h, r)
      ctx.lineTo(x + r, y + h)
      ctx.arcTo(x, y + h, x, y + h - r, r)
      ctx.lineTo(x, y + r)
      ctx.arcTo(x, y, x + r, y, r)
      ctx.closePath()
    }

    const drawReactorVessel = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Main vessel body
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      // Vessel outline
      ctx.beginPath()
      ctx.moveTo(-50, -120)
      ctx.lineTo(-50, 80)
      ctx.arc(0, 80, 50, Math.PI, 0, false)
      ctx.lineTo(50, -120)
      ctx.arc(0, -120, 50, 0, Math.PI, false)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      // Fuel rods (vertical lines)
      ctx.strokeStyle = "#666666"
      ctx.lineWidth = 1
      for (let i = -40; i <= 40; i += 5) {
        ctx.beginPath()
        ctx.moveTo(i, -100)
        ctx.lineTo(i, 60)
        ctx.stroke()
      }

      // Top dome
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(0, -120, 50, 0, Math.PI, false)
      ctx.stroke()

      // Bottom dome
      ctx.beginPath()
      ctx.arc(0, 80, 50, Math.PI, 0, false)
      ctx.stroke()

      // Connection nozzle (right side)
      ctx.fillStyle = "#3a3a3a"
      ctx.fillRect(50, -10, 25, 20)
      ctx.strokeRect(50, -10, 25, 20)

      ctx.restore()
    }

    const drawReactorCoolantPump = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Pump casing
      ctx.fillStyle = "#3a3a3a"
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2

      ctx.beginPath()
      ctx.arc(0, 0, 30, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      // Impeller blades
      ctx.strokeStyle = "#666666"
      ctx.lineWidth = 2
      for (let i = 0; i < 6; i++) {
        const angle = (i / 6) * Math.PI * 2
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(Math.cos(angle) * 20, Math.sin(angle) * 20)
        ctx.stroke()
      }

      // Motor housing
      ctx.fillStyle = "#2a2a2a"
      ctx.fillRect(-15, -50, 30, 40)
      ctx.strokeRect(-15, -50, 30, 40)

      ctx.restore()
    }

    const drawSteamGenerator = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Main vessel outline
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.beginPath()
      ctx.moveTo(-60, -150)
      ctx.lineTo(-60, 100)
      ctx.arc(0, 100, 60, Math.PI, 0, false)
      ctx.lineTo(60, -150)
      ctx.arc(0, -150, 60, 0, Math.PI, false)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      // Heat exchanger tubes (cross-hatch pattern)
      ctx.strokeStyle = "#555555"
      ctx.lineWidth = 1
      for (let i = -50; i <= 50; i += 6) {
        for (let j = -130; j <= 80; j += 6) {
          ctx.beginPath()
          ctx.moveTo(i, j)
          ctx.lineTo(i + 3, j + 3)
          ctx.stroke()
        }
      }

      // Hot section (bottom) - orange/red gradient
      const hotGradient = ctx.createLinearGradient(0, 60, 0, 100)
      hotGradient.addColorStop(0, "rgba(255, 100, 0, 0.7)")
      hotGradient.addColorStop(1, "rgba(255, 150, 50, 0.5)")
      ctx.fillStyle = hotGradient
      ctx.fillRect(-55, 60, 110, 40)

      // Transition section - gradient from hot to cold
      const transitionGradient = ctx.createLinearGradient(0, 0, 0, 60)
      transitionGradient.addColorStop(0, "rgba(100, 150, 255, 0.3)")
      transitionGradient.addColorStop(0.5, "rgba(150, 100, 200, 0.3)")
      transitionGradient.addColorStop(1, "rgba(255, 100, 100, 0.5)")
      ctx.fillStyle = transitionGradient
      ctx.fillRect(-55, 0, 110, 60)

      // Cold section (top) - blue
      ctx.fillStyle = "rgba(100, 150, 255, 0.3)"
      ctx.fillRect(-55, -130, 110, 130)

      // Steam outlet pipe (top)
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#3a3a3a"
      ctx.fillRect(-12, -180, 24, 30)
      ctx.strokeRect(-12, -180, 24, 30)

      // Hot leg inlet (left side, lower)
      ctx.fillRect(-80, 65, 20, 20)
      ctx.strokeRect(-80, 65, 20, 20)

      // Cold leg outlet (left side, upper)
      ctx.fillRect(-80, -15, 20, 20)
      ctx.strokeRect(-80, -15, 20, 20)

      ctx.restore()
    }

    const drawTurbine = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Turbine casing
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      ctx.fillRect(-70, -45, 140, 90)
      ctx.strokeRect(-70, -45, 140, 90)

      // Turbine blades pattern
      ctx.strokeStyle = "#666666"
      ctx.lineWidth = 1.5
      for (let i = -50; i <= 50; i += 12) {
        ctx.beginPath()
        ctx.moveTo(i, -35)
        ctx.lineTo(i + 6, 0)
        ctx.lineTo(i, 35)
        ctx.stroke()
      }

      // Central shaft
      ctx.fillStyle = "#555555"
      ctx.fillRect(-75, -8, 150, 16)
      ctx.strokeRect(-75, -8, 150, 16)

      ctx.restore()
    }

    const drawCondenser = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Condenser body
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2a2a2a"

      roundRect(-90, -70, 180, 140, 8)
      ctx.fill()
      ctx.stroke()

      // Water collection at bottom with wavy surface
      const waterGradient = ctx.createLinearGradient(0, 35, 0, 70)
      waterGradient.addColorStop(0, "rgba(100, 150, 255, 0.6)")
      waterGradient.addColorStop(1, "rgba(80, 130, 255, 0.8)")
      ctx.fillStyle = waterGradient

      ctx.beginPath()
      ctx.moveTo(-90, 35)
      for (let i = -90; i <= 90; i += 8) {
        ctx.lineTo(i, 35 + Math.sin(i * 0.1) * 2)
      }
      ctx.lineTo(90, 70)
      ctx.lineTo(-90, 70)
      ctx.closePath()
      ctx.fill()

      ctx.restore()
    }

    const drawGenerator = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Generator box
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#d32f2f"
      ctx.fillRect(-45, -45, 90, 90)
      ctx.strokeRect(-45, -45, 90, 90)

      // Lightning bolt icon
      ctx.fillStyle = "#ffeb3b"
      ctx.strokeStyle = "#ffeb3b"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(-8, -25)
      ctx.lineTo(8, -3)
      ctx.lineTo(-3, -3)
      ctx.lineTo(12, 25)
      ctx.lineTo(-8, 3)
      ctx.lineTo(3, 3)
      ctx.closePath()
      ctx.fill()
      ctx.stroke()

      ctx.restore()
    }

    const drawCondensateStorageTank = (x: number, y: number) => {
      ctx.save()
      ctx.translate(x, y)

      // Tank body
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#0277bd"
      ctx.fillRect(-70, -90, 140, 180)
      ctx.strokeRect(-70, -90, 140, 180)

      // Water level inside
      const waterGradient = ctx.createLinearGradient(0, -50, 0, 90)
      waterGradient.addColorStop(0, "rgba(100, 180, 255, 0.5)")
      waterGradient.addColorStop(1, "rgba(80, 150, 255, 0.7)")
      ctx.fillStyle = waterGradient
      ctx.fillRect(-65, -50, 130, 135)

      ctx.restore()
    }

    const drawPump = (x: number, y: number, label: string) => {
      ctx.save()
      ctx.translate(x, y)

      // Pump casing
      ctx.strokeStyle = "#888888"
      ctx.lineWidth = 2
      ctx.fillStyle = "#2196f3"
      ctx.beginPath()
      ctx.arc(0, 0, 22, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      // Impeller
      ctx.strokeStyle = "#ffffff"
      ctx.lineWidth = 2
      for (let i = 0; i < 4; i++) {
        const angle = (i / 4) * Math.PI * 2
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(Math.cos(angle) * 14, Math.sin(angle) * 14)
        ctx.stroke()
      }

      ctx.restore()
    }

    const drawPipes = () => {
      // PRIMARY LOOP - Hot Leg (red)
      ctx.strokeStyle = "#ff4444"
      ctx.lineWidth = 16
      ctx.lineCap = "round"
      ctx.lineJoin = "round"

      ctx.beginPath()
      ctx.moveTo(200, 320) // Reactor outlet
      ctx.bezierCurveTo(250, 320, 350, 280, 400, 250) // Curve up
      ctx.bezierCurveTo(420, 240, 440, 240, 460, 245) // Curve to SG
      ctx.lineTo(490, 255) // SG inlet
      ctx.stroke()

      // PRIMARY LOOP - Cold Leg (orange/yellow)
      ctx.strokeStyle = "#ff9933"
      ctx.lineWidth = 16

      ctx.beginPath()
      ctx.moveTo(490, 345) // SG outlet
      ctx.lineTo(350, 345) // Horizontal
      ctx.bezierCurveTo(320, 345, 300, 365, 300, 395) // Curve down
      ctx.lineTo(300, 520) // Vertical down to pump
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(300, 560) // Pump outlet
      ctx.lineTo(300, 620) // Down
      ctx.bezierCurveTo(300, 640, 280, 660, 260, 660) // Curve left
      ctx.lineTo(200, 660) // Horizontal
      ctx.lineTo(200, 480) // Up to reactor inlet
      ctx.stroke()

      // SECONDARY LOOP - Steam Line (light gray/white)
      ctx.strokeStyle = "#e8e8e8"
      ctx.lineWidth = 12

      ctx.beginPath()
      ctx.moveTo(550, 170) // SG steam outlet
      ctx.bezierCurveTo(600, 150, 700, 150, 750, 170) // Curve up and right
      ctx.bezierCurveTo(780, 180, 800, 200, 820, 230) // Curve down to turbine
      ctx.lineTo(850, 280) // Turbine inlet
      ctx.stroke()

      // SECONDARY LOOP - Condensate Return (blue)
      ctx.strokeStyle = "#4080ff"
      ctx.lineWidth = 12

      ctx.beginPath()
      ctx.moveTo(950, 325) // Turbine outlet
      ctx.lineTo(950, 380) // Down to condenser
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(950, 450) // Condenser outlet
      ctx.lineTo(950, 490) // Down to hotwell
      ctx.stroke()

      // SECONDARY LOOP - Feedwater Line (dark blue)
      ctx.strokeStyle = "#0066cc"
      ctx.lineWidth = 12

      ctx.beginPath()
      ctx.moveTo(972, 510) // Condensate pump outlet
      ctx.lineTo(1050, 510) // Right
      ctx.lineTo(1050, 600) // Down to storage
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(1050, 690) // Storage outlet
      ctx.lineTo(1050, 750) // Down
      ctx.bezierCurveTo(1050, 770, 1030, 780, 1000, 780) // Curve left
      ctx.lineTo(850, 780) // Left
      ctx.bezierCurveTo(820, 780, 800, 760, 800, 730) // Curve up
      ctx.lineTo(800, 580) // Up to feed pump
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(778, 570) // Feed pump outlet
      ctx.bezierCurveTo(750, 570, 720, 550, 700, 520) // Curve up and left
      ctx.bezierCurveTo(680, 490, 650, 460, 620, 440) // Continue curve
      ctx.bezierCurveTo(590, 420, 560, 400, 530, 390) // To SG
      ctx.lineTo(490, 380) // SG feedwater inlet
      ctx.stroke()

      // CIRCULATING WATER (cyan)
      ctx.strokeStyle = "#00bcd4"
      ctx.lineWidth = 10

      ctx.beginPath()
      ctx.moveTo(1150, 410) // Cooling inlet
      ctx.lineTo(1040, 410) // To condenser
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(1040, 430) // Condenser cooling outlet
      ctx.lineTo(1150, 430) // Cooling outlet
      ctx.stroke()

      // AUXILIARY FEEDWATER (dashed blue)
      ctx.strokeStyle = "#0066cc"
      ctx.lineWidth = 8
      ctx.setLineDash([10, 5])

      ctx.beginPath()
      ctx.moveTo(1050, 800) // Storage aux outlet
      ctx.lineTo(900, 800) // Left
      ctx.bezierCurveTo(870, 800, 850, 780, 850, 750) // Curve up
      ctx.lineTo(850, 650) // Up
      ctx.stroke()

      ctx.setLineDash([])
    }

    const drawLabels = () => {
      // Helper function to draw label with background
      const drawLabelWithBackground = (
        text: string | string[],
        x: number,
        y: number,
        align: CanvasTextAlign = "center",
        fontSize = 14,
        bgColor = "rgba(42, 42, 42, 0.95)",
        textColor = "#ffffff",
      ) => {
        const lines = Array.isArray(text) ? text : [text]
        ctx.font = `bold ${fontSize}px Arial, sans-serif`
        ctx.textAlign = align

        // Measure text for background box
        const maxWidth = Math.max(...lines.map((line) => ctx.measureText(line).width))
        const lineHeight = fontSize * 1.4
        const totalHeight = lines.length * lineHeight
        const padding = 8

        // Draw background box
        ctx.fillStyle = bgColor
        ctx.strokeStyle = "#555555"
        ctx.lineWidth = 1

        let boxX = x - maxWidth / 2 - padding
        if (align === "left") boxX = x - padding
        if (align === "right") boxX = x - maxWidth - padding

        roundRect(boxX, y - lineHeight + 2 - padding, maxWidth + padding * 2, totalHeight + padding * 2, 4)
        ctx.fill()
        ctx.stroke()

        // Draw text
        ctx.fillStyle = textColor
        lines.forEach((line, i) => {
          ctx.fillText(line, x, y + i * lineHeight)
        })
      }

      // Reactor vessel label - top left
      drawLabelWithBackground(["REACTOR", "VESSEL"], 160, 140, "center", 13)

      // Reactor coolant pump label - bottom
      drawLabelWithBackground(["REACTOR", "COOLANT", "PUMP"], 300, 690, "center", 12)

      // Steam generator label - top center
      drawLabelWithBackground(["STEAM", "GENERATOR"], 550, 140, "center", 14)

      // Main turbine label - top
      drawLabelWithBackground(["MAIN", "TURBINE"], 920, 210, "center", 13)

      // Condenser label - bottom
      drawLabelWithBackground("CONDENSER", 950, 540, "center", 13)

      // Generator label - right side
      drawLabelWithBackground("GENERATOR", 1120, 285, "left", 13)

      // Hotwell label - inside condenser area
      drawLabelWithBackground("HOTWELL", 950, 505, "center", 11, "rgba(42, 42, 42, 0.85)", "#aaaaaa")

      // Feed pump label - left of pump
      drawLabelWithBackground(["FEED", "PUMP"], 730, 570, "right", 11)

      // Condensate pump label - below pump
      drawLabelWithBackground(["CONDENSATE", "PUMP"], 950, 560, "center", 11)

      // Condensate storage tank label - inside tank with larger font
      ctx.font = "bold 16px Arial, sans-serif"
      ctx.textAlign = "center"
      ctx.fillStyle = "#ffffff"
      ctx.strokeStyle = "#0277bd"
      ctx.lineWidth = 2
      ctx.strokeText("CONDENSATE", 1050, 625)
      ctx.fillText("CONDENSATE", 1050, 625)
      ctx.strokeText("STORAGE", 1050, 647)
      ctx.fillText("STORAGE", 1050, 647)
      ctx.strokeText("TANK", 1050, 669)
      ctx.fillText("TANK", 1050, 669)

      // Circulating water label - right side
      drawLabelWithBackground(["CIRCULATING", "WATER"], 1200, 420, "left", 11)

      // Auxiliary feedwater label - bottom
      drawLabelWithBackground(["AUXILIARY", "FEEDWATER"], 900, 840, "center", 11)

      // Loop labels with prominent background boxes
      // Primary loop label - bottom left
      drawLabelWithBackground("PRIMARY LOOP", 200, 760, "center", 16, "rgba(255, 100, 50, 0.2)", "#ffaa66")

      // Secondary loop label - top right
      drawLabelWithBackground("SECONDARY LOOP", 870, 125, "center", 16, "rgba(100, 150, 255, 0.2)", "#88ccff")
    }

    const getParticlePosition = (particle: Particle): { x: number; y: number } => {
      const t = particle.progress
      let x = 0,
        y = 0

      if (particle.path === "primary-hot") {
        // Hot leg path from reactor to steam generator
        if (t < 0.3) {
          const localT = t / 0.3
          x = 200 + localT * 50
          y = 320
        } else if (t < 0.7) {
          const localT = (t - 0.3) / 0.4
          const curveT = localT
          x = 250 + curveT * 150
          y = 320 - Math.sin(curveT * Math.PI) * 70
        } else {
          const localT = (t - 0.7) / 0.3
          x = 400 + localT * 90
          y = 250 + localT * 5
        }
      } else if (particle.path === "primary-cold") {
        // Cold leg path from steam generator back to reactor
        if (t < 0.15) {
          const localT = t / 0.15
          x = 490 - localT * 140
          y = 345
        } else if (t < 0.25) {
          const localT = (t - 0.15) / 0.1
          x = 350 - localT * 50
          y = 345 + localT * 50
        } else if (t < 0.5) {
          const localT = (t - 0.25) / 0.25
          x = 300
          y = 395 + localT * 125
        } else if (t < 0.6) {
          const localT = (t - 0.5) / 0.1
          x = 300
          y = 520 + localT * 40
        } else if (t < 0.7) {
          const localT = (t - 0.6) / 0.1
          x = 300
          y = 560 + localT * 60
        } else if (t < 0.8) {
          const localT = (t - 0.7) / 0.1
          x = 300 - localT * 40
          y = 620 + localT * 40
        } else {
          const localT = (t - 0.8) / 0.2
          x = 260 - localT * 60
          y = 660 - localT * 180
        }
      } else if (particle.path === "secondary-steam") {
        // Steam line from SG to turbine
        if (t < 0.3) {
          const localT = t / 0.3
          x = 550 + localT * 50
          y = 170 - localT * 20
        } else if (t < 0.7) {
          const localT = (t - 0.3) / 0.4
          x = 600 + localT * 150
          y = 150 + Math.sin(localT * Math.PI) * 20
        } else {
          const localT = (t - 0.7) / 0.3
          x = 750 + localT * 100
          y = 170 + localT * 110
        }
      } else if (particle.path === "secondary-condensate") {
        // Condensate from turbine to hotwell
        if (t < 0.5) {
          const localT = t / 0.5
          x = 950
          y = 325 + localT * 55
        } else {
          const localT = (t - 0.5) / 0.5
          x = 950
          y = 450 + localT * 40
        }
      } else if (particle.path === "secondary-feedwater") {
        // Feedwater from condensate pump through storage to feed pump to SG
        if (t < 0.1) {
          const localT = t / 0.1
          x = 972 + localT * 78
          y = 510
        } else if (t < 0.2) {
          const localT = (t - 0.1) / 0.1
          x = 1050
          y = 510 + localT * 90
        } else if (t < 0.3) {
          const localT = (t - 0.2) / 0.1
          x = 1050
          y = 690 + localT * 60
        } else if (t < 0.4) {
          const localT = (t - 0.3) / 0.1
          x = 1050 - localT * 50
          y = 750 + localT * 30
        } else if (t < 0.5) {
          const localT = (t - 0.4) / 0.1
          x = 1000 - localT * 150
          y = 780
        } else if (t < 0.6) {
          const localT = (t - 0.5) / 0.1
          x = 850 - localT * 50
          y = 780 - localT * 50
        } else if (t < 0.75) {
          const localT = (t - 0.6) / 0.15
          x = 800
          y = 730 - localT * 150
        } else if (t < 0.85) {
          const localT = (t - 0.75) / 0.1
          x = 800 - localT * 22
          y = 580 - localT * 10
        } else {
          const localT = (t - 0.85) / 0.15
          x = 778 - localT * 288
          y = 570 - localT * 180
        }
      }

      return { x, y }
    }

    const animate = () => {
      if (!ctx || !canvas) return

      // Clear canvas
      ctx.fillStyle = "#1a1a1a"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Calculate scale to fit content
      const contentWidth = 1300
      const contentHeight = 900
      const scaleX = canvas.width / contentWidth
      const scaleY = canvas.height / contentHeight
      const scale = Math.min(scaleX, scaleY) * 0.9

      // Center content
      const offsetX = (canvas.width - contentWidth * scale) / 2
      const offsetY = (canvas.height - contentHeight * scale) / 2

      setCanvasTransform({ scale, offsetX, offsetY })

      ctx.save()
      ctx.translate(offsetX, offsetY)
      ctx.scale(scale, scale)

      // Draw all pipes first (background)
      drawPipes()

      // Draw all components
      drawReactorVessel(160, 400)
      drawReactorCoolantPump(300, 540)
      drawSteamGenerator(550, 350)
      drawTurbine(920, 280)
      drawCondenser(950, 410)
      drawGenerator(1050, 285)
      drawCondensateStorageTank(1050, 645)
      drawPump(800, 570, "FEED PUMP")
      drawPump(950, 510, "CONDENSATE PUMP")

      // Draw particles
      const flowRate = (parameters.flow?.primaryCoolant || 100) / 100
      particlesRef.current.forEach((particle) => {
        particle.progress += 0.004 * flowRate
        if (particle.progress > 1) particle.progress = 0

        const pos = getParticlePosition(particle)

        // Set particle color based on path
        if (particle.path === "primary-hot") {
          ctx.fillStyle = "rgba(255, 100, 100, 0.9)"
          ctx.shadowColor = "#ff6600"
          ctx.shadowBlur = 8
        } else if (particle.path === "primary-cold") {
          ctx.fillStyle = "rgba(255, 150, 100, 0.9)"
          ctx.shadowColor = "#ff9933"
          ctx.shadowBlur = 8
        } else if (particle.path === "secondary-steam") {
          ctx.fillStyle = "rgba(255, 255, 255, 0.8)"
          ctx.shadowColor = "#ffffff"
          ctx.shadowBlur = 10
        } else if (particle.path === "secondary-condensate") {
          ctx.fillStyle = "rgba(100, 150, 255, 0.9)"
          ctx.shadowColor = "#4080ff"
          ctx.shadowBlur = 8
        } else {
          ctx.fillStyle = "rgba(80, 130, 255, 0.9)"
          ctx.shadowColor = "#0066cc"
          ctx.shadowBlur = 8
        }

        ctx.beginPath()
        ctx.arc(pos.x, pos.y, 4, 0, Math.PI * 2)
        ctx.fill()

        ctx.shadowBlur = 0
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

  const Label = ({
    x,
    y,
    children,
    className = "",
  }: {
    x: number
    y: number
    children: React.ReactNode
    className?: string
  }) => {
    const screenPos = toScreenCoords(x, y)
    return (
      <div
        className={`absolute font-mono text-xs text-sidebar-foreground bg-sidebar-accent/90 backdrop-blur-sm border border-sidebar-border rounded px-2 py-1 pointer-events-none ${className}`}
        style={{
          left: `${screenPos.x}px`,
          top: `${screenPos.y}px`,
          transform: "translate(-50%, -50%)",
        }}
      >
        {children}
      </div>
    )
  }

  return (
    <main ref={containerRef} className="flex-1 relative bg-[#1a1a1a]">
      <canvas ref={canvasRef} className="w-full h-full" />

      <Label x={160} y={250} className="text-center">
        <div>REACTOR</div>
        <div>VESSEL</div>
      </Label>

      <Label x={300} y={620} className="text-center">
        <div>REACTOR</div>
        <div>COOLANT</div>
        <div>PUMP</div>
      </Label>

      <Label x={550} y={150} className="text-center font-semibold">
        <div>STEAM</div>
        <div>GENERATOR</div>
      </Label>

      <Label x={920} y={200} className="text-center">
        <div>MAIN</div>
        <div>TURBINE</div>
      </Label>

      <Label x={950} y={500} className="text-center">
        CONDENSER
      </Label>

      <Label x={1150} y={285} className="text-center">
        GENERATOR
      </Label>

      <Label x={950} y={475} className="text-center text-[10px] text-sidebar-muted-foreground">
        HOTWELL
      </Label>

      <Label x={730} y={570} className="text-center text-[10px]">
        <div>FEED</div>
        <div>PUMP</div>
      </Label>

      <Label x={950} y={545} className="text-center text-[10px]">
        <div>CONDENSATE</div>
        <div>PUMP</div>
      </Label>

      <Label x={1050} y={645} className="text-center font-semibold bg-[#0277bd]/80 text-white border-[#0277bd]">
        <div>CONDENSATE</div>
        <div>STORAGE</div>
        <div>TANK</div>
      </Label>

      <Label x={1200} y={420} className="text-center text-[10px]">
        <div>CIRCULATING</div>
        <div>WATER</div>
      </Label>

      <Label x={900} y={820} className="text-center text-[10px]">
        <div>AUXILIARY</div>
        <div>FEEDWATER</div>
      </Label>

      <Label x={200} y={730} className="text-center font-semibold bg-[#ff6633]/20 text-[#ffaa66] border-[#ff6633]">
        PRIMARY LOOP
      </Label>

      <Label x={870} y={100} className="text-center font-semibold bg-[#4080ff]/20 text-[#88ccff] border-[#4080ff]">
        SECONDARY LOOP
      </Label>

      {/* Status Panel */}
      <div className="absolute top-4 left-4 bg-sidebar-accent/90 backdrop-blur-sm border border-sidebar-border rounded p-4 space-y-2">
        <div className="text-xs font-mono text-sidebar-muted-foreground">REACTOR STATUS</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#3388ff] animate-pulse" />
            <span className="text-sm font-mono text-sidebar-foreground">
              Power: {parameters.other?.power?.toFixed(1) || 0}%
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#ff4444]" />
            <span className="text-sm font-mono text-sidebar-foreground">
              Core: {parameters.temperature?.core?.toFixed(1) || 0}°C
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#4444ff]" />
            <span className="text-sm font-mono text-sidebar-foreground">
              Flow: {parameters.flow?.primaryCoolant?.toFixed(0) || 0} kg/s
            </span>
          </div>
        </div>
      </div>
    </main>
  )
}
