"use client";

import { useState, useMemo } from "react";
import Navigation from "@/components/Navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { powerRankings } from "@/data/powerRankings";

// Get available seasons (sorted, newest first)
const getAvailableSeasons = () => {
  const seasons = Object.keys(powerRankings).map(Number).sort((a, b) => b - a);
  return seasons;
};

export default function PowerRankings() {
  const availableSeasons = getAvailableSeasons();
  const [selectedSeason, setSelectedSeason] = useState<number>(availableSeasons[0] || 2025);

  const seasonData = powerRankings[selectedSeason.toString() as keyof typeof powerRankings];

  // Prepare chart data: one data point per week with each manager's totalRank
  const chartData = useMemo(() => {
    if (!seasonData) return [];

    const managers = new Set<string>();
    seasonData.weeks.forEach((week) => {
      week.managers.forEach((m) => managers.add(m.manager));
    });

    return seasonData.weeks.map((week) => {
      const dataPoint: any = { week: week.week };
      week.managers.forEach((manager) => {
        dataPoint[manager.manager] = manager.totalRank;
      });
      return dataPoint;
    });
  }, [seasonData]);

  // Get final/latest rankings for summary table
  const finalRankings = useMemo(() => {
    if (!seasonData) return [];
    return seasonData.finalRankings || [];
  }, [seasonData]);

  // Manager colors for chart lines (JBS color scheme)
  const managerColors: Record<string, string> = {
    "Matt": "#1E4D9B",      // jbsBlue
    "Peter": "#FDB515",      // jbsGold
    "Ted": "#2563EB",        // Blue
    "Lanny": "#059669",       // Green
    "Ben": "#DC2626",         // Red
    "Joey": "#7C3AED",        // Purple
    "Tyler": "#EA580C",       // Orange
    "Vernon": "#0891B2",      // Cyan
    "Jason": "#BE185D",       // Pink
    "John": "#475569",        // Slate
  };

  if (!seasonData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
        <Navigation currentPage="/power-rankings" />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold text-jbsBlue mb-8 text-center">
            Power Rankings
          </h1>
          <p className="text-center text-gray-600">No data available for selected season.</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/power-rankings" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-jbsBlue mb-4 text-center">
            Power Rankings
          </h1>
          
          {/* Season Selector */}
          <div className="flex justify-center mb-6">
            <label htmlFor="season-select" className="mr-3 text-lg font-semibold text-gray-700">
              Season:
            </label>
            <select
              id="season-select"
              value={selectedSeason}
              onChange={(e) => setSelectedSeason(Number(e.target.value))}
              className="px-4 py-2 border-2 border-jbsBlue rounded-lg text-jbsBlue font-semibold bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-jbsGold"
            >
              {availableSeasons.map((season) => (
                <option key={season} value={season}>
                  {season}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Chart Section */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-jbsBlue mb-4">
            Traditional Power Rankings Over Time
          </h2>
          <p className="text-gray-600 mb-6 text-sm">
            Power rankings for each manager throughout the {selectedSeason} regular season. Higher total rank = better performance.
          </p>
          
          <div className="w-full" style={{ height: "500px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="week" 
                  label={{ value: "Week", position: "insideBottom", offset: -5 }}
                  stroke="#1E4D9B"
                />
                <YAxis 
                  label={{ value: "Total Power Rank", angle: -90, position: "insideLeft" }}
                  stroke="#1E4D9B"
                  domain={['dataMin - 2', 'dataMax + 2']}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '2px solid #1E4D9B',
                    borderRadius: '8px'
                  }}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="line"
                />
                {Object.keys(managerColors).map((manager) => {
                  // Only show line if manager has data in this season
                  if (chartData.length > 0 && chartData[0][manager] !== undefined) {
                    return (
                      <Line
                        key={manager}
                        type="monotone"
                        dataKey={manager}
                        stroke={managerColors[manager]}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                    );
                  }
                  return null;
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Summary Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 bg-gradient-to-r from-jbsBlue to-jbsGold">
            <h2 className="text-2xl font-bold text-white">
              Final Power Rankings - {selectedSeason}
            </h2>
            <p className="text-white/90 text-sm mt-1">
              Week {seasonData.finalWeek} Rankings
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Manager
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Record Rank
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Points Rank
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Breakdown Rank
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Rank
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {finalRankings.map((manager, index) => {
                  const rank = index + 1;
                  return (
                    <tr 
                      key={manager.manager}
                      className={`hover:bg-gray-50 ${
                        rank === 1 ? "bg-gradient-to-r from-jbsGold/10 to-jbsGold/5" : ""
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-lg font-bold ${
                          rank === 1 ? "text-jbsGold" : "text-gray-700"
                        }`}>
                          {rank === 1 && "👑 "}
                          {rank}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-semibold text-jbsBlue">
                          {manager.manager}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-sm text-gray-700">
                          {manager.recordRank.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-sm text-gray-700">
                          {manager.pointsRank.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className="text-sm text-gray-700">
                          {manager.breakdownRank.toFixed(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <span className={`text-lg font-bold ${
                          rank === 1 ? "text-jbsGold" : "text-jbsBlue"
                        }`}>
                          {manager.totalRank.toFixed(1)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
