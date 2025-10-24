"use client"

import { ChevronDown } from "lucide-react"
import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ControlSidebarProps {
  parameters: Record<string, Record<string, number>>
  updateParameter: (category: string, param: string, value: number) => void
  isSimulationRunning: boolean
  isLoading: boolean
  toggleSimulation: () => void
}

const categories = [
  { key: "temperature", label: "Температуры", unit: "°C" },
  { key: "pressure", label: "Давление", unit: "bar" },
  { key: "flow", label: "Потоки", unit: "%" },
  { key: "reactivity", label: "Реактивность", unit: "pcm" },
  { key: "radiation", label: "Радиация", unit: "mSv/h" },
  { key: "other", label: "Прочее", unit: "" },
]

/**
 * Mapping function to provide proper Russian labels for parameters
 * @param category - The parameter category
 * @param param - The parameter key
 * @returns Localized parameter label
 */
const getParameterLabel = (category: string, param: string): string => {
  const temperatureLabels: Record<string, string> = {
    timeSeconds: "Время (сек)",
    averageRcsTemperature: "Средняя температура RCS",
    hotLegTemperatureA: "Температура горячего канала А",
    hotLegTemperatureB: "Температура горячего канала В",
    coldLegTemperatureA: "Температура холодного канала А",
    coldLegTemperatureB: "Температура холодного канала В",
    steamGeneratorSteamFlowA: "Паровой поток парогенератора А",
    steamGeneratorSteamFlowB: "Паровой поток парогенератора В",
    reactorThermalPower: "Тепловая мощность реактора",
    turbineLoad: "Нагрузка турбины",
    sgTubeLeakageA: "Утечка труб SG A",
    sgTubeLeakageB: "Утечка труб SG B",
    pressurizerTemperature: "Температура прессуризатора",
    reactorBuildingTemperature: "Температура в здании реактора",
    pressurizerHeaterPower: "Мощность нагревателя прессуризатора",
    moderatorTemperatureReactivity: "Реактивность температуры модератора",
    neutronFluxPower: "Мощность нейтронного потока",
    submergedFuelTemperature: "Температура погруженного топлива",
    peakFuelTemperature: "Температура пикового топлива",
    averageFuelTemperature: "Средняя температура топлива",
    peakFuelCladdingTemperature: "Температура оболочки пикового топлива",
    accumulatorFlow: "Поток аккумулятора",
    radioactiveReleaseRateRB: "Скорость радиоактивного выброса RB",
    radioactiveReleaseRateSGValves: "Скорость радиоактивного выброса SG клапаны",
    radioactiveReleaseRateCondenser: "Скорость радиоактивного выброса конденсатор",
    doseToThyroidEAB: "Доза на щитовидную железу (EAB)",
    rwstWaterVolume: "Объем воды RWST",
    massOfMoltenConcrete: "Масса расплавленного бетона",
    debrisTemperatureInCavity: "Температура обломков в каверне",
    debrisTemperatureInLowerPlenum: "Температура обломков в нижнем пленуме",
    moltenConcreteTemperature: "Температура расплавленного бетона",
  }

  const reactivityLabels: Record<string, string> = {
    boronAcidReactivity: "Реактивность борной кислоты",
    moderatorTemperatureReactivity: "Реактивность температуры модератора",
    fuelReactivityDoppler: "Реактивность топлива (Допплер)",
    rodReactivity: "Реактивность стержней",
    totalReactivity: "Общая реактивность",
  }

  const radiationLabels: Record<string, string> = {
    radiationInBuilding: "Радиация в здании",
    radiationInSteamLine: "Радиация в паропроводе",
    condenserRadiation: "Радиация конденсатора",
    auxiliaryBuildingRadiation: "Радиация вспомогательного здания",
    rcsActivity: "Активность RCS",
    i131ConcentrationInRcs: "Концентрация I-131 в RCS",
  }

  const miscellaneousLabels: Record<string, string> = {
    rcsLiquidVolume: "Объем жидкости в RCS",
    rcsAirVolume: "Объем воздуха в RCS",
    sgWaterLevelAWideRange: "Уровень воды SG A (широкий диапазон)",
    sgWaterLevelBWideRange: "Уровень воды SG B (широкий диапазон)",
    sgHeatRemovalA: "Теплоотвод SG A",
    sgHeatRemovalB: "Теплоотвод SG B",
    sgWaterLevelANarrowRange: "Уровень воды SG A (узкий диапазон)",
    sgWaterLevelBNarrowRange: "Уровень воды SG B (узкий диапазон)",
    rhrPower: "Мощность RHR",
    coreWaterLevel: "Уровень воды в активной зоне",
    makeupReserveChannelA: "Запас подпитки канала А",
    makeupReserveChannelB: "Запас подпитки канала В",
    claddingDamageFraction: "Фракция повреждения оболочки",
    departureFromNucleateBoilingRatio: "Отношение отрыва от кипения",
    coolingFanPower: "Мощность охлаждающего вентилятора",
    massOfHydrogenEvolvedFromZrH2O: "Масса водорода, выделенного Zr-H₂O",
    hydrogenConcentrationInRB: "Концентрация водорода в RB",
    massOfLeakageFromRB: "Масса утечки из RB",
    massOfLeakageFromSG: "Масса утечки из SG",
    integratedRuptureFlow: "Интегрированный поток разрыва",
    integratedRuptureEnergy: "Интегрированная энергия разрыва",
    zrOxidationFraction: "Фракция окисления Zr",
    massOfCoriumInDW: "Масса кория в DW",
    massOfCCIGases: "Масса газов CCI",
    boronConcentrationInRCS: "Концентрация бора в RCS",
    channelAFlowRatio: "Соотношение потока канала А",
    channelBFlowRatio: "Соотношение потока канала В",
    coreFlowRatio: "Соотношение потока активной зоны",
  }

  const flowLabels: Record<string, string> = {
    reactorCoolantFlowA: "Поток охлаждающей жидкости реактора А",
    reactorCoolantFlowB: "Поток охлаждающей жидкости реактора В",
    steamGeneratorWaterFeedA: "Подача воды парогенератора А",
    steamGeneratorWaterFeedB: "Подача воды парогенератора В",
    steamGeneratorSteamFlowA: "Паровой поток парогенератора А",
    steamGeneratorSteamFlowB: "Паровой поток парогенератора В",
    rcsWaterLeakage: "Утечка воды из RCS",
    waterFeedFromPressurizerSafetyValves: "Подача воды из прессуризатора и защитных клапанов",
    rcsLeakEnthalpy: "Энтальпия утечки RCS",
    hpiFlow: "Поток HPI",
    eccsFlow: "Поток ECCS",
    reactorThermalPower: "Тепловая мощность реактора",
    sgTubeLeakageA: "Утечка труб SG A",
    sgTubeLeakageB: "Утечка труб SG B",
    waterLevelRBSump: "Уровень воды в сборнике RB",
    flowThroughRuptureRB: "Поток через разрыв в RB",
    pressurizerSprayFlow: "Подача спрея прессуризатора",
    containmentSprayFlow: "Подача спрея корпуса",
    neutronFluxPower: "Мощность нейтронного потока",
    coreThermalPower: "Тепловая мощность активной зоны",
    accumulatorFlow: "Поток аккумулятора",
    lpsiRhrFlow: "Поток LPSI (RHR)",
    makeupFlow: "Поток подпитки",
    doseToBodyEAB: "Доза на тело (EAB)",
    msvAdvFlowSGA: "Поток MSV/ADV SG A",
    msvAdvFlowSGB: "Поток MSV/ADV SG B",
    letdownFlow: "Поток отбора",
    flowThroughFWBreakLine: "Поток по линии FW Break",
  }

  const pressureLabels: Record<string, string> = {
    steamGeneratorPressureA: "Давление парогенератора А",
    steamGeneratorPressureB: "Давление парогенератора В",
    pressurizerPressureLevel: "Уровень давления в прессуризаторе",
    waterFeedFromPressurizer: "Подача воды из прессуризатора",
    waterEnthalpyFromPressurizer: "Энтальпия воды из прессуризатора",
    hpiFlow: "Поток HPI",
    reactorBuildingPressure: "Давление в здании реактора",
    partialAirPressureRB: "Частичное давление воздуха в RB",
    pressurizerSprayFlow: "Подача спрея прессуризатора",
    containmentSprayFlow: "Подача спрея корпуса",
    neutronFluxPower: "Мощность нейтронного потока",
    coreThermalPower: "Тепловая мощность активной зоны",
    peakFuelTemperature: "Температура пикового топлива",
    peakFuelCladdingTemperature: "Температура оболочки пикового топлива",
    lpsiRhrFlow: "Поток LPSI (RHR)",
    rcsPressure: "Давление в RCS",
    debrisTemperatureLowerPlenum: "Температура обломков в нижнем пленуме",
  }

  if (category === "temperature" && temperatureLabels[param]) {
    return temperatureLabels[param]
  }

  if (category === "flow" && flowLabels[param]) {
    return flowLabels[param]
  }

  if (category === "reactivity" && reactivityLabels[param]) {
    return reactivityLabels[param]
  }

  if (category === "radiation" && radiationLabels[param]) {
    return radiationLabels[param]
  }

  if (category === "other" && miscellaneousLabels[param]) {
    return miscellaneousLabels[param]
  }

  if (category === "pressure" && pressureLabels[param]) {
    return pressureLabels[param]
  }

  // Fallback to the original formatting for other categories
  return param.replace(/([A-Z])/g, " $1").trim()
}

/**
 * Get appropriate unit for a specific parameter
 * @param category - The parameter category
 * @param param - The parameter key
 * @returns Unit string
 */
const getParameterUnit = (category: string, param: string): string => {
  const temperatureUnits: Record<string, string> = {
    timeSeconds: "сек",
    averageRcsTemperature: "°C",
    hotLegTemperatureA: "°C",
    hotLegTemperatureB: "°C",
    coldLegTemperatureA: "°C",
    coldLegTemperatureB: "°C",
    steamGeneratorSteamFlowA: "kg/s",
    steamGeneratorSteamFlowB: "kg/s",
    reactorThermalPower: "MW",
    turbineLoad: "MW",
    sgTubeLeakageA: "kg/s",
    sgTubeLeakageB: "kg/s",
    pressurizerTemperature: "°C",
    reactorBuildingTemperature: "°C",
    pressurizerHeaterPower: "kW",
    moderatorTemperatureReactivity: "pcm",
    neutronFluxPower: "MW",
    submergedFuelTemperature: "°C",
    peakFuelTemperature: "°C",
    averageFuelTemperature: "°C",
    peakFuelCladdingTemperature: "°C",
    accumulatorFlow: "kg/s",
    radioactiveReleaseRateRB: "Bq/s",
    radioactiveReleaseRateSGValves: "Bq/s",
    radioactiveReleaseRateCondenser: "Bq/s",
    doseToThyroidEAB: "mSv",
    rwstWaterVolume: "m³",
    massOfMoltenConcrete: "kg",
    debrisTemperatureInCavity: "°C",
    debrisTemperatureInLowerPlenum: "°C",
    moltenConcreteTemperature: "°C",
  }

  const flowUnits: Record<string, string> = {
    reactorCoolantFlowA: "kg/s",
    reactorCoolantFlowB: "kg/s",
    steamGeneratorWaterFeedA: "kg/s",
    steamGeneratorWaterFeedB: "kg/s",
    steamGeneratorSteamFlowA: "kg/s",
    steamGeneratorSteamFlowB: "kg/s",
    rcsWaterLeakage: "kg/s",
    waterFeedFromPressurizerSafetyValves: "kg/s",
    rcsLeakEnthalpy: "kJ/kg",
    hpiFlow: "kg/s",
    eccsFlow: "kg/s",
    reactorThermalPower: "MW",
    sgTubeLeakageA: "kg/s",
    sgTubeLeakageB: "kg/s",
    waterLevelRBSump: "m",
    flowThroughRuptureRB: "kg/s",
    pressurizerSprayFlow: "kg/s",
    containmentSprayFlow: "kg/s",
    neutronFluxPower: "MW",
    coreThermalPower: "MW",
    accumulatorFlow: "kg/s",
    lpsiRhrFlow: "kg/s",
    makeupFlow: "kg/s",
    doseToBodyEAB: "mSv",
    msvAdvFlowSGA: "kg/s",
    msvAdvFlowSGB: "kg/s",
    letdownFlow: "kg/s",
    flowThroughFWBreakLine: "kg/s",
  }

  if (category === "temperature" && temperatureUnits[param]) {
    return temperatureUnits[param]
  }

  if (category === "flow" && flowUnits[param]) {
    return flowUnits[param]
  }

  if (category === "reactivity") {
    const reactivityUnits: Record<string, string> = {
      boronAcidReactivity: "pcm",
      moderatorTemperatureReactivity: "pcm",
      fuelReactivityDoppler: "pcm",
      rodReactivity: "pcm",
      totalReactivity: "pcm",
    }
    return reactivityUnits[param] || "pcm"
  }

  if (category === "radiation") {
    const radiationUnits: Record<string, string> = {
      radiationInBuilding: "mSv/h",
      radiationInSteamLine: "mSv/h",
      condenserRadiation: "mSv/h",
      auxiliaryBuildingRadiation: "mSv/h",
      rcsActivity: "Bq/m³",
      i131ConcentrationInRcs: "Bq/m³",
    }
    return radiationUnits[param] || "mSv/h"
  }

  if (category === "other") {
    const miscellaneousUnits: Record<string, string> = {
      rcsLiquidVolume: "m³",
      rcsAirVolume: "m³",
      sgWaterLevelAWideRange: "%",
      sgWaterLevelBWideRange: "%",
      sgHeatRemovalA: "MW",
      sgHeatRemovalB: "MW",
      sgWaterLevelANarrowRange: "%",
      sgWaterLevelBNarrowRange: "%",
      rhrPower: "MW",
      coreWaterLevel: "%",
      makeupReserveChannelA: "%",
      makeupReserveChannelB: "%",
      claddingDamageFraction: "",
      departureFromNucleateBoilingRatio: "",
      coolingFanPower: "kW",
      massOfHydrogenEvolvedFromZrH2O: "kg",
      hydrogenConcentrationInRB: "%",
      massOfLeakageFromRB: "kg",
      massOfLeakageFromSG: "kg",
      integratedRuptureFlow: "kg",
      integratedRuptureEnergy: "MJ",
      zrOxidationFraction: "",
      massOfCoriumInDW: "kg",
      massOfCCIGases: "kg",
      boronConcentrationInRCS: "ppm",
      channelAFlowRatio: "",
      channelBFlowRatio: "",
      coreFlowRatio: "",
    }
    return miscellaneousUnits[param] || ""
  }

  if (category === "pressure") {
    const pressureUnits: Record<string, string> = {
      steamGeneratorPressureA: "bar",
      steamGeneratorPressureB: "bar",
      pressurizerPressureLevel: "bar",
      waterFeedFromPressurizer: "kg/s",
      waterEnthalpyFromPressurizer: "kJ/kg",
      hpiFlow: "kg/s",
      reactorBuildingPressure: "bar",
      partialAirPressureRB: "bar",
      pressurizerSprayFlow: "kg/s",
      containmentSprayFlow: "kg/s",
      neutronFluxPower: "%",
      coreThermalPower: "MW",
      peakFuelTemperature: "°C",
      peakFuelCladdingTemperature: "°C",
      lpsiRhrFlow: "kg/s",
      rcsPressure: "bar",
      debrisTemperatureLowerPlenum: "°C",
    }
    return pressureUnits[param] || "bar"
  }

  // Return default units for other categories
  const categoryUnits: Record<string, string> = {
    temperature: "°C",
    pressure: "bar",
    flow: "%",
    reactivity: "pcm",
    radiation: "mSv/h",
    other: "",
  }
  
  return categoryUnits[category] || ""
}

export default function ControlSidebar({ parameters, updateParameter, isSimulationRunning, isLoading, toggleSimulation }: ControlSidebarProps) {
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
        <div className="mt-4">
          <button
            onClick={toggleSimulation}
            disabled={isLoading}
            className={`w-full px-4 py-3 font-mono text-sm font-bold rounded transition-colors flex items-center justify-center gap-2 ${
              isLoading
                ? "bg-yellow-600 text-white cursor-not-allowed"
                : isSimulationRunning
                ? "bg-red-600 hover:bg-red-700 text-white"
                : "bg-green-600 hover:bg-green-700 text-white"
            }`}
          >
            {isLoading && (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            )}
            {isLoading ? "INITIALIZING..." : isSimulationRunning ? "STOP SIMULATION" : "START SIMULATION"}
          </button>
        </div>
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
                      className="text-xs font-mono text-sidebar-muted-foreground"
                    >
                      {getParameterLabel(category.key, param)}
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
                      {getParameterUnit(category.key, param) && (
                        <span className="text-xs text-sidebar-muted-foreground font-mono min-w-[3rem]">
                          {getParameterUnit(category.key, param)}
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
