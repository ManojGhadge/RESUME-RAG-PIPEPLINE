import React from "react";
import { NavLink } from "react-router-dom";
import { useResume } from "../../context/ResumeContext.jsx";

const links = [
  { to: "/dashboard", label: "Dashboard", requiresResume: false },
  { to: "/chat", label: "Chat", requiresResume: true },
  { to: "/interview", label: "Interview", requiresResume: true },
  { to: "/ats", label: "ATS", requiresResume: true },
  { to: "/jd-match", label: "JD Match", requiresResume: true },
];

export default function Sidebar() {
  const { activeResumeId } = useResume();

  return (
    <aside className="w-64 bg-surface border-r border-gray-200/60 p-6 flex flex-col">
      <div className="mb-8">
        <h2 className="text-2xl font-display text-primary font-bold">RESUMEANA</h2>
        <p className="text-xs text-muted font-body mt-1">AI Resume & Interview Assistant</p>
      </div>
      <nav className="flex-1 space-y-1.5">
        {links.map((link) => {
          const isDisabled = link.requiresResume && !activeResumeId;
          if (isDisabled) {
            return (
              <div
                key={link.to}
                className="px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 cursor-not-allowed select-none flex items-center justify-between font-body bg-gray-50/50"
                title="Upload or select a resume first"
              >
                <span>{link.label}</span>
                <span className="text-[9px] uppercase tracking-wider bg-gray-100 text-gray-400 px-1.5 py-0.5 rounded font-semibold font-body">Locked</span>
              </div>
            );
          }
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `block px-3 py-2.5 rounded-lg text-sm font-medium transition-all font-body ${
                  isActive
                    ? "bg-primary text-white shadow-sm font-semibold"
                    : "text-ink hover:bg-primary-light hover:text-primary"
                }`
              }
            >
              {link.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
