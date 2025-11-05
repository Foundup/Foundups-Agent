
import React, { useState, useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { CapturedItem, ItemStatus } from './types';
import * as storage from './services/storage';
// import * as ipfs from './services/ipfsService';
import { ItemReviewer } from './components/ItemReviewer';
import { FullscreenGallery } from './components/FullscreenGallery';
import { BottomNavBar } from './components/BottomNavBar';
import { LeftSidebarNav } from './components/LeftSidebarNav';
import { RecordingIndicator } from './components/RecordingIndicator';
// import { PigeonMapView } from './components/PigeonMapView';

export type CaptureMode = 'photo' | 'video';

// Liberty Alert Types (imported from existing modules/communication/liberty_alert/src/models)
interface LibertyAlert {
  id: string;
  location: { latitude: number; longitude: number };
  message: string;
  video_url?: string;
  timestamp: number;
}

// GotJunk Item for Map Display
interface GotJunkItem {
  id: string;
  location: { latitude: number; longitude: number };
  title: string;
  imageUrl: string;
  status: 'available' | 'sold' | 'auction';
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
  // === MY ITEMS (ownership: 'mine') ===
  const [myDrafts, setMyDrafts] = useState<CapturedItem[]>([]); // status: 'draft' - in review
  const [myListed, setMyListed] = useState<CapturedItem[]>([]); // status: 'listed' - available for others

  // === OTHER PEOPLE'S ITEMS (ownership: 'others') ===
  const [browseFeed, setBrowseFeed] = useState<CapturedItem[]>([]); // status: 'browsing' - Tab 1
  const [cart, setCart] = useState<CapturedItem[]>([]); // status: 'in_cart' - Tab 4
  const [skipped, setSkipped] = useState<CapturedItem[]>([]); // status: 'skipped' - hidden

  // === NAVIGATION STATE ===
  const [activeTab, setActiveTab] = useState<'browse' | 'map' | 'myitems' | 'cart'>('browse');

  // === UI STATE ===
  const [isGalleryOpen, setGalleryOpen] = useState(false);
  const [captureMode, setCaptureMode] = useState<CaptureMode>('photo');
  const [isRecording, setIsRecording] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | undefined>();

  // Liberty Alert State (unlocked via SOS morse code easter egg)
  const [libertyAlerts, setLibertyAlerts] = useState<LibertyAlert[]>([]);
  const [libertyEnabled, setLibertyEnabled] = useState(false); // OFF until SOS unlock
  const [voiceRecognition, setVoiceRecognition] = useState<any>(null);
  const [keywordDetected, setKeywordDetected] = useState(false);

  // SOS Morse Code Detection State
  const [tapTimes, setTapTimes] = useState<number[]>([]);
  const tapTimeoutRef = useRef<number | null>(null);
  const sosDetectionActive = useRef<boolean>(false);

  useEffect(() => {
    const initializeApp = async () => {
//       // Initialize IPFS (Helia) for decentralized storage
//       try {
//         await ipfs.initHelia();
//         console.log('[GotJunk] IPFS initialized - decentralized storage ready');
//       } catch (error) {
//         console.error('[GotJunk] IPFS initialization failed:', error);
//       }

      const allItems = await storage.getAllItems();

      try {
        const position = await getCurrentPositionPromise();
        const { latitude, longitude } = position.coords;
        setUserLocation({ latitude, longitude });

        // Separate MY items from OTHER people's items
        const myItems = allItems.filter(item => item.ownership === 'mine');
        const otherItems = allItems.filter(item => item.ownership === 'others');

        // Filter OTHER people's items by 50km radius
        const nearby = otherItems.filter(item => {
          if (typeof item.latitude !== 'number' || typeof item.longitude !== 'number') {
            return false;
          }
          const distance = calculateDistance(latitude, longitude, item.latitude, item.longitude);
          return distance <= 50;
        });

        // MY ITEMS: Separate by status
        setMyDrafts(myItems.filter(item => item.status === 'draft'));
        setMyListed(myItems.filter(item => item.status === 'listed'));

        // OTHER PEOPLE'S ITEMS: Separate by status
        setBrowseFeed(nearby.filter(item => item.status === 'browsing'));
        setCart(nearby.filter(item => item.status === 'in_cart'));
        setSkipped(nearby.filter(item => item.status === 'skipped'));

      } catch (error) {
        console.error("Geolocation error or permission denied:", error);

        // Fallback: Load MY items only (no location filtering)
        const myItems = allItems.filter(item => item.ownership === 'mine');
        setMyDrafts(myItems.filter(item => item.status === 'draft'));
        setMyListed(myItems.filter(item => item.status === 'listed'));
      }

      // Store user location for map
      try {
        const position = await getCurrentPositionPromise();
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      } catch (error) {
        console.error("Could not get user location for map:", error);
      }
    };
    initializeApp();
  }, []);

  // Liberty Alert: Initialize Web Speech API when recording starts
  useEffect(() => {
    if (!libertyEnabled || !isRecording) {
      // Stop voice recognition if recording stops
      if (voiceRecognition) {
        voiceRecognition.stop();
        setVoiceRecognition(null);
      }
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Liberty Alert - Web Speech API not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = 'en-US';
    recognition.interimResults = true; // Get interim results for better detection

    // Liberty Alert keywords (expanded list from user request)
    const LIBERTY_KEYWORDS = ['ice', 'immigration', 'checkpoint', 'raid', 'kidnap', 'undocumented', 'illegal', 'snatched'];

    recognition.onresult = (event: any) => {
      const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
      console.log('Liberty Alert - Voice detected:', transcript);

      if (LIBERTY_KEYWORDS.some(kw => transcript.includes(kw))) {
        console.log('🧊 Liberty Alert - KEYWORD DETECTED:', transcript);
        setKeywordDetected(true);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Liberty Alert - Speech recognition error:', event.error);
    };

    recognition.start();
    setVoiceRecognition(recognition);
    console.log('🎤 Liberty Alert - Voice listening started during video recording');

    return () => {
      recognition.stop();
      console.log('🎤 Liberty Alert - Voice listening stopped');
    };
  }, [libertyEnabled, isRecording]);

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
      status: 'draft', // MY items start as drafts
      ownership: 'mine', // I captured this item
      createdAt: Date.now(),
      ...location,
    };

    await storage.saveItem(newItem);
    setMyDrafts(current => [newItem, ...current]);

    // Liberty Alert: If keyword detected during video recording, create alert
    if (libertyEnabled && keywordDetected && blob.type.startsWith('video/')) {
      console.log('🧊 Liberty Alert - Creating ice cube marker for video');

      // TODO: Upload video to YouTube as unlisted (user's brilliant idea!)
      // For now, store video locally and create alert
      const alert: LibertyAlert = {
        id: `alert-${Date.now()}`,
        location: location || { latitude: 0, longitude: 0 },
        message: 'Liberty Alert - Keyword detected',
        video_url: newItem.url, // Temporary - will be YouTube URL
        timestamp: Date.now(),
      };

      setLibertyAlerts(prev => [alert, ...prev]);

      // TODO: Post to backend API
      // await fetch('/api/liberty/alert', {
      //   method: 'POST',
      //   body: JSON.stringify(alert),
      // });

      console.log('🧊 Ice cube marker created on map!');
      setKeywordDetected(false); // Reset for next recording
    }
  };
  
  const handleReviewDecision = async (item: CapturedItem, decision: 'keep' | 'delete') => {
    // Optimistically remove from draft queue for snappy UI
    setMyDrafts(current => current.filter(i => i.id !== item.id));

    if (decision === 'keep') {
      const listedItem: CapturedItem = {
        ...item,
        status: 'listed', // Change status: 'draft' → 'listed'
        ownership: 'mine' // Ensure ownership is set
      };

//       // Upload to IPFS in background for decentralized storage
//       try {
//         console.log('[GotJunk] Uploading to IPFS...');
//         const ipfsCid = await ipfs.uploadToIPFS(item.blob);
//         console.log('[GotJunk] IPFS upload successful:', ipfsCid);
// 
//         // Update item with IPFS CID
//         listedItem.ipfsCid = ipfsCid;
//         await storage.updateItemStatus(item.id, 'listed');
// 
//         // TODO: Pin item for storage rewards (WSP 98 mesh network)
//         // await ipfs.pinItem(ipfsCid);
//       } catch (error) {
//         console.error('[GotJunk] IPFS upload failed:', error);
//         // Continue with local storage only
//         await storage.updateItemStatus(item.id, 'listed');
//       }

      setMyListed(current => [listedItem, ...current]);
    } else {
      // Delete: Remove from storage entirely
      URL.revokeObjectURL(item.url);
      await storage.deleteItem(item.id);
    }
  };

  const handleDeleteMyItem = async (itemToDelete: CapturedItem) => {
    URL.revokeObjectURL(itemToDelete.url);
    await storage.deleteItem(itemToDelete.id);
    setMyListed(current => current.filter(item => item.id !== itemToDelete.id));
  };

  // BROWSE FEED: Handle swipe actions on other people's items
  const handleBrowseSwipe = async (item: CapturedItem, direction: 'left' | 'right') => {
    // Remove from browse feed
    setBrowseFeed(current => current.filter(i => i.id !== item.id));

    if (direction === 'right') {
      // Swipe RIGHT = Add to cart
      const cartItem: CapturedItem = { ...item, status: 'in_cart' };
      setCart(current => [cartItem, ...current]);
      await storage.updateItemStatus(item.id, 'in_cart');
    } else {
      // Swipe LEFT = Skip (don't show again)
      const skippedItem: CapturedItem = { ...item, status: 'skipped' };
      setSkipped(current => [skippedItem, ...current]);
      await storage.updateItemStatus(item.id, 'skipped');
    }
  };

  const currentReviewItem = myDrafts.length > 0 ? myDrafts[0] : null;

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


      {/* Main Content Area - Tab-Based */}
      <div className="flex-grow relative flex flex-col justify-center items-center">
        {/* TAB 1: BROWSE FEED (other people's items in 50km radius) */}
        {activeTab === 'browse' && (
          <>
            <AnimatePresence>
              {browseFeed.length > 0 && (
                <ItemReviewer
                  key={browseFeed[0].id}
                  item={browseFeed[0]}
                  onDecision={(decision) => handleBrowseSwipe(browseFeed[0], decision === 'keep' ? 'right' : 'left')}
                />
              )}
            </AnimatePresence>

            {browseFeed.length === 0 && !isRecording && (
              <div className="text-center p-8">
                <h2 className="text-3xl font-bold text-white mb-3">GotJunk?!</h2>
                <p className="text-xl text-gray-300 font-semibold mb-2">Browse items near you</p>
                <p className="text-lg text-green-400 font-bold">
                  Swipe Right ➡️ to Cart | Swipe Left ⬅️ to Skip
                </p>
                <p className="text-sm text-gray-400 mt-3">50km radius • No items found</p>
              </div>
            )}
          </>
        )}

        {/* TAB 2: MAP (shown via overlay, content hidden) */}
        {/* Map is rendered separately as overlay */}

        {/* TAB 3: MY ITEMS (my drafts + listed items) */}
        {activeTab === 'myitems' && (
          <>
            <AnimatePresence>
              {currentReviewItem && (
                <ItemReviewer
                  key={currentReviewItem.id}
                  item={currentReviewItem}
                  onDecision={handleReviewDecision}
                />
              )}
            </AnimatePresence>

            {myDrafts.length === 0 && myListed.length === 0 && !isRecording && (
              <div className="text-center p-8">
                <h2 className="text-3xl font-bold text-white mb-3">My Items</h2>
                <p className="text-xl text-gray-300 font-semibold mb-2">Capture your first item!</p>
                <p className="text-lg text-green-400 font-bold">
                  Snap it! 📸 Swipe Up ⬆️ to List
                </p>
                <p className="text-sm text-gray-400 mt-3">No items yet</p>
              </div>
            )}
          </>
        )}

        {/* TAB 4: CART (items I want from others) */}
        {activeTab === 'cart' && (
          <div className="text-center p-8">
            <h2 className="text-3xl font-bold text-white mb-3">Shopping Cart</h2>
            <p className="text-xl text-gray-300 font-semibold mb-2">{cart.length} items</p>
            {cart.length === 0 && (
              <p className="text-sm text-gray-400 mt-3">Swipe right on browse items to add them here</p>
            )}
          </div>
        )}
      </div>

      {/* Left sidebar navigation */}
      <LeftSidebarNav
        activeTab={activeTab}
        onGalleryClick={() => {
          if (!sosDetectionActive.current) {
            setActiveTab('browse'); // Tab 1: Browse
          }
        }}
        onGalleryIconTap={(duration) => {
          const SHORT_TAP = 200;
          setTapTimes(prev => {
            const newTaps = [...prev, duration];
            if (newTaps.length > 0) {
              sosDetectionActive.current = true;
            }
            if (newTaps.length > 9) newTaps.shift();
            if (newTaps.length === 9) {
              const pattern = newTaps.map(d => d < SHORT_TAP ? 'S' : 'L').join('');
              console.log('🔍 SOS Pattern:', pattern);
              if (pattern === 'SSSLLLSSS') {
                console.log('🗽 SOS DETECTED!');
                setLibertyEnabled(true);
                alert('🗽 Liberty Alert Unlocked!');
                sosDetectionActive.current = false;
                return [];
              }
            }
            return newTaps;
          });
          if (tapTimeoutRef.current) clearTimeout(tapTimeoutRef.current);
          tapTimeoutRef.current = window.setTimeout(() => {
            setTapTimes([]);
            sosDetectionActive.current = false;
          }, 3000);
        }}
        onMapClick={() => {
          setTapTimes([]);
          sosDetectionActive.current = false;
          if (tapTimeoutRef.current) clearTimeout(tapTimeoutRef.current);
          setActiveTab('map'); // Tab 2: Map
          setMapOpen(true);
        }}
        onMyItemsClick={() => {
          setActiveTab('myitems'); // Tab 3: My Items
          console.log('📦 My Items clicked');
        }}
        onCartClick={() => {
          setActiveTab('cart'); // Tab 4: Cart
          console.log('🛒 Cart clicked');
        }}
        libertyEnabled={libertyEnabled}
      />

      {/* Bottom navigation bar */}
      <BottomNavBar
        captureMode={captureMode}
        onToggleCaptureMode={() => setCaptureMode(mode => mode === 'photo' ? 'video' : 'photo')}
        onCapture={handleCapture}
        onReviewAction={(action) => {
          if (activeTab === 'browse' && browseFeed.length > 0) {
            handleBrowseSwipe(browseFeed[0], action === 'keep' ? 'right' : 'left');
          } else if (activeTab === 'myitems' && currentReviewItem) {
            handleReviewDecision(currentReviewItem, action);
          }
        }}
        isRecording={isRecording}
        setIsRecording={setIsRecording}
        countdown={countdown}
        setCountdown={setCountdown}
        hasReviewItems={activeTab === 'browse' ? browseFeed.length > 0 : myDrafts.length > 0}
        onSearchClick={() => {
          console.log('🔍 Search clicked');
          // TODO: Open search modal
        }}
      />

      {isGalleryOpen && (
        <FullscreenGallery
          items={myListed}
          onClose={() => setGalleryOpen(false)}
          onDelete={handleDeleteMyItem}
        />
      )}

    </div>
  );
};

export default App;
