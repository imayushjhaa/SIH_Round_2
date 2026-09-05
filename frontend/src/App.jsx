import React, { useState, useEffect } from "react";
import axios from "axios";
import { MapContainer, TileLayer, GeoJSON, useMap, ZoomControl } from "react-leaflet";
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
  AlertOctagon,
  Download,
  Sun,
  Moon
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
      map.flyToBounds(bounds, { padding: [50, 50], maxZoom: 18, duration: 1.2 });
    }
  }, [selectedPlot, geoData, map]);

  return null;
}

// Sub-component: RFCTLARR Statutory Pipeline & Timeline Monitor
function StatutoryTimelineModule({ plotInfo, darkMode }) {
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
    <div className={`p-3 rounded-lg border space-y-2.5 ${
      darkMode ? "bg-slate-800/80 border-slate-700" : "bg-slate-50 border-slate-200"
    }`}>
      <div className="flex justify-between items-center">
        <span className={`text-[11px] font-bold tracking-wide uppercase flex items-center gap-1.5 ${
          darkMode ? "text-slate-200" : "text-slate-700"
        }`}>
          <Scale size={13} className="text-amber-500" /> RFCTLARR Statutory Pipeline
        </span>
        <span className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
          darkMode ? "bg-slate-700 text-slate-300" : "bg-slate-200 text-slate-700"
        }`}>
          Stage {activeIndex + 1} of 5
        </span>
      </div>

      {/* 5-Stage Stepper Track */}
      <div className="relative flex items-center justify-between pt-0.5 pb-0.5">
        <div className={`absolute top-[12px] left-3 right-3 h-0.5 z-0 ${
          darkMode ? "bg-slate-700" : "bg-slate-200"
        }`}></div>
        <div 
          className="absolute top-[12px] left-3 h-0.5 bg-emerald-500 z-0 transition-all duration-500"
          style={{ width: `${(activeIndex / (STATUTORY_STAGES.length - 1)) * 90}%` }}
        ></div>

        {STATUTORY_STAGES.map((stg, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div key={stg.id} className="relative z-10 flex flex-col items-center">
              <div 
                className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold transition-all ${
                  isDone 
                    ? "bg-emerald-500 text-white shadow-xs" 
                    : isCurrent 
                    ? isLapsed
                      ? "bg-red-600 text-white ring-4 ring-red-500/30 animate-pulse"
                      : "bg-blue-600 text-white ring-4 ring-blue-500/30 shadow-sm" 
                    : darkMode 
                    ? "bg-slate-800 text-slate-500 border border-slate-600" 
                    : "bg-white text-slate-400 border-2 border-slate-300"
                }`}
              >
                {isDone ? <Check size={11} strokeWidth={3} /> : idx + 1}
              </div>
              <span 
                className={`text-[9px] mt-1 font-semibold whitespace-nowrap ${
                  isCurrent 
                    ? isLapsed ? "text-red-500 font-bold" : "text-blue-400 font-bold" 
                    : isDone 
                    ? "text-emerald-500" 
                    : darkMode ? "text-slate-500" : "text-slate-400"
                }`}
              >
                {stg.label}
              </span>
              <span className={`text-[8px] scale-90 -mt-0.5 ${
                darkMode ? "text-slate-500" : "text-slate-400"
              }`}>{stg.window}</span>
            </div>
          );
        })}
      </div>

      {/* Statutory Timeline Details & Expiry Card */}
      <div className={`p-2 rounded border text-xs space-y-1 ${
        isLapsed 
          ? darkMode ? "bg-red-950/40 border-red-800/80 text-red-200" : "bg-red-50/80 border-red-300 text-red-900"
          : isCritical 
          ? darkMode ? "bg-amber-950/40 border-amber-800/80 text-amber-200" : "bg-amber-50/80 border-amber-300 text-amber-900"
          : darkMode ? "bg-slate-900/90 border-slate-700 text-slate-300" : "bg-white border-slate-200 text-slate-700"
      }`}>
        <div className="flex items-center justify-between font-medium text-[11px]">
          <span className="flex items-center gap-1">
            <Calendar size={11} className={darkMode ? "text-slate-400" : "text-slate-500"} /> Sec 11 Notification:
          </span>
          <span className={`font-semibold ${darkMode ? "text-slate-100" : "text-slate-900"}`}>{formatLegalDate(plotInfo.sec_11_date)}</span>
        </div>

        <div className="flex items-center justify-between font-medium text-[11px]">
          <span className="flex items-center gap-1">
            <Clock size={11} className={darkMode ? "text-slate-400" : "text-slate-500"} /> Sec 19 Deadline:
          </span>
          <span className={`font-semibold ${darkMode ? "text-slate-100" : "text-slate-900"}`}>{deadline}</span>
        </div>

        <div className={`pt-1 border-t flex items-center justify-between font-bold text-[11px] ${
          darkMode ? "border-slate-700" : "border-slate-200/60"
        }`}>
          <span>Statutory Status:</span>
          {isLapsed ? (
            <span className="text-red-400 flex items-center gap-1">
              <ShieldAlert size={11} /> LAPSED under Sec 19(7) ({Math.abs(plotInfo.statutory_days_left)}d Overdue)
            </span>
          ) : isCritical ? (
            <span className="text-amber-400 flex items-center gap-1">
              <AlertTriangle size={11} /> Expiration Imminent ({plotInfo.statutory_days_left}d Left)
            </span>
          ) : (
            <span className="text-emerald-400">
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

  // Night Mode State
  const [darkMode, setDarkMode] = useState(true);

  // Search & Filter State ("ALL", "LAPSE", "HIGH_RISK", "SAFE")
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

  // Executive CSV Dossier Generator
  const exportLapsingDossierCSV = () => {
    if (!geoData?.features) return;

    const criticalParcels = geoData.features.filter((f) => {
      const p = f.properties;
      return (
        p.statutory_days_left < 45 ||
        p.risk_tier === "Critical" ||
        p.risk_tier === "High" ||
        p.status_color === "red"
      );
    });

    const headers = [
      "Khasra No",
      "Village",
      "Corridor Project",
      "Current Statutory Stage",
      "Statutory Days Left",
      "Legal Compliance Status",
      "Risk Tier",
      "Disbursement Pct",
      "Mandated Action Rule"
    ];

    const rows = criticalParcels.map((f) => {
      const p = f.properties;
      const isLapsed = p.statutory_days_left < 0;
      const legalStatus = isLapsed 
        ? `LAPSED (${Math.abs(p.statutory_days_left)}d Overdue)` 
        : p.statutory_days_left < 45 
        ? `CRITICAL (${p.statutory_days_left}d Left)` 
        : "High Risk Monitored";

      const mandatedAction = isLapsed
        ? "Re-issue Section 11 Notification"
        : p.statutory_days_left < 45
        ? "Emergency Section 19 Gazette Publication"
        : "Expedite Hearing & Disbursement";

      return [
        `"${p.khasra_no}"`,
        `"${p.village || 'N/A'}"`,
        `"${p.project || 'N/A'}"`,
        `"${p.stage || 'N/A'}"`,
        p.statutory_days_left,
        `"${legalStatus}"`,
        `"${p.risk_tier}"`,
        `"${p.disbursement_pct}%"`,
        `"${mandatedAction}"`
      ];
    });

    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" 
      + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `PRAGATI_Land_Lapsing_Dossier_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
    
    const isStatutoryCritical = props.statutory_days_left < 45 && props.stage !== "Possession Taken";
    let effectiveColor = isStatutoryCritical ? "red" : props.status_color;

    // Filter Logic
    let matchesFilter = true;
    if (activeFilter === "LAPSE") {
      matchesFilter = isStatutoryCritical;
    } else if (activeFilter === "HIGH_RISK") {
      matchesFilter = props.risk_tier === "Critical" || props.risk_tier === "High" || effectiveColor === "red";
    } else if (activeFilter === "SAFE") {
      matchesFilter = effectiveColor === "green";
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      matchesFilter = matchesFilter && (
        props.khasra_no.toLowerCase().includes(q) || 
        (props.village && props.village.toLowerCase().includes(q))
      );
    }

    const isSimulatedPlot = simResult && simResult.khasra_no === props.khasra_no;
    if (isSimulatedPlot) {
      if (simResult.new_predicted_delay_days < 45) {
        effectiveColor = "green";
      } else if (simResult.new_predicted_delay_days < 90) {
        effectiveColor = "yellow";
      }
    }

    let fill = effectiveColor === "red" ? "#ef4444" : effectiveColor === "yellow" ? "#eab308" : "#22c55e";
    let fillOp = matchesFilter ? (isSelected ? 0.85 : 0.5) : 0.08;

    if (isStatutoryCritical && !isSimulatedPlot) {
      fill = "url(#statutory-lapse-stripes)";
      fillOp = matchesFilter ? (isSelected ? 1 : 0.95) : 0.15;
    }

    return {
      fillColor: fill,
      weight: isSelected ? 3.5 : isStatutoryCritical ? 2.5 : 1.5,
      opacity: matchesFilter ? 0.95 : 0.2,
      color: isSelected ? "#38bdf8" : isStatutoryCritical ? "#ef4444" : isSimulatedPlot ? "#22c55e" : "#ffffff",
      dashArray: isSelected ? "" : isStatutoryCritical ? "4, 2" : "3",
      fillOpacity: fillOp
    };
  };

  const isPlotLapsed = plotDetails && plotDetails.plot_info.statutory_days_left < 0;

  // Safe Parcels dynamic count
  const safeCount = geoData?.features
    ? geoData.features.filter(f => {
        const p = f.properties;
        const isCritical = p.statutory_days_left < 45 && p.stage !== "Possession Taken";
        return !isCritical && p.status_color === "green";
      }).length
    : (summary?.safe_parcels ?? 6);

  return (
    <div className={`flex flex-col h-screen font-sans transition-colors duration-300 ${
      darkMode ? "bg-slate-950 text-slate-100" : "bg-slate-100 text-slate-800"
    }`}>
      
      {/* Hidden Global SVG Defs for Canvas Fill Patterns */}
      <svg className="absolute w-0 h-0 pointer-events-none" aria-hidden="true">
        <defs>
          <pattern
            id="statutory-lapse-stripes"
            width="12"
            height="12"
            patternTransform="rotate(45 0 0)"
            patternUnits="userSpaceOnUse"
          >
            <rect width="12" height="12" fill="#ef4444" fillOpacity="0.45" />
            <line x1="0" y1="0" x2="0" y2="12" stroke="#dc2626" strokeWidth="2.8" />
          </pattern>
        </defs>
      </svg>

      {/* Global CSS for Leaflet & Removing Browser SVG Focus Borders */}
      <style>{`
        /* Remove browser default rectangular outline on clicked SVG polygons */
        path.leaflet-interactive:focus,
        path.leaflet-interactive:focus-visible,
        .leaflet-container path:focus,
        svg:focus,
        svg *:focus {
          outline: none !important;
        }

        .leaflet-top.leaflet-left .leaflet-control-zoom {
          display: none !important;
        }
        .leaflet-bottom.leaflet-right .leaflet-control-zoom {
          margin-bottom: 14px !important;
          margin-right: 14px !important;
          border-radius: 8px !important;
          overflow: hidden !important;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
          border: 1px solid #334155 !important;
        }
        .leaflet-control-zoom a {
          background-color: rgba(15, 23, 42, 0.95) !important;
          color: #f8fafc !important;
          border-bottom: 1px solid #334155 !important;
          width: 30px !important;
          height: 30px !important;
          line-height: 30px !important;
          font-weight: bold !important;
        }
        .leaflet-control-zoom a:hover {
          background-color: #1e293b !important;
          color: #38bdf8 !important;
        }
      `}</style>

      {/* Compact Top Header */}
      <header className="bg-slate-900 text-white px-5 py-2.5 flex justify-between items-center shadow-md border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-amber-400/10 border border-amber-400/20 rounded-lg">
            <Scale className="text-amber-400" size={20} />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-wide flex items-center gap-2 text-slate-100">
              PRAGATI-Land <span className="text-slate-500 font-normal">|</span> <span className="text-xs font-medium text-slate-300">Statutory Compliance & Delay Mitigation Engine</span>
            </h1>
            <p className="text-[10px] text-slate-400">
              RFCTLARR Act 2013 Statutory Timeline Monitor & Decision Support System
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2.5">
          <button
            onClick={exportLapsingDossierCSV}
            className="flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-bold px-3 py-1.5 rounded-lg shadow-sm transition-all cursor-pointer"
            title="Download CSV report of all lapsed and critical parcels"
          >
            <Download size={13} /> Export Lapsing Dossier
          </button>

          {/* Night Mode / Theme Toggle Button */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`p-1.5 rounded-lg border transition-all cursor-pointer flex items-center gap-1.5 text-xs font-semibold ${
              darkMode 
                ? "bg-slate-800 border-slate-700 text-amber-300 hover:bg-slate-750" 
                : "bg-slate-800 border-slate-700 text-slate-300 hover:text-white"
            }`}
            title={darkMode ? "Switch to Light Theme" : "Switch to Dark Mode"}
          >
            {darkMode ? <Sun size={14} className="text-amber-400" /> : <Moon size={14} />}
            <span className="hidden sm:inline">{darkMode ? "Day" : "Night"}</span>
          </button>

          <div className="text-[11px] bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700 text-amber-300 font-medium">
            Active: {summary?.active_corridor || "Loading..."}
          </div>
        </div>
      </header>

      {/* 5-Column Executive KPI Strip */}
      <div className={`grid grid-cols-5 gap-2.5 px-5 py-2 border-b transition-colors ${
        darkMode ? "bg-slate-900 border-slate-800" : "bg-white border-slate-200"
      }`}>
        
        {/* Metric 1: Total Parcels */}
        <div 
          onClick={() => setActiveFilter("ALL")}
          title="Click to view all corridor parcels"
          className={`flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer select-none transition-all ${
            activeFilter === "ALL" 
              ? darkMode 
                ? "bg-slate-800 border-2 border-slate-500 shadow-md ring-2 ring-slate-600/40 scale-[1.01]" 
                : "bg-slate-100 border-2 border-slate-600 shadow-sm ring-2 ring-slate-400/20 scale-[1.01]"
              : darkMode 
              ? "bg-slate-800/60 border border-slate-750 hover:bg-slate-800 hover:border-slate-700" 
              : "bg-slate-50 border border-slate-200 hover:bg-slate-100/70 hover:border-slate-300"
          }`}
        >
          <div>
            <div className="flex items-center gap-1">
              <p className={`text-[10px] font-bold uppercase tracking-wider ${
                darkMode ? "text-slate-300" : "text-slate-600"
              }`}>Total Parcels</p>
              {activeFilter === "ALL" && (
                <span className="text-[8px] bg-slate-700 text-amber-300 px-1 py-0.2 rounded font-bold uppercase">Active</span>
              )}
            </div>
            <p className="text-[10px] text-slate-400">All corridor plots</p>
          </div>
          <p className={`text-lg font-extrabold ${darkMode ? "text-white" : "text-slate-800"}`}>{summary?.total_parcels ?? "--"}</p>
        </div>

        {/* Metric 2: Section 19 Lapse Alert */}
        <div 
          onClick={() => setActiveFilter(activeFilter === "LAPSE" ? "ALL" : "LAPSE")}
          title="Click to isolate statutory critical and lapsed parcels (<45d)"
          className={`flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer select-none transition-all ${
            activeFilter === "LAPSE" 
              ? darkMode
                ? "bg-red-950/70 border-2 border-red-500 shadow-md ring-2 ring-red-500/40 scale-[1.01]"
                : "bg-red-100/90 border-2 border-red-600 shadow-md ring-2 ring-red-500/30 scale-[1.01]" 
              : darkMode
              ? "bg-red-950/30 border border-red-900/60 hover:bg-red-950/50"
              : "bg-red-50/70 border border-red-200 hover:bg-red-100/60 hover:border-red-300"
          }`}
        >
          <div>
            <div className="flex items-center gap-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-red-500 flex items-center gap-1">
                <AlertTriangle size={11} className="text-red-500" /> Sec 19 Lapse
              </p>
              <span className={`text-[8px] px-1 py-0.2 rounded font-bold uppercase ${
                activeFilter === "LAPSE" ? "bg-red-600 text-white animate-pulse" : "bg-red-200 text-red-800"
              }`}>
                {activeFilter === "LAPSE" ? "Active" : "<45d"}
              </span>
            </div>
            <p className="text-[10px] text-red-400/90">Click to filter critical</p>
          </div>
          <p className="text-lg font-extrabold text-red-500">{summary?.critical_lapsing_parcels ?? "--"}</p>
        </div>

        {/* Metric 3: High Delay Risk */}
        <div 
          onClick={() => setActiveFilter(activeFilter === "HIGH_RISK" ? "ALL" : "HIGH_RISK")}
          title="Click to filter all operational delay parcels (>90 days)"
          className={`flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer select-none transition-all ${
            activeFilter === "HIGH_RISK" 
              ? darkMode
                ? "bg-amber-950/70 border-2 border-amber-500 shadow-md ring-2 ring-amber-500/40 scale-[1.01]"
                : "bg-amber-100/90 border-2 border-amber-600 shadow-md ring-2 ring-amber-500/30 scale-[1.01]" 
              : darkMode
              ? "bg-amber-950/30 border border-amber-900/60 hover:bg-amber-950/50"
              : "bg-amber-50/70 border border-amber-200 hover:bg-amber-100/60 hover:border-amber-300"
          }`}
        >
          <div>
            <div className="flex items-center gap-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-amber-500">High Delay Risk</p>
              {activeFilter === "HIGH_RISK" && (
                <span className="text-[8px] bg-amber-600 text-white px-1 py-0.2 rounded font-bold uppercase">Active</span>
              )}
            </div>
            <p className="text-[10px] text-amber-400/90">&gt;90d delay plots</p>
          </div>
          <p className="text-lg font-extrabold text-amber-500">{summary?.high_risk_parcels ?? "--"}</p>
        </div>

        {/* Metric 4: Safe / Cleared Parcels */}
        <div 
          onClick={() => setActiveFilter(activeFilter === "SAFE" ? "ALL" : "SAFE")}
          title="Click to isolate safe parcels on track without active dispute"
          className={`flex items-center justify-between px-3 py-1.5 rounded-lg cursor-pointer select-none transition-all ${
            activeFilter === "SAFE" 
              ? darkMode
                ? "bg-emerald-950/70 border-2 border-emerald-500 shadow-md ring-2 ring-emerald-500/40 scale-[1.01]"
                : "bg-emerald-100/90 border-2 border-emerald-600 shadow-md ring-2 ring-emerald-500/30 scale-[1.01]" 
              : darkMode
              ? "bg-emerald-950/30 border border-emerald-900/60 hover:bg-emerald-950/50"
              : "bg-emerald-50/70 border border-emerald-200 hover:bg-emerald-100/60 hover:border-emerald-300"
          }`}
        >
          <div>
            <div className="flex items-center gap-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-500 flex items-center gap-1">
                <CheckCircle2 size={11} className="text-emerald-500" /> Safe / Cleared
              </p>
              {activeFilter === "SAFE" && (
                <span className="text-[8px] bg-emerald-600 text-white px-1 py-0.2 rounded font-bold uppercase">Active</span>
              )}
            </div>
            <p className="text-[10px] text-emerald-400/90">On track, dispute-free</p>
          </div>
          <p className="text-lg font-extrabold text-emerald-500">{safeCount}</p>
        </div>

        {/* Metric 5: Avg Disbursement Velocity */}
        <div 
          title="RFCTLARR Sec 38 Mandate: Minimum 80% compensation required before physical possession"
          className={`flex items-center justify-between px-3 py-1.5 rounded-lg select-none ${
            darkMode ? "bg-slate-800/60 border border-slate-750" : "bg-slate-50 border border-slate-200"
          }`}
        >
          <div>
            <div className="flex items-center gap-1">
              <p className={`text-[10px] font-bold uppercase tracking-wider ${
                darkMode ? "text-slate-300" : "text-slate-700"
              }`}>Disbursement</p>
              <span className={`text-[8px] font-semibold px-1 py-0.2 rounded ${
                darkMode ? "bg-slate-700 text-slate-300" : "bg-slate-200 text-slate-700"
              }`}>Target: 80%</span>
            </div>
            <p className="text-[10px] text-slate-400">Award cleared</p>
          </div>
          <p className={`text-lg font-extrabold ${darkMode ? "text-slate-200" : "text-slate-800"}`}>{summary?.avg_disbursement_pct ?? "--"}%</p>
        </div>

      </div>

      {/* Main Workspace */}
      <div className="flex flex-1 overflow-hidden p-3 gap-3">
        {/* Left Side: Cadastral Satellite Map */}
        <div className={`w-2/3 h-full relative rounded-xl overflow-hidden shadow-md border ${
          darkMode ? "border-slate-800" : "border-slate-300"
        }`}>
          
          {/* Top-Left: Search Bar */}
          <div className="absolute top-3 left-3 z-[1000]">
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                placeholder="Search Khasra (e.g. KH-643)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-900/90 text-white text-xs px-3.5 py-2 pl-9 rounded-xl border border-slate-700 shadow-xl placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400 backdrop-blur-md w-56 transition-all"
              />
              <Search size={14} className="absolute left-3 top-2.5 text-slate-400" />
            </form>
          </div>

          {/* Bottom-Left: Map Legend */}
          <div className="absolute bottom-3 left-3 z-[1000] bg-slate-900/90 text-white px-3 py-1.5 rounded-lg shadow-xl border border-slate-700 text-xs flex items-center gap-3 backdrop-blur-md">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2.5 h-2.5 bg-emerald-500 rounded-xs inline-block"></span> Safe
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2.5 h-2.5 bg-amber-500 rounded-xs inline-block"></span> Under Review
            </span>
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2.5 h-2.5 bg-red-500 rounded-xs inline-block"></span> Dispute
            </span>
            <span className="flex items-center gap-1.5 font-medium" title="Section 19(7) Imminent (<45d) or Abated Lapsed Parcel">
              <span 
                className="w-3 h-3 rounded-xs border border-red-500 inline-block shadow-xs" 
                style={{
                  background: "repeating-linear-gradient(45deg, #dc2626, #dc2626 2px, rgba(239, 68, 68, 0.45) 2px, rgba(239, 68, 68, 0.45) 6px)"
                }}
              ></span> 
              <span className="text-red-300">Sec 19 Lapse</span>
            </span>
          </div>

          {geoData && (
            <MapContainer 
              key="satellite-map"
              center={[28.7475, 76.8305]}
              zoom={15} 
              maxZoom={19}
              zoomControl={false}
              scrollWheelZoom={true} 
              className="w-full h-full"
            >
              <ZoomControl position="bottomright" />
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
                  const isLapse = feature.properties.statutory_days_left < 45 && feature.properties.stage !== "Possession Taken";
                  layer.bindTooltip(
                    `<strong>${feature.properties.khasra_no}</strong><br/>${feature.properties.village}${isLapse ? '<br/><span style="color:#ef4444;font-weight:bold">⚠️ Sec 19 Statutory Risk</span>' : ''}${isSim ? '<br/><span style="color:#22c55e;font-weight:bold">⚡ Simulation Active</span>' : ''}`,
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
        <div className={`w-1/3 h-full overflow-y-auto p-4 rounded-xl shadow-md border space-y-3.5 transition-colors ${
          darkMode 
            ? "bg-slate-900 border-slate-800 text-slate-100" 
            : "bg-white border-slate-200 text-slate-800"
        }`}>
          {!selectedPlot ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <Layers size={44} className={`mb-2 ${darkMode ? "text-slate-700" : "text-slate-300"}`} />
              <p className={`font-medium text-sm ${darkMode ? "text-slate-300" : "text-slate-600"}`}>Select any Land Parcel (Khasra) on the map</p>
              <p className="text-xs text-slate-500">Click a polygon or search above to inspect statutory timelines</p>
            </div>
          ) : loadingDetails ? (
            <p className="text-xs text-slate-400">Evaluating statutory compliance & running SHAP models...</p>
          ) : plotDetails && (
            <>
              {/* Parcel Header */}
              <div className={`border-b pb-2.5 ${darkMode ? "border-slate-800" : "border-slate-200"}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className={`text-base font-bold ${darkMode ? "text-white" : "text-slate-900"}`}>{plotDetails.plot_info.khasra_no}</h2>
                    <p className="text-xs text-slate-400">Village: {plotDetails.plot_info.village} | {plotDetails.plot_info.project}</p>
                  </div>
                  <span className={`text-[11px] px-2 py-0.5 rounded font-semibold ${
                    simResult ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40" :
                    isPlotLapsed ? "bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse font-bold" :
                    plotDetails.plot_info.risk_tier === "Critical" ? "bg-red-500/20 text-red-400 border border-red-500/40" :
                    plotDetails.plot_info.risk_tier === "High" ? "bg-amber-500/20 text-amber-400 border border-amber-500/40" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                  }`}>
                    {simResult ? "Simulated Tier" : isPlotLapsed ? "Statutorily Lapsed" : `${plotDetails.plot_info.risk_tier} Risk`}
                  </span>
                </div>
              </div>

              {/* Dynamic RFCTLARR Statutory Timeline & Pipeline Monitor */}
              <StatutoryTimelineModule plotInfo={plotDetails.plot_info} darkMode={darkMode} />

              {/* Predicted Delay Card with Legal Guardrail Override */}
              {isPlotLapsed ? (
                <div className="bg-red-950 text-white p-3 rounded-lg border border-red-700 space-y-1 shadow-inner">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-red-400 text-xs font-bold uppercase tracking-wider">
                      <AlertOctagon size={14} /> Statutory Proceeding Abated
                    </span>
                    <span className="text-[10px] bg-red-900/80 text-red-200 px-2 py-0.5 rounded font-mono font-bold">
                      Sec 19(7) VOID
                    </span>
                  </div>
                  <p className="text-base font-bold text-red-100 tracking-wide">
                    ACQUISITION LEGALLY VOID
                  </p>
                  <p className="text-[11px] text-red-300 leading-tight">
                    Statutory 365-day threshold lapsed. Operational delay calculation suspended. Mandates fresh Section 11 Preliminary Notification.
                  </p>
                </div>
              ) : (
                <div className="bg-slate-950/80 border border-slate-800 text-white p-2.5 rounded-lg flex items-center justify-between">
                  <div>
                    <p className="text-[11px] text-slate-400">
                      {simResult ? "Simulated Delay Projection" : "Predicted Lifecycle Delay"}
                    </p>
                    <p className={`text-xl font-bold ${simResult ? "text-emerald-400" : "text-amber-400"}`}>
                      {simResult ? simResult.new_predicted_delay_days : plotDetails.predicted_delay_days} Days
                    </p>
                  </div>
                  <Clock className="text-slate-600" size={28} />
                </div>
              )}

              {/* Explainable AI (SHAP Breakdown) */}
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <h3 className={`text-[11px] font-bold uppercase tracking-wider ${
                    darkMode ? "text-slate-300" : "text-slate-700"
                  }`}>
                    Key Delay Drivers (TreeSHAP)
                  </h3>
                  {isPlotLapsed && (
                    <span className="text-[9px] text-red-400 font-semibold bg-red-950/50 px-1.5 py-0.2 rounded border border-red-900">
                      Pre-Lapse Root Cause
                    </span>
                  )}
                </div>
                <div className="space-y-1.5">
                  {plotDetails.shap_breakdown.map((item, idx) => (
                    <div key={idx} className={`text-xs p-2 rounded border ${
                      darkMode ? "bg-slate-850 border-slate-800 text-slate-200" : "bg-slate-50 border-slate-200 text-slate-700"
                    }`}>
                      <div className="flex justify-between font-medium mb-1">
                        <span className="capitalize text-[11px]">{item.factor.replace(/_/g, " ")}</span>
                        <span className="text-red-500 font-bold text-[11px]">+{item.impact_days}d ({item.contribution_pct}%)</span>
                      </div>
                      <div className={`w-full h-1.5 rounded-full overflow-hidden ${darkMode ? "bg-slate-800" : "bg-slate-200"}`}>
                        <div className="bg-red-500 h-full" style={{ width: `${item.contribution_pct}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Prescriptive Recommendation Card + Dynamic GenAI Ground Plan */}
              <div className={`p-3 rounded-lg space-y-1.5 border ${
                darkMode ? "bg-amber-950/20 border-amber-900/60 text-amber-200" : "bg-amber-50 border-amber-300 text-amber-900"
              }`}>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 font-bold text-[11px] uppercase">
                    <CheckCircle2 size={14} className="text-amber-500" /> Prescriptive Administrative Action
                  </span>
                  <span className={`flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.2 rounded-full border ${
                    darkMode ? "bg-amber-900/40 border-amber-700 text-amber-300" : "bg-amber-200/80 border-amber-300 text-amber-900"
                  }`}>
                    <Sparkles size={10} className="text-amber-500" /> GenAI Ground Plan
                  </span>
                </div>

                <p className={`text-xs font-bold leading-snug ${darkMode ? "text-slate-100" : "text-slate-900"}`}>
                  {isPlotLapsed ? "Initiate Emergency Re-Notification under Section 11(1)" : plotDetails.prescriptive_recommendation.action_title}
                </p>
                
                {plotDetails.ai_mitigation_steps && plotDetails.ai_mitigation_steps.length > 0 ? (
                  <div className="space-y-1.5 pt-0.5">
                    {plotDetails.ai_mitigation_steps.map((step, idx) => (
                      <div key={idx} className={`text-[11px] flex items-start gap-1.5 p-2 rounded border shadow-xs ${
                        darkMode ? "bg-slate-800/80 border-slate-700 text-slate-200" : "bg-white/90 border-amber-200 text-slate-700"
                      }`}>
                        <span className="font-bold text-amber-500 min-w-[14px]">{idx + 1}.</span>
                        <span className="leading-tight">{step}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    {plotDetails.prescriptive_recommendation.description}
                  </p>
                )}

                <div className="text-[10px] font-medium pt-0.5 opacity-90">
                  Assigned To: <span className="font-bold">{plotDetails.prescriptive_recommendation.recommended_officer}</span>
                </div>

                <button
                  onClick={() => setShowNoticeModal(true)}
                  className="mt-1.5 w-full flex items-center justify-center gap-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold py-1.5 px-3 rounded shadow-sm transition-colors cursor-pointer"
                >
                  <FileText size={13} /> Generate Statutory Order / Notice Draft
                </button>
              </div>

              {/* What-If Counterfactual Simulator */}
              <div className={`p-3 rounded-lg space-y-2.5 border ${
                darkMode ? "bg-slate-800/80 border-slate-700" : "bg-slate-50 border-slate-300"
              }`}>
                <div className="flex items-center justify-between">
                  <div className={`flex items-center gap-1.5 font-bold text-xs ${darkMode ? "text-slate-200" : "text-slate-800"}`}>
                    <Sliders size={14} className={darkMode ? "text-slate-400" : "text-slate-600"} /> "What-If" Mitigation Simulator
                  </div>
                  {simResult && (
                    <button
                      onClick={resetSimulation}
                      className="text-[10px] text-slate-400 hover:text-slate-200 flex items-center gap-1 underline cursor-pointer"
                    >
                      <RotateCcw size={10} /> Reset
                    </button>
                  )}
                </div>

                {isPlotLapsed ? (
                  <div className={`p-2 rounded text-[11px] border ${
                    darkMode ? "bg-red-950/40 border-red-900 text-red-300" : "bg-red-100/70 border-red-200 text-red-800"
                  }`}>
                    <strong>Simulation Disabled:</strong> Exceeded Section 19 statutory timeframes. Standard interventions cannot reverse legal lapsing without re-notification.
                  </div>
                ) : (
                  <>
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span>Disbursement Target:</span>
                        <span className="font-bold">{simDisbursement}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={simDisbursement}
                        onChange={(e) => setSimDisbursement(e.target.value)}
                        className={`w-full cursor-pointer h-1.5 rounded-lg appearance-none ${
                          darkMode ? "bg-slate-700" : "bg-slate-200"
                        }`}
                      />
                    </div>

                    <div className="space-y-1 text-xs">
                      <label className="flex items-center gap-2 cursor-pointer text-[11px]">
                        <input
                          type="checkbox"
                          checked={!resolveKhata}
                          onChange={(e) => setResolveKhata(!e.target.checked)}
                        />
                        Resolve Succession / Title Dispute
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer text-[11px]">
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
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-1.5 rounded transition-colors cursor-pointer"
                    >
                      Simulate Intervention
                    </button>

                    {simResult && (
                      <div className={`mt-1.5 p-2 rounded text-xs space-y-0.5 border ${
                        darkMode ? "bg-emerald-950/40 border-emerald-900 text-emerald-300" : "bg-emerald-50 border-emerald-300 text-emerald-800"
                      }`}>
                        <div className="flex items-center justify-between font-bold text-[11px]">
                          <span>New Delay: {simResult.new_predicted_delay_days} Days</span>
                          <span className="text-emerald-500 flex items-center">
                            <TrendingDown size={13} className="mr-0.5" /> Saved: {simResult.days_saved}d
                          </span>
                        </div>
                        <p className="text-[10px] text-emerald-400 font-medium">
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

      {/* Official Government Notice / Memo Modal (Always White Paper Output for Print Clarity) */}
      {showNoticeModal && plotDetails && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-[2000] flex items-center justify-center p-4">
          <div className="bg-white text-slate-900 rounded-xl shadow-2xl max-w-2xl w-full border border-slate-300 overflow-hidden flex flex-col max-h-[90vh]">
            <div className="bg-slate-900 text-white px-6 py-3 flex justify-between items-center">
              <span className="text-xs uppercase tracking-wider font-semibold text-amber-400 flex items-center gap-1.5">
                <FileText size={16} /> Automated Administrative Order Draft
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.print()}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-2.5 py-1 rounded flex items-center gap-1 border border-slate-700 cursor-pointer"
                >
                  <Printer size={13} /> Print Memo
                </button>
                <button
                  onClick={() => setShowNoticeModal(false)}
                  className="text-slate-400 hover:text-white cursor-pointer"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="p-8 overflow-y-auto space-y-4 font-serif text-sm leading-relaxed">
              <div className="text-center border-b border-slate-300 pb-3">
                <h3 className="font-bold text-base tracking-wide uppercase text-slate-900">Office of the Competent Authority for Land Acquisition (CALA)</h3>
                <p className="text-xs font-sans text-slate-500">Government of Haryana / Revenue & Disaster Management Department</p>
                <p className="text-[11px] font-sans text-slate-400 mt-0.5">Under Right to Fair Compensation and Transparency in Land Acquisition (RFCTLARR) Act, 2013</p>
              </div>

              <div className="flex justify-between font-sans text-xs pt-1 text-slate-600">
                <span><strong>Order Ref:</strong> CALA/REV/{plotDetails.plot_info.khasra_no.replace('/', '-')}/2026</span>
                <span><strong>Date:</strong> {new Date().toLocaleDateString('en-GB')}</span>
              </div>

              <div className="font-sans text-xs bg-slate-50 p-2.5 rounded border border-slate-200 text-slate-800">
                <p><strong>To:</strong> {plotDetails.prescriptive_recommendation.recommended_officer}</p>
                <p><strong>Subject:</strong> Immediate statutory direction regarding Khasra No. <strong>{plotDetails.plot_info.khasra_no}</strong>, Village {plotDetails.plot_info.village} ({plotDetails.plot_info.project}).</p>
              </div>

              <p className="text-slate-800">
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

              <p className="text-slate-800">
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