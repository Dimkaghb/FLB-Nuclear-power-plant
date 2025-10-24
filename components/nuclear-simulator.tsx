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
      timeSeconds: 0,                          // Время (сек)
      averageRcsTemperature: 295.0,            // Средняя температура RCS
      hotLegTemperatureA: 325.0,               // Температура горячего канала А
      hotLegTemperatureB: 325.0,               // Температура горячего канала В
      coldLegTemperatureA: 290.0,              // Температура холодного канала А
      coldLegTemperatureB: 290.0,              // Температура холодного канала В
      steamGeneratorSteamFlowA: 1500.0,        // Паровой поток парогенератора А
      steamGeneratorSteamFlowB: 1500.0,        // Паровой поток парогенератора В
      reactorThermalPower: 3000.0,             // Тепловая мощность реактора
      turbineLoad: 1000.0,                     // Нагрузка турбины
      sgTubeLeakageA: 0.0,                     // Утечка труб SG A
      sgTubeLeakageB: 0.0,                     // Утечка труб SG B
      pressurizerTemperature: 345.0,           // Температура прессуризатора
      reactorBuildingTemperature: 25.0,        // Температура в здании реактора
      pressurizerHeaterPower: 0.0,             // Мощность нагревателя прессуризатора
      moderatorTemperatureReactivity: -0.2,    // Реактивность температуры модератора
      neutronFluxPower: 100.0,                 // Мощность нейтронного потока
      submergedFuelTemperature: 1100.0,        // Температура погруженного топлива
      peakFuelTemperature: 1200.0,             // Температура пикового топлива
      averageFuelTemperature: 1000.0,          // Средняя температура топлива
      peakFuelCladdingTemperature: 650.0,      // Температура оболочки пикового топлива
      accumulatorFlow: 0.0,                    // Поток аккумулятора
      radioactiveReleaseRateRB: 0.0,           // Скорость радиоактивного выброса RB
      radioactiveReleaseRateSGValves: 0.0,     // Скорость радиоактивного выброса SG клапаны
      radioactiveReleaseRateCondenser: 0.0,    // Скорость радиоактивного выброса конденсатор
      doseToThyroidEAB: 0.0,                   // Доза на щитовидную железу (EAB)
      rwstWaterVolume: 2000.0,                 // Объем воды RWST
      massOfMoltenConcrete: 0.0,               // Масса расплавленного бетона
      debrisTemperatureInCavity: 300.0,        // Температура обломков в каверне
      debrisTemperatureInLowerPlenum: 300.0,   // Температура обломков в нижнем пленуме
      moltenConcreteTemperature: 0.0,          // Температура расплавленного бетона
    },
    pressure: {
      steamGeneratorPressureA: 70.0,           // Давление парогенератора А
      steamGeneratorPressureB: 70.0,           // Давление парогенератора В  
      pressurizerPressureLevel: 155.0,         // Уровень давления в прессуризаторе
      waterFeedFromPressurizer: 0.0,           // Подача воды из прессуризатора и защитных клапанов
      waterEnthalpyFromPressurizer: 2800.0,    // Энтальпия воды из прессуризатора
      hpiFlow: 0.0,                            // Поток HPI
      reactorBuildingPressure: 1.0,            // Давление в здании реактора
      partialAirPressureRB: 0.8,               // Частичное давление воздуха в RB
      pressurizerSprayFlow: 0.0,               // Подача спрея прессуризатора
      containmentSprayFlow: 0.0,               // Подача спрея корпуса
      neutronFluxPower: 100.0,                 // Мощность нейтронного потока
      coreThermalPower: 3000.0,                // Тепловая мощность активной зоны
      peakFuelTemperature: 1200.0,             // Температура пикового топлива
      peakFuelCladdingTemperature: 650.0,      // Температура оболочки пикового топлива
      lpsiRhrFlow: 0.0,                        // Поток LPSI (RHR)
      rcsPressure: 155.0,                      // Давление в RCS
      debrisTemperatureLowerPlenum: 300.0,     // Температура обломков в нижнем пленуме
    },
    flow: {
      reactorCoolantFlowA: 100, // Поток охлаждающей жидкости реактора А
      reactorCoolantFlowB: 100, // Поток охлаждающей жидкости реактора В
      steamGeneratorWaterFeedA: 80, // Подача воды парогенератора А
      steamGeneratorWaterFeedB: 80, // Подача воды парогенератора В
      steamGeneratorSteamFlowA: 75, // Паровой поток парогенератора А
      steamGeneratorSteamFlowB: 75, // Паровой поток парогенератора В
      rcsWaterLeakage: 0, // Утечка воды из RCS
      waterFeedFromPressurizerSafetyValves: 0, // Подача воды из прессуризатора и защитных клапанов
      rcsLeakEnthalpy: 0, // Энтальпия утечки RCS
      hpiFlow: 0, // Поток HPI
      eccsFlow: 0, // Поток ECCS
      reactorThermalPower: 3000, // Тепловая мощность реактора
      sgTubeLeakageA: 0, // Утечка труб SG A
      sgTubeLeakageB: 0, // Утечка труб SG B
      waterLevelRBSump: 0, // Уровень воды в сборнике RB
      flowThroughRuptureRB: 0, // Поток через разрыв в RB
      pressurizerSprayFlow: 0, // Подача спрея прессуризатора
      containmentSprayFlow: 0, // Подача спрея корпуса
      neutronFluxPower: 3500, // Мощность нейтронного потока
      coreThermalPower: 3000, // Тепловая мощность активной зоны
      accumulatorFlow: 0, // Поток аккумулятора
      lpsiRhrFlow: 0, // Поток LPSI (RHR)
      makeupFlow: 5, // Поток подпитки
      doseToBodyEAB: 0, // Доза на тело (EAB)
      msvAdvFlowSGA: 0, // Поток MSV/ADV SG A
      msvAdvFlowSGB: 0, // Поток MSV/ADV SG B
      letdownFlow: 3, // Поток отбора
      flowThroughFWBreakLine: 0, // Поток по линии FW Break
    },
    reactivity: {
      boronAcidReactivity: 1200, // Реактивность борной кислоты
      moderatorTemperatureReactivity: -0.1, // Реактивность температуры модератора
      fuelReactivityDoppler: -0.3, // Реактивность топлива (Допплер)
      rodReactivity: 50, // Реактивность стержней
      totalReactivity: 0.0, // Общая реактивность
    },
    radiation: {
      radiationInBuilding: 0.1, // Радиация в здании
      radiationInSteamLine: 0.02, // Радиация в паропроводе
      condenserRadiation: 0.05, // Радиация конденсатора
      auxiliaryBuildingRadiation: 0.08, // Радиация вспомогательного здания
      rcsActivity: 50, // Активность RCS
      i131ConcentrationInRcs: 1.5, // Концентрация I-131 в RCS
    },
    other: {
      rcsLiquidVolume: 320.5, // Объем жидкости в RCS
      rcsAirVolume: 15.2, // Объем воздуха в RCS
      sgWaterLevelAWideRange: 75.3, // Уровень воды SG A (широкий диапазон)
      sgWaterLevelBWideRange: 74.8, // Уровень воды SG B (широкий диапазон)
      sgHeatRemovalA: 850.2, // Теплоотвод SG A
      sgHeatRemovalB: 847.6, // Теплоотвод SG B
      sgWaterLevelANarrowRange: 76.1, // Уровень воды SG A (узкий диапазон)
      sgWaterLevelBNarrowRange: 75.4, // Уровень воды SG B (узкий диапазон)
      rhrPower: 125.8, // Мощность RHR
      coreWaterLevel: 95.2, // Уровень воды в активной зоне
      makeupReserveChannelA: 85.7, // Запас подпитки канала А
      makeupReserveChannelB: 84.3, // Запас подпитки канала В
      claddingDamageFraction: 0.02, // Фракция повреждения оболочки
      departureFromNucleateBoilingRatio: 2.15, // Отношение отрыва от кипения
      coolingFanPower: 45.6, // Мощность охлаждающего вентилятора
      massOfHydrogenEvolvedFromZrH2O: 12.3, // Масса водорода, выделенного Zr-H2O
      hydrogenConcentrationInRB: 0.8, // Концентрация водорода в RB
      massOfLeakageFromRB: 2.1, // Масса утечки из RB
      massOfLeakageFromSG: 1.5, // Масса утечки из SG
      integratedRuptureFlow: 45.2, // Интегрированный поток разрыва
      integratedRuptureEnergy: 125.8, // Интегрированная энергия разрыва
      zrOxidationFraction: 0.15, // Фракция окисления Zr
      massOfCoriumInDW: 0.0, // Масса кория в DW
      massOfCCIGases: 0.0, // Масса газов CCI
      boronConcentrationInRCS: 1250.0, // Концентрация бора в RCS
      channelAFlowRatio: 1.02, // Соотношение потока канала А
      channelBFlowRatio: 0.98, // Соотношение потока канала В
      coreFlowRatio: 1.0, // Соотношение потока активной зоны
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
