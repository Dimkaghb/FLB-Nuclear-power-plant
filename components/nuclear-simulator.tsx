"use client"

import { useState, useEffect } from "react"
import ReactorVisualization from "./reactor-visualization"
import ControlSidebar from "./control-sidebar"

export default function NuclearSimulator() {
  const [mounted, setMounted] = useState(false)
  const [isSimulationRunning, setIsSimulationRunning] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [simulationStartTime, setSimulationStartTime] = useState<number | null>(null)

  useEffect(() => {
    console.log("[v0] NuclearSimulator mounted")
    setMounted(true)
  }, [])

  const [parameters, setParameters] = useState({
    temperature: {
      coldLeg: 290,
      hotLeg: 325,
      core: 350,
      steamGenerator: 280,
      pressurizer: 345,
      containment: 25,
      coolant: 295,
      fuel: 1200,
      moderator: 310,
      reflector: 300,
    },
    pressure: {
      primary: 155,
      secondary: 70,
      containment: 1.0,
      pressurizer: 155,
      steamLine: 65,
      feedwater: 75,
      reactor: 155,
      condenser: 0.05,
      turbine: 60,
      pump: 160,
    },
    flow: {
      primaryCoolant: 100,
      secondaryCoolant: 85,
      feedwater: 80,
      steam: 75,
      condensate: 78,
      makeup: 5,
      letdown: 3,
      charging: 4,
      blowdown: 2,
      emergency: 0,
    },
    reactivity: {
      controlRods: 50,
      boron: 1200,
      xenon: 0.5,
      temperature: -0.2,
      void: 0,
      doppler: -0.3,
      moderator: -0.1,
      fuel: 0.8,
      reflector: 0.2,
      total: 0.0,
    },
    radiation: {
      core: 1000,
      containment: 0.1,
      primary: 50,
      secondary: 0.05,
      stack: 0.01,
      waste: 100,
      fuel: 2000,
      coolant: 45,
      steam: 0.02,
      environment: 0.001,
    },
    other: {
      power: 100,
      efficiency: 33,
      turbineSpeed: 1800,
      generatorOutput: 1000,
      gridFrequency: 60,
      vibration: 0.5,
      neutronFlux: 3.5,
      burnup: 15000,
      uptime: 98.5,
      capacity: 100,
    },
  })

  const updateParameter = (category: string, param: string, value: number) => {
    console.log("[v0] Updating parameter:", category, param, value)
    setParameters((prev) => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [param]: value,
      },
    }))
  }

  /**
   * Toggles the simulation state between running and stopped
   * Includes 2-second loading delay when starting simulation
   */
  const toggleSimulation = () => {
    if (isSimulationRunning) {
      // Stop simulation immediately
      console.log("[v0] Stopping simulation")
      setIsSimulationRunning(false)
      setIsLoading(false)
      setSimulationStartTime(null)
    } else {
      // Start simulation with loading delay
      console.log("[v0] Starting simulation with loading delay")
      setIsLoading(true)
      
      setTimeout(() => {
        setIsSimulationRunning(true)
        setIsLoading(false)
        setSimulationStartTime(Date.now())
        console.log("[v0] Simulation started after loading")
      }, 2000) // 2-second delay
    }
  }

  if (!mounted) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-foreground font-mono">Loading reactor systems...</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <ControlSidebar 
        parameters={parameters} 
        updateParameter={updateParameter}
        isSimulationRunning={isSimulationRunning}
        isLoading={isLoading}
        toggleSimulation={toggleSimulation}
      />
      <ReactorVisualization 
        parameters={parameters} 
        isSimulationRunning={isSimulationRunning}
        simulationStartTime={simulationStartTime}
      />
    </div>
  )
}
