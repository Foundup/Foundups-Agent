
import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CapturedItem, ItemStatus } from './types';
import * as storage from './services/storage';
import { ItemReviewer } from './components/ItemReviewer';
import { FullscreenGallery } from './components/FullscreenGallery';
import { BottomNavBar } from './components/BottomNavBar';
import { RecordingIndicator } from './components/RecordingIndicator';

export type CaptureMode = 'photo' | 'video';

// Liberty Alert Types (imported from existing modules/communication/liberty_alert/src/models)
interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  message: string;
  video_url?: string;
  timestamp: number;
}

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

  // Liberty Alert State
  const [libertyAlerts, setLibertyAlerts] = useState<LibertyAlert[]>([]);
  const [isLibertyListening, setIsLibertyListening] = useState(false);
  const [libertyEnabled, setLibertyEnabled] = useState(false);

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

  // Liberty Alert: Web Speech API initialization
  useEffect(() => {
    if (!libertyEnabled || !isLibertyListening) return;

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Web Speech API not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    const ICE_KEYWORDS = ['ice', 'immigration', 'checkpoint', 'raid'];

    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
      console.log('Liberty Alert - Transcript:', transcript);

      if (ICE_KEYWORDS.some(kw => transcript.includes(kw))) {
        console.log('Liberty Alert - Keyword detected! Triggering alert...');
        handleLibertyAlertTrigger();
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Liberty Alert - Speech recognition error:', event.error);
    };

    recognition.start();
    console.log('Liberty Alert - Voice listening started');

    return () => {
      recognition.stop();
      console.log('Liberty Alert - Voice listening stopped');
    };
  }, [libertyEnabled, isLibertyListening]);

  const handleLibertyAlertTrigger = async () => {
    console.log('Liberty Alert - Creating alert with 10-second video recording');

    try {
      const position = await getCurrentPositionPromise();
      const { latitude, longitude } = position.coords;

      // Create alert with location
      const newAlert: LibertyAlert = {
        id: `alert-${Date.now()}`,
        location: { latitude, longitude },
        message: 'ICE Alert',
        timestamp: Date.now(),
      };

      // TODO: Record 10-second video and upload to backend
      // For now, add alert to local state
      setLibertyAlerts(prev => [newAlert, ...prev]);

      // Post alert to backend (will integrate with existing Liberty Alert modules)
      // await fetch('/api/liberty/alert', {
      //   method: 'POST',
      //   body: JSON.stringify(newAlert),
      // });

    } catch (error) {
      console.error('Liberty Alert - Failed to create alert:', error);
    }
  };

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

      {/* Liberty Alert Floating Button */}
      {libertyEnabled && (
        <motion.button
          className={`fixed bottom-32 right-6 z-50 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center text-3xl transition-colors ${
            isLibertyListening ? 'bg-amber-500 animate-pulse' : 'bg-amber-600/80'
          }`}
          onTouchStart={() => setIsLibertyListening(true)}
          onTouchEnd={() => setIsLibertyListening(false)}
          onMouseDown={() => setIsLibertyListening(true)}
          onMouseUp={() => setIsLibertyListening(false)}
          whileTap={{ scale: 0.9 }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
        >
          🗽
        </motion.button>
      )}

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
        onMapClick={() => {
          // Enable Liberty Alert mode
          if (!libertyEnabled) {
            setLibertyEnabled(true);
            alert('🗽 Liberty Alert Mode Enabled! Press and hold the Liberty button to activate voice detection. Say keywords like "ICE", "immigration", "checkpoint", or "raid" to trigger an alert.');
          } else {
            // TODO: Show map with ice cube markers for liberty alerts
            alert(`Liberty Alert Map - ${libertyAlerts.length} alerts nearby`);
          }
        }}
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
