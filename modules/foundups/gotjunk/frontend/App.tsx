
import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { CapturedItem, ItemStatus } from './types';
import * as storage from './services/storage';
import { ItemReviewer } from './components/ItemReviewer';
import { FullscreenGallery } from './components/FullscreenGallery';
import { BottomNavBar } from './components/BottomNavBar';
import { RecordingIndicator } from './components/RecordingIndicator';

export type CaptureMode = 'photo' | 'video';

// Haversine formula to calculate distance between two lat/lon points in kilometers
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

const getCurrentPositionPromise = (): Promise<GeolocationPosition> => {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    });
  });
};


const App: React.FC = () => {
  const [reviewItems, setReviewItems] = useState<CapturedItem[]>([]);
  const [keptItems, setKeptItems] = useState<CapturedItem[]>([]);
  const [isGalleryOpen, setGalleryOpen] = useState(false);
  const [captureMode, setCaptureMode] = useState<CaptureMode>('photo');
  const [isRecording, setIsRecording] = useState(false);
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    const initializeApp = async () => {
      const allItems = await storage.getAllItems();
      let itemsToDisplay = allItems;
      
      try {
        const position = await getCurrentPositionPromise();
        const { latitude, longitude } = position.coords;
        
        itemsToDisplay = allItems.filter(item => {
          if (typeof item.latitude !== 'number' || typeof item.longitude !== 'number') {
            return false;
          }
          const distance = calculateDistance(latitude, longitude, item.latitude, item.longitude);
          return distance <= 50;
        });

      } catch (error) {
        console.error("Geolocation error or permission denied:", error);
      }
      
      setReviewItems(itemsToDisplay.filter(item => item.status === 'review'));
      setKeptItems(itemsToDisplay.filter(item => item.status === 'kept'));
    };
    initializeApp();
  }, []);

  const handleCapture = async (blob: Blob) => {
    let location: { latitude: number, longitude: number } | undefined = undefined;
    try {
      const position = await getCurrentPositionPromise();
      location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
    } catch (error) {
      console.error("Could not get location for capture:", error);
    }

    const newItem: CapturedItem = {
      id: `item-${Date.now()}`,
      blob,
      url: URL.createObjectURL(blob),
      status: 'review',
      ...location,
    };

    await storage.saveItem(newItem);
    setReviewItems(current => [newItem, ...current]);
  };
  
  const handleReviewDecision = async (item: CapturedItem, decision: 'keep' | 'delete') => {
    // Optimistically remove from review queue for a snappy UI
    setReviewItems(current => current.filter(i => i.id !== item.id));

    if (decision === 'keep') {
      const keptItem = { ...item, status: 'kept' as ItemStatus };
      await storage.updateItemStatus(item.id, 'kept');
      setKeptItems(current => [keptItem, ...current]);
    } else {
      URL.revokeObjectURL(item.url);
      await storage.deleteItem(item.id);
    }
  };

  const handleDeleteKeptItem = async (itemToDelete: CapturedItem) => {
    URL.revokeObjectURL(itemToDelete.url);
    await storage.deleteItem(itemToDelete.id);
    setKeptItems(current => current.filter(item => item.id !== itemToDelete.id));
  };
  
  const currentReviewItem = reviewItems.length > 0 ? reviewItems[0] : null;

  return (
    <div 
      className="h-full w-full flex flex-col overflow-hidden bg-gray-900"
      style={{
        background: 'linear-gradient(160deg, #2A3A68 49.9%, #2F4179 50%)'
      }}
    >
       <AnimatePresence>
        {isRecording && <RecordingIndicator countdown={countdown} />}
      </AnimatePresence>

      <div className="flex-grow relative flex flex-col justify-center items-center">
        <AnimatePresence>
          {currentReviewItem && (
            <ItemReviewer 
              key={currentReviewItem.id} 
              item={currentReviewItem} 
              onDecision={handleReviewDecision} 
            />
          )}
        </AnimatePresence>
        
        {reviewItems.length === 0 && !isRecording && (
          <div className="text-center p-8">
               <h2 className="text-2xl font-bold text-white">Welcome to GotJunk!</h2>
               <p className="text-gray-300 mt-1 max-w-xs">It's Tinder for Your Junk! 1. Swipe what you want or Snap what you have. AI does the rest.</p>
          </div>
        )}
      </div>

      <BottomNavBar 
        captureMode={captureMode}
        onToggleCaptureMode={() => setCaptureMode(mode => mode === 'photo' ? 'video' : 'photo')}
        onCapture={handleCapture}
        onReviewAction={(action) => currentReviewItem && handleReviewDecision(currentReviewItem, action)}
        onGalleryClick={() => setGalleryOpen(true)}
        onMapClick={() => alert('Map view coming soon!')}
        isRecording={isRecording}
        setIsRecording={setIsRecording}
        countdown={countdown}
        setCountdown={setCountdown}
        hasReviewItems={reviewItems.length > 0}
      />

      {isGalleryOpen && (
        <FullscreenGallery
          items={keptItems}
          onClose={() => setGalleryOpen(false)}
          onDelete={handleDeleteKeptItem}
        />
      )}
    </div>
  );
};

export default App;
