"use client";

import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { championships } from '@/data/champions';

// Map first names to full names for trophy display
const nameMapping: Record<string, string> = {
  'Ted': 'Ted Schnuck',
  'Peter': 'Peter Lazaroff',
  'Lanny': 'Lanny Benson',
  'Ben': 'Benjamin Kline',
  'Vernon': 'Vernon Chaplin',
  'John': 'John Hubert',
  'Joey': 'Joseph Passanante',
  'Matt': 'Matt Mendelsohn',
  'Tyler': 'Tyler Barrie',
  'Jason': 'Jason Dupont',
  'Ty': 'Ty Fridrich',
};

// Map first names to full names for runner-up, reg season, most points
const getFullName = (firstName: string | null): string | null => {
  if (!firstName) return null;
  return nameMapping[firstName] || firstName;
};

interface ChampionData {
  year: number;
  name: string;
}

export default function FantasyTrophy() {
  const containerRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const zoomLevelRef = useRef<number>(26); // Initial zoom distance (reduced to bring trophy closer)
  
  // Convert championships data to Trophy component format
  const champions: ChampionData[] = championships.map((champ) => ({
    year: champ.year,
    name: getFullName(champ.champion) || champ.champion,
  })).reverse(); // Reverse to show newest first

  useEffect(() => {
    if (!containerRef.current) return;
    
    const w = containerRef.current.clientWidth;
    const h = 1000; // Reduced height to minimize whitespace above trophy
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, w / h, 0.1, 1000);
    camera.position.set(0, 5, zoomLevelRef.current); // Adjusted Y to better frame trophy in smaller container
    camera.lookAt(0, 4.8, 0); // Adjusted lookAt to center trophy in frame
    cameraRef.current = camera;
    
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setClearColor(0xffffff, 0); // Transparent background for light theme
    
    while (containerRef.current.firstChild) {
      containerRef.current.removeChild(containerRef.current.firstChild);
    }
    containerRef.current.appendChild(renderer.domElement);
    
    const ambient = new THREE.AmbientLight(0xffffff, 2.0);
    scene.add(ambient);
    
    const spot1 = new THREE.SpotLight(0xffffff, 4.0);
    spot1.position.set(5, 15, 10);
    spot1.angle = Math.PI / 4;
    spot1.penumbra = 0.3;
    scene.add(spot1);
    
    const spot2 = new THREE.SpotLight(0xffffff, 3.5);
    spot2.position.set(-5, 12, -8);
    spot2.angle = Math.PI / 4;
    spot2.penumbra = 0.3;
    scene.add(spot2);
    
    const front = new THREE.PointLight(0xffffff, 2.5);
    front.position.set(0, 4, 12);
    scene.add(front);
    
    // Add additional rim lights for more brightness
    const rimLight1 = new THREE.DirectionalLight(0xffffff, 2.0);
    rimLight1.position.set(10, 8, 5);
    scene.add(rimLight1);
    
    const rimLight2 = new THREE.DirectionalLight(0xffffff, 1.8);
    rimLight2.position.set(-10, 8, 5);
    scene.add(rimLight2);
    
    // Add top-down light for maximum brightness
    const topLight = new THREE.DirectionalLight(0xffffff, 1.5);
    topLight.position.set(0, 20, 0);
    scene.add(topLight);
    
    const trophy = new THREE.Group();
    
    // Materials - Vibrant Bright Gold theme with emissive glow
    const goldMat = new THREE.MeshStandardMaterial({ 
      color: 0xFFFF99, 
      metalness: 0.98, 
      roughness: 0.02,
      emissive: 0xFFD700,
      emissiveIntensity: 0.3
    });
    const goldMatCup = new THREE.MeshStandardMaterial({ 
      color: 0xFFFF99, 
      metalness: 0.98, 
      roughness: 0.01,
      emissive: 0xFFD700,
      emissiveIntensity: 0.4
    });
    const blueMat = new THREE.MeshStandardMaterial({ 
      color: 0x60A5FA, 
      metalness: 0.7, 
      roughness: 0.2,
      emissive: 0x3B82F6,
      emissiveIntensity: 0.2
    });
    const tierMat = new THREE.MeshStandardMaterial({ 
      color: 0xFFFF99, 
      metalness: 0.95, 
      roughness: 0.05,
      emissive: 0xFFD700,
      emissiveIntensity: 0.25
    });
    
    // Fixed plaque dimensions for consistent sizing
    const FIXED_PLATE_WIDTH = 1.5;
    const FIXED_PLATE_HEIGHT = 0.9;
    
    const createNameTexture = (year: number, name: string) => {
      // Canvas dimensions matching fixed plate aspect ratio (1.5:0.9 = 1.67:1)
      const canvas = document.createElement('canvas');
      canvas.width = 500;
      canvas.height = 300; // Aspect ratio matches fixed plate dimensions
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      
      // Pure white background for maximum brightness
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, 500, 300);
      
      ctx.strokeStyle = '#3B82F6';
      ctx.lineWidth = 6;
      ctx.strokeRect(8, 8, 484, 284);
      
      // Year - darker blue, bold
      ctx.fillStyle = '#1E4D9B'; // Darker blue for better contrast
      ctx.font = 'bold 64px Georgia';
      ctx.textAlign = 'center';
      ctx.fillText(year.toString(), 250, 100);
      
      // Last name - pure black, bold
      ctx.fillStyle = '#000000'; // Pure black for maximum contrast
      ctx.font = 'bold 48px Georgia';
      const lastName = name.split(' ').pop() || name;
      ctx.fillText(lastName.toUpperCase(), 250, 175);
      
      // First name - black, bold
      ctx.font = 'bold 32px Georgia'; // Made bold
      ctx.fillStyle = '#000000'; // Changed from gray to black
      const firstName = name.split(' ')[0];
      ctx.fillText(firstName, 250, 230);
      
      return new THREE.CanvasTexture(canvas);
    };
    
    const tiers = [
      { y: 0.5, width: 4.8, height: 1.1, plates: [0,1,2,3,4,5,6,7] },
      { y: 1.7, width: 4.0, height: 1.1, plates: [8,9,10,11,12,13,14,15] },
      { y: 2.9, width: 3.2, height: 1.1, plates: [16,17,18,19,20,21,22,23] },
      { y: 4.1, width: 2.4, height: 1.0, plates: [24,25,26] },
    ];
    
    tiers.forEach((tier) => {
      const baseGeo = new THREE.BoxGeometry(tier.width, tier.height, tier.width);
      const base = new THREE.Mesh(baseGeo, tierMat);
      base.position.y = tier.y;
      trophy.add(base);
      
      const trimGeo = new THREE.BoxGeometry(tier.width + 0.1, 0.06, tier.width + 0.1);
      const trim = new THREE.Mesh(trimGeo, goldMat);
      trim.position.y = tier.y + tier.height/2 + 0.03;
      trophy.add(trim);
      
      const platesPerSide = Math.ceil(tier.plates.length / 4);
      
      // Use fixed dimensions for all plaques
      const plateWidth = FIXED_PLATE_WIDTH;
      const plateHeight = FIXED_PLATE_HEIGHT;
      
      tier.plates.forEach((champIndex, i) => {
        if (champIndex >= champions.length) return;
        const champ = champions[champIndex];
        
        const side = Math.floor(i / platesPerSide);
        const posOnSide = i % platesPerSide;
        
        const plateGeo = new THREE.BoxGeometry(plateWidth, plateHeight, 0.08);
        const texture = createNameTexture(champ.year, champ.name);
        if (!texture) return;
        const plateMat = new THREE.MeshStandardMaterial({ 
          map: texture, 
          metalness: 0.8, 
          roughness: 0.1,
          emissive: 0xffffff,
          emissiveIntensity: 0.15
        });
        const plate = new THREE.Mesh(plateGeo, plateMat);
        
        // Calculate spacing to distribute plates evenly around the tier
        const spacing = (tier.width - 0.3) / Math.max(platesPerSide, 1);
        const offset = (posOnSide - (platesPerSide - 1) / 2) * spacing;
        const dist = tier.width / 2 + 0.04;
        
        if (side === 0) {
          plate.position.set(offset, tier.y, dist);
        } else if (side === 1) {
          plate.position.set(dist, tier.y, -offset);
          plate.rotation.y = Math.PI / 2;
        } else if (side === 2) {
          plate.position.set(-offset, tier.y, -dist);
          plate.rotation.y = Math.PI;
        } else {
          plate.position.set(-dist, tier.y, offset);
          plate.rotation.y = -Math.PI / 2;
        }
        
        trophy.add(plate);
      });
    });
    
    // Cup pedestal - positioned to sit directly on top tier (tier 4 top at y=4.6)
    const topTierTop = 4.1 + 1.0 / 2; // Top tier center (4.1) + half height (0.5) = 4.6
    
    // Add a small connecting ring to bridge the gap between tier and pedestal
    const connectorGeo = new THREE.CylinderGeometry(0.95, 0.95, 0.05, 32);
    const connector = new THREE.Mesh(connectorGeo, goldMatCup);
    connector.position.y = topTierTop + 0.025; // Sits on top tier
    trophy.add(connector);
    
    const pedestalGeo = new THREE.CylinderGeometry(0.7, 0.95, 0.8, 32);
    const pedestal = new THREE.Mesh(pedestalGeo, goldMatCup);
    // Position pedestal to sit on the connector ring
    pedestal.position.y = topTierTop + 0.05 + 0.4; // Connector top (4.625) + half pedestal height (0.4) = 5.025
    trophy.add(pedestal);
    
    // Cup stem - adjust position based on new pedestal position
    const stemGeo = new THREE.CylinderGeometry(0.35, 0.55, 1.6, 32);
    const stem = new THREE.Mesh(stemGeo, goldMatCup);
    stem.position.y = 6.225; // Adjusted to maintain proper spacing with new pedestal position
    trophy.add(stem);
    
    // Cup bowl
    const cupPoints: THREE.Vector2[] = [];
    for (let i = 0; i <= 20; i++) {
      const t = i / 20;
      const r = 0.4 + Math.pow(t, 0.6) * 1.5;
      cupPoints.push(new THREE.Vector2(r, t * 1.8));
    }
    const cupGeo = new THREE.LatheGeometry(cupPoints, 48);
    const cup = new THREE.Mesh(cupGeo, goldMatCup);
    cup.position.y = 7.0;
    trophy.add(cup);
    
    // Blue rim on cup
    const rimGeo = new THREE.TorusGeometry(1.9, 0.1, 16, 64);
    const rim = new THREE.Mesh(rimGeo, blueMat);
    rim.rotation.x = Math.PI / 2;
    rim.position.y = 8.8;
    trophy.add(rim);
    
    // Handles
    const handleGeo = new THREE.TorusGeometry(0.65, 0.1, 12, 24, Math.PI);
    const handleL = new THREE.Mesh(handleGeo, goldMatCup);
    handleL.position.set(-1.85, 7.9, 0);
    handleL.rotation.z = Math.PI / 2;
    handleL.rotation.y = Math.PI / 2;
    trophy.add(handleL);
    
    const handleR = new THREE.Mesh(handleGeo, goldMatCup);
    handleR.position.set(1.85, 7.9, 0);
    handleR.rotation.z = -Math.PI / 2;
    handleR.rotation.y = -Math.PI / 2;
    trophy.add(handleR);
    
    // Football on top - blue with gold laces
    const fbGeo = new THREE.SphereGeometry(0.45, 32, 32);
    fbGeo.scale(1, 0.6, 0.6);
    const football = new THREE.Mesh(fbGeo, blueMat);
    football.position.y = 9.3;
    football.rotation.z = Math.PI / 4;
    trophy.add(football);
    
    // Gold laces
    for (let i = -2; i <= 2; i++) {
      const laceGeo = new THREE.BoxGeometry(0.04, 0.12, 0.04);
      const lace = new THREE.Mesh(laceGeo, goldMat);
      lace.position.set(i * 0.09, 9.4, 0.27);
      lace.rotation.z = Math.PI / 4;
      trophy.add(lace);
    }
    
    scene.add(trophy);
    
    let rotation = 0;
    let frameId: number;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      rotation += 0.004;
      trophy.rotation.y = rotation;
      if (cameraRef.current) {
        cameraRef.current.position.z = zoomLevelRef.current;
        cameraRef.current.lookAt(0, 4.8, 0); // Match adjusted lookAt
      }
      renderer.render(scene, camera);
    };
    animate();
    
    // Add zoom controls with mouse wheel
    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomSpeed = 0.5;
      const minZoom = 18; // Allow closer zoom
      const maxZoom = 45; // Reduced max zoom since we start closer
      
      if (e.deltaY > 0) {
        // Zoom out
        zoomLevelRef.current = Math.min(maxZoom, zoomLevelRef.current + zoomSpeed);
      } else {
        // Zoom in
        zoomLevelRef.current = Math.max(minZoom, zoomLevelRef.current - zoomSpeed);
      }
    };
    
    const container = containerRef.current;
    if (container) {
      container.addEventListener('wheel', handleWheel, { passive: false });
    }
    
    return () => {
      cancelAnimationFrame(frameId);
      if (container) {
        container.removeEventListener('wheel', handleWheel);
      }
      renderer.dispose();
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-0 pb-12">
        <div ref={containerRef} className="bg-white rounded-lg shadow-lg border border-gray-200 flex justify-center items-center" style={{height: '1000px', width: '100%'}} />
      </div>
    </div>
  );
}
