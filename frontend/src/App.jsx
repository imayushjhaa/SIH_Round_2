import React, { useState, useEffect } from "react";
import axios from "axios";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  TrendingDown, 
  Layers, 
  Sliders, 
  Scale,
  FileText,
  Printer,
  X,
  Sparkles,
  Search,
  RotateCcw,
  Check,
  Calendar,
  ShieldAlert,
  AlertOctagon
} from "lucide-react";

const BACKEND_URL = "http://127.0.0.1:8000";

// RFCTLARR 2013 5-Stage Statutory Pipeline Definition
const STATUTORY_STAGES = [
  { id: "sec11", label: "Sec 11", full: "Section 11 (Notice)", window: "Day 0" },
  { id: "sec15", label: "Sec 15", full: "Section 15 (Hearing)", window: "60 Days" },
  { id: "sec19", label: "Sec 19", full: "Section 19 (Declaration)", window: "Max 365 Days" },
  { id: "award", label: "Sec 23", full: "Award Enquiry / Sec 23", window: "+12 Months" },
  { id: "possession", label: "Possession", full: "Physical Possession", window: "Post-Award" },
];

// Helper: Format ISO Date into Clean Reading Format
const formatLegalDate = (dateStr) => {
  if (!dateStr) return "N/A";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
};

// Helper: Calculate Statutory Expiration (Sec 11 Date + 365 Days)
const calculateSec19Deadline = (sec11DateStr) => {
  if (!sec11DateStr) return "N/A";
  const d = new Date(sec11DateStr);
  d.setDate(d.getDate() + 365);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
};

// Sub-component: Smooth Fly-To & Zoom Controller
function MapController({ selectedPlot, geoData }) {
  const map = useMap();

  useEffect(() => {
    if (!selectedPlot || !geoData?.features) return;
    const feature = geoData.features.find(
      (f) => f.properties.khasra_no === selectedPlot
    );
    if (feature?.geometry?.coordinates) {
      const coords = feature.geometry.coordinates[0];
      const lats = coords.map((c) => c[1]);
      const lngs = coords.map((c) => c[0]);
      const bounds = [
        [Math.min(...lats), Math.min(...lngs)],
        [Math.max(...lats), Math.max(...lngs)],
      ];
      map.flyToBounds(bounds, { padding: [60, 60], maxZoom: 18, duration: 1.2 });
    }
  }, [selectedPlot, geoData, map]);

  return null;
}

// Sub-component: RFCTLARR Statutory Pipeline & Timeline Monitor
function StatutoryTimelineModule({ plotInfo }) {
  const getStageIndex = (stageName) => {
    if (!stageName) return 0;
    const s = stageName.toLowerCase();
    if (s.includes("11") || s.includes("notice")) return 0;
    if (s.includes("15") || s.includes("hearing")) return 1;
    if (s.includes("19") || s.includes("declaration")) return 2;
    if (s.includes("award") || s.includes("23") || s.includes("enquiry")) return 3;
    if (s.includes("possession")) return 4;
    return 1;
  };

  const activeIndex = getStageIndex(plotInfo.stage);
  const isLapsed = plotInfo.statutory_days_left < 0 && activeIndex < 2;
  const isCritical = plotInfo.statutory_days_left >= 0 && plotInfo.statutory_days_left < 45 && activeIndex < 2;
  const deadline = calculateSec19Deadline(plotInfo.sec_11_date);

  return (
    <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-bold tracking-wide uppercase text-slate-700 flex items-center gap-1.5">
          <Scale size={13} className="text-amber-600" /> RFCTLARR Statutory Pipeline
        </span>
        <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-semibold">
          Stage {activeIndex + 1} of 5
        </span>
      </div>

      {/* 5-Stage Stepper Track */}
      <div className="relative flex items-center justify-between pt-1 pb-1">
        <div className="absolute top-[13px] left-3 right-3 h-0.5 bg-slate-200 z-0"></div>
        <div 
          className="absolute top-[13px] left-3 h-0.5 bg-emerald-500 z-0 transition-all duration-500"
          style={{ width: `${(activeIndex / (STATUTORY_STAGES.length - 1)) * 90}%` }}
        ></div>

        {STATUTORY_STAGES.map((stg, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div key={stg.id} className="relative z-10 flex flex-col items-center">
              <div 
                className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                  isDone 
                    ? "bg-emerald-500 text-white shadow-xs" 
                    : isCurrent 
                    ? isLapsed
                      ? "bg-red-600 text-white ring-4 ring-red-100 animate-pulse"
                      : "bg-blue-600 text-white ring-4 ring-blue-100 shadow-sm" 
                    : "bg-white text-slate-400 border-2 border-slate-300"
                }`}
              >
                {isDone ? <Check size={12} strokeWidth={3} /> : idx + 1}
              </div>
              <span 
                className={`text-[9px] mt-1.5 font-semibold whitespace-nowrap ${
                  isCurrent 
                    ? isLapsed ? "text-red-700 font-bold" : "text-blue-700 font-bold" 
                    : isDone 
                    ? "text-emerald-700" 
                    : "text-slate-400"
                }`}
              >
                {stg.label}
              </span>
              <span className="text-[8px] text-slate-400 scale-90 -mt-0.5">{stg.window}</span>
            </div>
          );
        })}
      </div>

      {/* Statutory Timeline Details & Expiry Card */}
      <div className={`p-2.5 rounded border text-xs space-y-1.5 ${
        isLapsed 
          ? "bg-red-50/80 border-red-300 text-red-900" 
          : isCritical 
          ? "bg-amber-50/80 border-amber-300 text-amber-900" 
          : "bg-white border-slate-200 text-slate-700"
      }`}>
        <div className="flex items-center justify-between font-medium">
          <span className="flex items-center gap-1">
            <Calendar size={12} className="text-slate-500" /> Sec 11 Notification:
          </span>
          <span className="font-semibold text-slate-900">{formatLegalDate(plotInfo.sec_11_date)}</span>
        </div>

        <div className="flex items-center justify-between font-medium">
          <span className="flex items-center gap-1">
            <Clock size={12} className="text-slate-500" /> Sec 19 Lapsing Deadline:
          </span>
          <span className="font-semibold text-slate-900">{deadline}</span>
        </div>

        <div className="pt-1 border-t border-slate-200/60 flex items-center justify-between font-bold">
          <span>Statutory Status:</span>
          {isLapsed ? (
            <span className="text-red-600 flex items-center gap-1 text-[11px]">
              <ShieldAlert size={12} /> LAPSED under Sec 19(7) ({Math.abs(plotInfo.statutory_days_left)}d Overdue)
            </span>
          ) : isCritical ? (
            <span className="text-amber-700 flex items-center gap-1 text-[11px]">
              <AlertTriangle size={12} /> Expiration Imminent ({plotInfo.statutory_days_left} Days Left)
            </span>
          ) : (
            <span className="text-emerald-700 text-[11px]">
              Active ({plotInfo.statutory_days_left} Days Remaining)
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [geoData, setGeoData] = useState(null);
  const [selectedPlot, setSelectedPlot] = useState(null);
  const [plotDetails, setPlotDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [showNoticeModal, setShowNoticeModal] = useState(false);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("ALL");

  // What-If Simulation State
  const [simDisbursement, setSimDisbursement] = useState(50);
  const [resolveKhata, setResolveKhata] = useState(false);
  const [resolveForest, setResolveForest] = useState(false);
  const [simResult, setSimResult] = useState(null);

  useEffect(() => {
    axios.get(`${BACKEND_URL}/api/dashboard/summary`)
      .then(res => setSummary(res.data))
      .catch(err => console.error("Summary error:", err));

    axios.get(`${BACKEND_URL}/api/parcels`)
      .then(res => setGeoData(res.data))
      .catch(err => console.error("GeoJSON error:", err));
  }, []);

  const handleParcelClick = (khasraNo) => {
    setSelectedPlot(khasraNo);
    setLoadingDetails(true);
    setSimResult(null);

    axios.get(`${BACKEND_URL}/api/plot/${encodeURIComponent(khasraNo)}`)
      .then(res => {
        setPlotDetails(res.data);
        setSimDisbursement(res.data.plot_info.disbursement_pct);
        setResolveKhata(res.data.plot_info.unpartitioned_khata === 1);
        setResolveForest(false);
      })
      .catch(err => console.error("Plot details error:", err))
      .finally(() => setLoadingDetails(false));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || !geoData) return;
    const found = geoData.features.find(f => 
      f.properties.khasra_no.toLowerCase().includes(searchQuery.trim().toLowerCase())
    );
    if (found) {
      handleParcelClick(found.properties.khasra_no);
    }
  };

  const runSimulation = () => {
    if (!selectedPlot) return;
    axios.post(`${BACKEND_URL}/api/simulate`, {
      khasra_no: selectedPlot,
      simulated_disbursement_pct: parseFloat(simDisbursement),
      resolve_khata: resolveKhata,
      resolve_forest: resolveForest
    })
      .then(res => setSimResult(res.data))
      .catch(err => console.error("Simulation error:", err));
  };

  const resetSimulation = () => {
    if (!plotDetails) return;
    setSimResult(null);
    setSimDisbursement(plotDetails.plot_info.disbursement_pct);
    setResolveKhata(plotDetails.plot_info.unpartitioned_khata === 1);
    setResolveForest(false);
  };

  const polygonStyle = (feature) => {
    const props = feature.properties;
    const isSelected = selectedPlot === props.khasra_no;
    
    // Statutory Reality Check:
    // Lapsed (< 0) or nearing statutory lapse (< 45 days) MUST render RED under RFCTLARR Sec 19(7)
    const isStatutoryCritical = props.statutory_days_left < 45 && props.stage !== "Possession Taken";
    let effectiveColor = isStatutoryCritical ? "red" : props.status_color;

    // Check Filter Criteria
    let matchesFilter = true;
    if (activeFilter === "LAPSE") {
      matchesFilter = isStatutoryCritical;
    } else if (activeFilter === "HIGH_RISK") {
      matchesFilter = props.risk_tier === "Critical" || props.risk_tier === "High" || effectiveColor === "red";
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      matchesFilter = matchesFilter && (
        props.khasra_no.toLowerCase().includes(q) || 
        (props.village && props.village.toLowerCase().includes(q))
      );
    }

    // Dynamic Simulation Recolor
    const isSimulatedPlot = simResult && simResult.khasra_no === props.khasra_no;
    if (isSimulatedPlot) {
      if (simResult.new_predicted_delay_days < 45) {
        effectiveColor = "green";
      } else if (simResult.new_predicted_delay_days < 90) {
        effectiveColor = "yellow";
      }
    }

    const baseFill = effectiveColor === "red" ? "#ef4444" : effectiveColor === "yellow" ? "#eab308" : "#22c55e";

    return {
      fillColor: baseFill,
      weight: isSelected ? 3.5 : 1.5,
      opacity: matchesFilter ? 0.95 : 0.2,
      color: isSelected ? "#38bdf8" : isSimulatedPlot ? "#22c55e" : "#ffffff",
      dashArray: isSelected ? "" : "3",
      fillOpacity: matchesFilter ? (isSelected ? 0.8 : 0.45) : 0.08
    };
  };

  const isPlotLapsed = plotDetails && plotDetails.plot_info.statutory_days_left < 0;

  return (
    <div className="flex flex-col h-screen bg-slate-100 font-sans text-slate-800">
      {/* Top Header */}
      <header className="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-md">
        <div>
          <h1 className="text-xl font-bold tracking-wide flex items-center gap-2">
            <Scale className="text-amber-400" size={24} />
            PRAGATI-Land : Statutory Compliance & Delay Mitigation Engine
          </h1>
          <p className="text-xs text-slate-400">
            RFCTLARR Act 2013 Statutory Timeline Monitor & Decision Support System
          </p>
        </div>
        <div className="text-xs bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700 text-amber-300 font-medium">
          Active Stretch: {summary?.active_corridor || "Loading..."}
        </div>
      </header>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-4 gap-4 px-6 py-3 bg-white border-b border-slate-200">
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
          <p className="text-xs text-slate-500 font-medium">Total Land Parcels</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{summary?.total_parcels ?? "--"}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Contiguous Corridor Sector</p>
        </div>

        <div className="p-3 bg-red-50/70 border border-red-200 rounded-lg">
          <div className="flex items-center justify-between">
            <p className="text-xs text-red-700 font-semibold flex items-center gap-1.5">
              <AlertTriangle size={14} className="text-red-500" /> Section 19 Lapse Alert
            </p>
            <span className="text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">
              &lt; 45 Days
            </span>
          </div>
          <p className="text-2xl font-bold text-red-700 mt-1">{summary?.critical_lapsing_parcels ?? "--"}</p>
          <p className="text-[11px] text-red-500/80 mt-0.5">Parcels nearing statutory cancellation</p>
        </div>

        <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg">
          <p className="text-xs text-amber-700 font-medium">High Delay Risk Parcels</p>
          <p className="text-2xl font-bold text-amber-800 mt-1">{summary?.high_risk_parcels ?? "--"}</p>
          <p className="text-[11px] text-amber-600/80 mt-0.5">Predicted delay exceeding 90 days</p>
        </div>

        <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
          <p className="text-xs text-emerald-700 font-medium">Avg Disbursement Velocity</p>
          <p className="text-2xl font-bold text-emerald-800 mt-1">{summary?.avg_disbursement_pct ?? "--"}%</p>
          <p className="text-[11px] text-emerald-600/80 mt-0.5">Award compensation cleared</p>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden p-4 gap-4">
        {/* Left Side: Cadastral Satellite Map */}
        <div className="w-2/3 h-full relative rounded-xl overflow-hidden shadow-md border border-slate-300">
          
          {/* Map Controls */}
          <div className="absolute top-3 right-3 z-[1000] flex items-center gap-2">
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                placeholder="Search Khasra (e.g. KH-643)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-900/90 text-white text-xs px-3 py-2 pl-8 rounded-lg border border-slate-700 placeholder-slate-400 focus:outline-none focus:border-amber-400 shadow-md backdrop-blur-sm w-44 transition-all focus:w-52"
              />
              <Search size={13} className="absolute left-2.5 top-2.5 text-slate-400" />
            </form>

            <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-700 backdrop-blur-sm shadow-md text-xs">
              <button
                type="button"
                onClick={() => setActiveFilter("ALL")}
                className={`px-2 py-1 rounded font-medium transition-all ${
                  activeFilter === "ALL" 
                    ? "bg-amber-400 text-slate-950 font-bold" 
                    : "text-slate-300 hover:text-white"
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setActiveFilter("LAPSE")}
                className={`px-2 py-1 rounded font-medium flex items-center gap-1 transition-all ${
                  activeFilter === "LAPSE" 
                    ? "bg-red-500 text-white font-bold" 
                    : "text-red-300 hover:text-white"
                }`}
              >
                &lt;45d Lapse
              </button>
              <button
                type="button"
                onClick={() => setActiveFilter("HIGH_RISK")}
                className={`px-2 py-1 rounded font-medium transition-all ${
                  activeFilter === "HIGH_RISK" 
                    ? "bg-amber-500 text-white font-bold" 
                    : "text-amber-300 hover:text-white"
                }`}
              >
                High Risk
              </button>
            </div>
          </div>

          {/* Map Legend */}
          <div className="absolute top-3 left-12 z-[1000] bg-slate-900/90 text-white px-3 py-2 rounded-md shadow-md border border-slate-700 text-xs flex gap-3 backdrop-blur-sm">
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 bg-emerald-500 rounded-sm inline-block"></span> Safe</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 bg-amber-500 rounded-sm inline-block"></span> Under Review</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 bg-red-500 rounded-sm inline-block"></span> Dispute / Risk</span>
          </div>

          {geoData && (
            <MapContainer 
              key="satellite-map"
              center={[28.7545, 76.9185]} 
              zoom={16} 
              maxZoom={19}
              scrollWheelZoom={true} 
              className="w-full h-full"
            >
              <TileLayer
                attribution='Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              />
              <GeoJSON
                key={`${JSON.stringify(geoData?.features?.length)}-${activeFilter}-${searchQuery}-${selectedPlot}-${simResult?.new_predicted_delay_days}`}
                data={geoData}
                style={polygonStyle}
                onEachFeature={(feature, layer) => {
                  const isSim = simResult && simResult.khasra_no === feature.properties.khasra_no;
                  layer.bindTooltip(
                    `<strong>${feature.properties.khasra_no}</strong><br/>${feature.properties.village}${isSim ? '<br/><span style="color:#22c55e;font-weight:bold">⚡ Simulation Active</span>' : ''}`,
                    { direction: "top", opacity: 0.9 }
                  );
                  layer.on({
                    click: () => handleParcelClick(feature.properties.khasra_no)
                  });
                }}
              />
              <MapController selectedPlot={selectedPlot} geoData={geoData} />
            </MapContainer>
          )}
        </div>

        {/* Right Side: Analytical & Prescriptive Drawer */}
        <div className="w-1/3 h-full overflow-y-auto p-5 bg-white rounded-xl shadow-md border border-slate-200 space-y-4">
          {!selectedPlot ? (
            <div className="h-full flex flex-col items-center justify-center text-center text-slate-400">
              <Layers size={48} className="mb-2 text-slate-300" />
              <p className="font-medium">Select any Land Parcel (Khasra) on the map</p>
              <p className="text-xs">Click a polygon or search above to inspect statutory timelines</p>
            </div>
          ) : loadingDetails ? (
            <p className="text-sm text-slate-500">Evaluating statutory compliance & running SHAP models...</p>
          ) : plotDetails && (
            <>
              {/* Parcel Header */}
              <div className="border-b border-slate-200 pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">{plotDetails.plot_info.khasra_no}</h2>
                    <p className="text-xs text-slate-500">Village: {plotDetails.plot_info.village} | {plotDetails.plot_info.project}</p>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded font-semibold ${
                    simResult ? "bg-emerald-100 text-emerald-800 border border-emerald-300" :
                    isPlotLapsed ? "bg-red-100 text-red-700 border border-red-300 animate-pulse font-bold" :
                    plotDetails.plot_info.risk_tier === "Critical" ? "bg-red-100 text-red-700 border border-red-300" :
                    plotDetails.plot_info.risk_tier === "High" ? "bg-amber-100 text-amber-700 border border-amber-300" : "bg-emerald-100 text-emerald-700"
                  }`}>
                    {simResult ? "Simulated Tier" : isPlotLapsed ? "Statutorily Lapsed" : `${plotDetails.plot_info.risk_tier} Risk`}
                  </span>
                </div>
              </div>

              {/* Dynamic RFCTLARR Statutory Timeline & Pipeline Monitor */}
              <StatutoryTimelineModule plotInfo={plotDetails.plot_info} />

              {/* Predicted Delay Card with Legal Guardrail Override */}
              {isPlotLapsed ? (
                <div className="bg-red-950 text-white p-3.5 rounded-lg border border-red-700 space-y-1 shadow-inner">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-red-400 text-xs font-bold uppercase tracking-wider">
                      <AlertOctagon size={15} /> Statutory Proceeding Abated
                    </span>
                    <span className="text-[10px] bg-red-900/80 text-red-200 px-2 py-0.5 rounded font-mono font-bold">
                      Sec 19(7) VOID
                    </span>
                  </div>
                  <p className="text-lg font-bold text-red-100 tracking-wide">
                    ACQUISITION LEGALLY VOID
                  </p>
                  <p className="text-[11px] text-red-300 leading-tight">
                    Statutory 365-day threshold lapsed. Cannot calculate operational delay. Mandates fresh Section 11 Preliminary Notification.
                  </p>
                </div>
              ) : (
                <div className="bg-slate-900 text-white p-3 rounded-lg flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-400">
                      {simResult ? "Simulated Delay Projection" : "Predicted Lifecycle Delay"}
                    </p>
                    <p className={`text-2xl font-bold ${simResult ? "text-emerald-400" : "text-amber-400"}`}>
                      {simResult ? simResult.new_predicted_delay_days : plotDetails.predicted_delay_days} Days
                    </p>
                  </div>
                  <Clock className="text-slate-500" size={32} />
                </div>
              )}

              {/* Explainable AI (SHAP Breakdown) */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Key Delay Drivers (TreeSHAP)
                  </h3>
                  {isPlotLapsed && (
                    <span className="text-[10px] text-red-600 font-semibold bg-red-50 px-1.5 py-0.5 rounded border border-red-200">
                      Pre-Lapse Root Cause
                    </span>
                  )}
                </div>
                <div className="space-y-2">
                  {plotDetails.shap_breakdown.map((item, idx) => (
                    <div key={idx} className="text-xs bg-slate-50 p-2 rounded border border-slate-200">
                      <div className="flex justify-between font-medium mb-1">
                        <span className="text-slate-700 capitalize">{item.factor.replace(/_/g, " ")}</span>
                        <span className="text-red-600 font-bold">+{item.impact_days} days ({item.contribution_pct}%)</span>
                      </div>
                      <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-red-500 h-full" style={{ width: `${item.contribution_pct}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Prescriptive Recommendation Card + Dynamic GenAI Ground Plan */}
              <div className="p-3 bg-amber-50 border border-amber-300 rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-amber-900 font-bold text-xs uppercase">
                    <CheckCircle2 size={16} className="text-amber-600" /> Prescriptive Administrative Action
                  </span>
                  <span className="flex items-center gap-1 bg-amber-200/80 text-amber-900 text-[10px] font-bold px-2 py-0.5 rounded-full border border-amber-300">
                    <Sparkles size={11} className="text-amber-700" /> GenAI Ground Plan
                  </span>
                </div>

                <p className="text-xs font-bold text-slate-900">
                  {isPlotLapsed ? "Initiate Emergency Re-Notification under Section 11(1)" : plotDetails.prescriptive_recommendation.action_title}
                </p>
                
                {plotDetails.ai_mitigation_steps && plotDetails.ai_mitigation_steps.length > 0 ? (
                  <div className="space-y-1.5 pt-1">
                    {plotDetails.ai_mitigation_steps.map((step, idx) => (
                      <div key={idx} className="text-[11px] text-slate-700 flex items-start gap-1.5 bg-white/90 p-2 rounded border border-amber-200 shadow-xs">
                        <span className="font-bold text-amber-700 min-w-[14px]">{idx + 1}.</span>
                        <span className="leading-tight">{step}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                    {plotDetails.prescriptive_recommendation.description}
                  </p>
                )}

                <div className="text-[11px] text-amber-900 font-medium pt-1">
                  Assigned To: <span className="font-bold">{plotDetails.prescriptive_recommendation.recommended_officer}</span>
                </div>

                <button
                  onClick={() => setShowNoticeModal(true)}
                  className="mt-2 w-full flex items-center justify-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold py-2 px-3 rounded shadow-sm transition-colors"
                >
                  <FileText size={14} /> Generate Statutory Order / Notice Draft
                </button>
              </div>

              {/* What-If Counterfactual Simulator */}
              <div className="p-3 bg-slate-50 border border-slate-300 rounded-lg space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-slate-800 font-bold text-xs">
                    <Sliders size={16} className="text-slate-600" /> "What-If" Mitigation Simulator
                  </div>
                  {simResult && (
                    <button
                      onClick={resetSimulation}
                      className="text-[10px] text-slate-500 hover:text-slate-800 flex items-center gap-1 underline"
                    >
                      <RotateCcw size={11} /> Reset
                    </button>
                  )}
                </div>

                {isPlotLapsed ? (
                  <div className="p-2.5 bg-red-100/70 border border-red-200 rounded text-[11px] text-red-800">
                    <strong>Simulation Disabled:</strong> This parcel has exceeded Section 19 statutory timeframes. Standard administrative interventions cannot reverse legal lapsing without re-notification.
                  </div>
                ) : (
                  <>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span>Disbursement Target:</span>
                        <span className="font-bold">{simDisbursement}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={simDisbursement}
                        onChange={(e) => setSimDisbursement(e.target.value)}
                        className="w-full cursor-pointer"
                      />
                    </div>

                    <div className="space-y-1 text-xs">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={!resolveKhata}
                          onChange={(e) => setResolveKhata(!e.target.checked)}
                        />
                        Resolve Succession / Title Dispute
                      </label>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={resolveForest}
                          onChange={(e) => setResolveForest(e.target.checked)}
                        />
                        Expedite Stage-II Forest Clearance
                      </label>
                    </div>

                    <button
                      onClick={runSimulation}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-2 rounded transition-colors"
                    >
                      Simulate Intervention
                    </button>

                    {simResult && (
                      <div className="mt-2 p-2.5 bg-emerald-50 border border-emerald-300 rounded text-xs space-y-1">
                        <div className="flex items-center justify-between font-bold text-emerald-800">
                          <span>New Delay: {simResult.new_predicted_delay_days} Days</span>
                          <span className="text-emerald-700 flex items-center">
                            <TrendingDown size={14} className="mr-0.5" /> Saved: {simResult.days_saved} Days
                          </span>
                        </div>
                        <p className="text-[11px] text-emerald-700 font-medium">
                          ✓ Map parcel recolored to indicate reduced risk status.
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Official Government Notice / Memo Modal */}
      {showNoticeModal && plotDetails && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[2000] flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full border border-slate-300 overflow-hidden flex flex-col max-h-[90vh]">
            <div className="bg-slate-900 text-white px-6 py-3 flex justify-between items-center">
              <span className="text-xs uppercase tracking-wider font-semibold text-amber-400 flex items-center gap-1.5">
                <FileText size={16} /> Automated Administrative Order Draft
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.print()}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-2.5 py-1 rounded flex items-center gap-1 border border-slate-700"
                >
                  <Printer size={13} /> Print Memo
                </button>
                <button
                  onClick={() => setShowNoticeModal(false)}
                  className="text-slate-400 hover:text-white"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="p-8 overflow-y-auto space-y-4 text-slate-800 font-serif text-sm leading-relaxed">
              <div className="text-center border-b border-slate-300 pb-3">
                <h3 className="font-bold text-base tracking-wide uppercase">Office of the Competent Authority for Land Acquisition (CALA)</h3>
                <p className="text-xs font-sans text-slate-500">Government of Haryana / Revenue & Disaster Management Department</p>
                <p className="text-[11px] font-sans text-slate-400 mt-0.5">Under Right to Fair Compensation and Transparency in Land Acquisition (RFCTLARR) Act, 2013</p>
              </div>

              <div className="flex justify-between font-sans text-xs pt-1">
                <span><strong>Order Ref:</strong> CALA/REV/{plotDetails.plot_info.khasra_no.replace('/', '-')}/2026</span>
                <span><strong>Date:</strong> {new Date().toLocaleDateString('en-GB')}</span>
              </div>

              <div className="font-sans text-xs bg-slate-50 p-2.5 rounded border border-slate-200">
                <p><strong>To:</strong> {plotDetails.prescriptive_recommendation.recommended_officer}</p>
                <p><strong>Subject:</strong> Immediate statutory direction regarding Khasra No. <strong>{plotDetails.plot_info.khasra_no}</strong>, Village {plotDetails.plot_info.village} ({plotDetails.plot_info.project}).</p>
              </div>

              <p>
                Whereas, land acquisition proceedings are actively underway for the National Corridor Project under the RFCTLARR Act, 2013. The statutory monitoring engine has flagged parcel <strong>{plotDetails.plot_info.khasra_no}</strong> as critical, having only <strong>{plotDetails.plot_info.statutory_days_left} days</strong> remaining prior to statutory lapsing.
              </p>

              <div className="bg-amber-50/70 border-l-4 border-amber-500 p-3 font-sans text-xs space-y-1.5">
                <p className="font-bold text-amber-900 mb-0.5">Mandated Administrative Directives:</p>
                {plotDetails.ai_mitigation_steps && plotDetails.ai_mitigation_steps.length > 0 ? (
                  plotDetails.ai_mitigation_steps.map((step, idx) => (
                    <p key={idx} className="text-slate-800 leading-snug">
                      <strong>{idx + 1}.</strong> {step}
                    </p>
                  ))
                ) : (
                  <p className="text-slate-700">{plotDetails.prescriptive_recommendation.description}</p>
                )}
              </div>

              <p>
                You are hereby directed to execute <strong>{plotDetails.prescriptive_recommendation.action_title}</strong> within 7 working days from the issuance of this order. Failure to comply may result in statutory lapsing under Section 19(7) / 25 of the Act, causing substantial public exchequer loss.
              </p>

              <div className="pt-6 flex justify-between items-end font-sans text-xs">
                <div>
                  <p className="text-[11px] text-slate-400">Generated automatically by</p>
                  <p className="font-semibold text-slate-700">PRAGATI-Land DSS Engine</p>
                </div>
                <div className="text-right">
                  <div className="h-10 border-b border-dotted border-slate-400 w-40 ml-auto mb-1"></div>
                  <p className="font-bold text-slate-800">Competent Authority / DM</p>
                  <p className="text-[11px] text-slate-500">Seal & Signature</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}