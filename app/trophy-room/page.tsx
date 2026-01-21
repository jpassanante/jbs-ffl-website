"use client";

import Navigation from "@/components/Navigation";
import FantasyTrophy from "@/components/Trophy";

export default function TrophyRoom() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/trophy-room" />
      <FantasyTrophy />
    </div>
  );
}
