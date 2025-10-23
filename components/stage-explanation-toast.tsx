"use client"

import React from "react"

interface StageExplanationToastProps {
  currentStage: number
  isVisible: boolean
}

/**
 * Toast component that displays explanations for each stage of the PWR system
 * Positioned at the bottom-right of the screen
 */
export default function StageExplanationToast({ currentStage, isVisible }: StageExplanationToastProps) {
  // PWR System Stage Explanations
  const stageExplanations = {
    0: {
      title: "System Initialization",
      description: "Preparing nuclear reactor systems for operation...",
      phase: "Startup"
    },
    1: {
      title: "1. Reactor Vessel - Nuclear Fission",
      description: "Nuclear fission occurs in the fuel rods, producing intense heat that warms the high-pressure water coolant.",
      phase: "Primary Loop"
    },
    2: {
      title: "2. Reactor Coolant Pump",
      description: "This pump forces the hot primary coolant to circulate from the reactor vessel to the steam generator.",
      phase: "Primary Loop"
    },
    3: {
      title: "3. Steam Generator - Heat Transfer",
      description: "The hot primary coolant transfers its heat through metal tubes to the cooler, lower-pressure water of the secondary loop, causing the secondary water to boil into steam.",
      phase: "Heat Transfer Bridge"
    },
    4: {
      title: "4. Return to Reactor Vessel",
      description: "The now-cooler primary water flows back into the reactor core to be reheated, completing its safety-isolated cycle.",
      phase: "Primary Loop"
    },
    5: {
      title: "5. Steam Generator - High-Pressure Steam",
      description: "High-pressure steam is produced from the boiling secondary water and routed to the turbine.",
      phase: "Secondary Loop"
    },
    6: {
      title: "6. Main Turbine - Mechanical Energy",
      description: "The high-pressure steam expands against the turbine blades, causing them to rotate rapidly, converting thermal energy into mechanical energy.",
      phase: "Secondary Loop"
    },
    7: {
      title: "7. Generator - Electrical Energy",
      description: "Connected to the turbine shaft, it converts the mechanical rotation into electrical energy that is sent to the power grid.",
      phase: "Secondary Loop"
    },
    8: {
      title: "8. Condenser - Steam Condensation",
      description: "The spent steam is cooled by circulating water, causing it to condense back into liquid water (condensate).",
      phase: "Secondary Loop"
    },
    9: {
      title: "9. Hotwell - Condensate Collection",
      description: "This acts as a reservoir to collect the condensed water.",
      phase: "Secondary Loop"
    },
    10: {
      title: "10. Condensate & Feed Pumps",
      description: "These pumps re-pressurize the water and push it back from the condenser/hotwell into the steam generator.",
      phase: "Secondary Loop"
    },
    11: {
      title: "11. Return to Steam Generator",
      description: "The high-pressure water re-enters the steam generator to be boiled again, completing the power generation cycle.",
      phase: "Secondary Loop"
    }
  }

  const currentExplanation = stageExplanations[currentStage as keyof typeof stageExplanations]

  if (!isVisible || !currentExplanation) {
    return null
  }

  // Get phase color
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case "Startup":
        return "bg-gray-600"
      case "Primary Loop":
        return "bg-red-600"
      case "Heat Transfer Bridge":
        return "bg-orange-600"
      case "Secondary Loop":
        return "bg-blue-600"
      default:
        return "bg-gray-600"
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm animate-in slide-in-from-bottom-2 duration-300">
      <div className="bg-black/90 backdrop-blur-sm border border-gray-700 rounded-lg p-4 shadow-2xl">
        {/* Phase Badge */}
        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white mb-2 ${getPhaseColor(currentExplanation.phase)}`}>
          {currentExplanation.phase}
        </div>
        
        {/* Stage Title */}
        <h3 className="text-white font-semibold text-sm mb-2 leading-tight">
          {currentExplanation.title}
        </h3>
        
        {/* Stage Description */}
        <p className="text-gray-300 text-xs leading-relaxed">
          {currentExplanation.description}
        </p>
        
        {/* Progress Indicator */}
        <div className="mt-3 flex items-center justify-between">
          <div className="flex space-x-1">
            {Array.from({ length: 12 }, (_, i) => (
              <div
                key={i}
                className={`w-1.5 h-1.5 rounded-full ${
                  i <= currentStage ? "bg-blue-400" : "bg-gray-600"
                }`}
              />
            ))}
          </div>
          <span className="text-gray-400 text-xs ml-2">
            {currentStage}/11
          </span>
        </div>
      </div>
    </div>
  )
}