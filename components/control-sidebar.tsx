"use client"

import { ChevronDown } from "lucide-react"
import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ControlSidebarProps {
  parameters: Record<string, Record<string, number>>
  updateParameter: (category: string, param: string, value: number) => void
}

const categories = [
  { key: "temperature", label: "Температуры", unit: "°C" },
  { key: "pressure", label: "Давление", unit: "bar" },
  { key: "flow", label: "Потоки", unit: "%" },
  { key: "reactivity", label: "Реактивность", unit: "pcm" },
  { key: "radiation", label: "Радиация", unit: "mSv/h" },
  { key: "other", label: "Прочее", unit: "" },
]

export default function ControlSidebar({ parameters, updateParameter }: ControlSidebarProps) {
  useEffect(() => {
    console.log("[v0] ControlSidebar mounted")
  }, [])

  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    temperature: true,
    pressure: false,
    flow: false,
    reactivity: false,
    radiation: false,
    other: false,
  })

  const toggleSection = (key: string) => {
    console.log("[v0] Toggling section:", key)
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <aside className="w-80 bg-sidebar border-r border-sidebar-border overflow-y-auto">
      <div className="p-4 border-b border-sidebar-border">
        <h1 className="text-lg font-mono text-sidebar-foreground">REACTOR CONTROL</h1>
      </div>
      <div className="divide-y divide-sidebar-border">
        {categories.map((category) => (
          <div key={category.key} className="border-b border-sidebar-border">
            <button
              onClick={() => toggleSection(category.key)}
              className="w-full px-4 py-3 flex items-center justify-between bg-sidebar-accent hover:bg-sidebar-accent/80 transition-colors"
            >
              <span className="text-sm font-mono text-sidebar-foreground">{category.label}</span>
              <ChevronDown
                className={`w-4 h-4 text-sidebar-muted-foreground transition-transform ${
                  openSections[category.key] ? "rotate-180" : ""
                }`}
              />
            </button>
            {openSections[category.key] && (
              <div className="p-4 space-y-3 bg-sidebar">
                {Object.entries(parameters[category.key] || {}).map(([param, value]) => (
                  <div key={param} className="space-y-1.5">
                    <Label
                      htmlFor={`${category.key}-${param}`}
                      className="text-xs font-mono text-sidebar-muted-foreground uppercase"
                    >
                      {param.replace(/([A-Z])/g, " $1").trim()}
                    </Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id={`${category.key}-${param}`}
                        type="number"
                        value={value}
                        onChange={(e) => updateParameter(category.key, param, Number.parseFloat(e.target.value) || 0)}
                        className="h-8 bg-input border-border text-foreground font-mono text-sm"
                        step="0.1"
                      />
                      {category.unit && (
                        <span className="text-xs text-sidebar-muted-foreground font-mono min-w-[3rem]">
                          {category.unit}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  )
}
