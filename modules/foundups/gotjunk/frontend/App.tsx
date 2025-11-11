
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
import { PhotoGrid } from './components/PhotoGrid';
import { ClassificationModal } from './components/ClassificationModal';
import { OptionsModal } from './components/OptionsModal';
import { InstructionsModal } from './components/InstructionsModal';
import { PurchaseModal } from './components/PurchaseModal';
import { ItemClassification } from './types';
import { PigeonMapView } from './components/PigeonMapView';
import { useViewport } from './hooks/useViewport';
import { useViewportHeight } from './hooks/useViewportHeight';

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
  const [activeTab, setActiveTab] = useState<'browse' | 'myitems' | 'cart'>('browse');

  // === UI STATE ===
  const [isGalleryOpen, setGalleryOpen] = useState(false);
  const [isMapOpen, setMapOpen] = useState(false);
  const [captureMode, setCaptureMode] = useState<CaptureMode>('photo');
  const [isRecording, setIsRecording] = useState(false);
  const [countdown, setCountdown] = useState(10);
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | undefined>();
  const [locationFilter, setLocationFilter] = useState<{ latitude: number; longitude: number } | null>(null);

  // === INSTRUCTIONS MODAL (shows on every page load) ===
  const [showInstructions, setShowInstructions] = useState(true);

  // === CLASSIFICATION FILTER ===
  const [classificationFilter, setClassificationFilter] = useState<'all' | ItemClassification>('all');

  // === RESPONSIVE VIEWPORT (iOS Safari vh fix) ===
  useViewport();
  useViewportHeight(); // Track visualViewport for proper modal centering

  // === CLASSIFICATION STATE ===
  const [pendingClassificationItem, setPendingClassificationItem] = useState<{blob: Blob, url: string, location?: {latitude: number, longitude: number}} | null>(null);
  const [isProcessingClassification, setIsProcessingClassification] = useState(false);

  // Safety backup: Store last captured item that needs classification
  const pendingClassificationBackupRef = useRef<{blob: Blob, url: string, location?: {latitude: number, longitude: number}} | null>(null);
  const classificationCompletedRef = useRef(false);

  // === AUTO-CLASSIFY STATE ===
  const [autoClassifyEnabled, setAutoClassifyEnabled] = useState(false);
  const [lastClassification, setLastClassification] = useState<{
    type: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number
  } | null>(null);
  const [isSelectingClassification, setIsSelectingClassification] = useState(false); // True when long-pressing toggle to select classification

  // Safety verification: Ensure classification modal appears and waits for user selection
  useEffect(() => {
    if (!pendingClassificationItem && pendingClassificationBackupRef.current && !classificationCompletedRef.current) {
      // Classification modal disappeared without user completing it!
      const backup = pendingClassificationBackupRef.current;

      console.warn('[GotJunk] SAFETY CHECK: Classification modal closed without selection! Restoring...');

      // Restore the pending item after a short delay to ensure clean state
      setTimeout(() => {
        if (!classificationCompletedRef.current) {
          console.log('[GotJunk] SAFETY RESTORE: Re-opening classification modal');
          setPendingClassificationItem(backup);
        }
      }, 100);
    }
  }, [pendingClassificationItem]);

  // === FULLSCREEN REVIEW STATE (My Items tab) ===
  const [reviewingItem, setReviewingItem] = useState<CapturedItem | null>(null);
  const [reviewQueue, setReviewQueue] = useState<CapturedItem[]>([]);

  // === FULLSCREEN REVIEW STATE (Cart tab) ===
  const [reviewingCartItem, setReviewingCartItem] = useState<CapturedItem | null>(null);
  const [cartReviewQueue, setCartReviewQueue] = useState<CapturedItem[]>([]);

  // === RE-CLASSIFICATION STATE ===
  const [reclassifyingItem, setReclassifyingItem] = useState<CapturedItem | null>(null);
  const [editingOptionsItem, setEditingOptionsItem] = useState<CapturedItem | null>(null);

  // === PURCHASE MODAL STATE (Cart items) ===
  const [purchasingItem, setPurchasingItem] = useState<CapturedItem | null>(null);

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

        // TODO: Future feature - add owner filter toggle to exclude user's own items from browse feed
        // For now, show ALL items (including mine) for testing "Tinder for stuff" experience
        // When filter is added, restore: const otherItems = allItems.filter(item => item.ownership === 'others');

        // Filter ALL items by 50km radius (including my items for testing)
        const nearby = allItems.filter(item => {
          if (typeof item.latitude !== 'number' || typeof item.longitude !== 'number') {
            return false;
          }
          const distance = calculateDistance(latitude, longitude, item.latitude, item.longitude);
          return distance <= 50;
        });

        // MY ITEMS: Separate by status (for My Items tab)
        setMyDrafts(myItems.filter(item => item.status === 'draft'));
        setMyListed(myItems.filter(item => item.status === 'listed'));

        // BROWSE FEED: Show ALL nearby items (including mine) - "Tinder for stuff"
        // Include draft, browsing, and listed items for full "My Items on landing" experience
        setBrowseFeed(nearby.filter(item =>
          item.status === 'draft' || item.status === 'browsing' || item.status === 'listed'
        ));
        setCart(nearby.filter(item => item.status === 'in_cart'));
        setSkipped(nearby.filter(item => item.status === 'skipped'));

      } catch (error) {
        console.error("Geolocation error or permission denied:", error);

        // Fallback: Load ALL items (no location filtering) for "Tinder for stuff" experience
        const myItems = allItems.filter(item => item.ownership === 'mine');
        setMyDrafts(myItems.filter(item => item.status === 'draft'));
        setMyListed(myItems.filter(item => item.status === 'listed'));

        // Show all items (draft + browsing + listed) in browse feed even without location
        setBrowseFeed(allItems.filter(item =>
          item.status === 'draft' || item.status === 'browsing' || item.status === 'listed'
        ));
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

    const capturedItem = {
      blob,
      url: URL.createObjectURL(blob),
      location
    };

    // Check if auto-classify is enabled
    if (autoClassifyEnabled && lastClassification) {
      console.log('[GotJunk] Auto-classify enabled - using last classification:', lastClassification);

      // Mark as completed immediately to skip safety verification
      classificationCompletedRef.current = true;
      pendingClassificationBackupRef.current = null;

      // Directly process with last classification (skip modal) - pass item directly to avoid race condition
      await handleClassify(
        lastClassification.type,
        lastClassification.discountPercent,
        lastClassification.bidDurationHours,
        capturedItem  // Pass item directly instead of relying on setState
      );
      return;
    }

    // Manual mode: Show classification modal
    // Reset classification completion flag for new capture
    classificationCompletedRef.current = false;

    // Store backup for safety verification
    pendingClassificationBackupRef.current = capturedItem;

    // Show classification modal
    console.log('[GotJunk] Photo captured - opening classification modal');
    setPendingClassificationItem(capturedItem);
  };

  // Handler for long-press on auto-classify toggle
  const handleLongPressAutoClassify = () => {
    console.log('[GotJunk] Long-press on auto-classify toggle - opening classification selector');

    // Set flag to indicate we're selecting classification (not classifying an actual item)
    setIsSelectingClassification(true);

    // Create a phantom item to trigger classification modal (won't be saved)
    const phantomItem = {
      blob: new Blob(), // Empty blob
      url: '', // No preview
      location: userLocation || undefined
    };

    // Set pending item to trigger classification modal
    setPendingClassificationItem(phantomItem);
  };

  const handleClassify = async (
    classification: ItemClassification,
    discountPercent?: number,
    bidDurationHours?: number,
    itemOverride?: {blob: Blob, url: string, location?: {latitude: number, longitude: number}}
  ) => {
    console.log('[GotJunk] handleClassify called:', { classification, discountPercent, bidDurationHours, hasPending: !!pendingClassificationItem, hasOverride: !!itemOverride, isProcessing: isProcessingClassification });

    // Use itemOverride for auto-classify (avoids React setState race condition)
    const item = itemOverride || pendingClassificationItem;

    // Prevent duplicate calls (race condition guard)
    if (!item || isProcessingClassification) {
      console.warn('[GotJunk] handleClassify called but no item or already processing!');
      return;
    }

    // Immediately capture the item data and clear pending state to prevent race conditions
    const { blob, url, location } = item;

    // Mark classification as completed to prevent safety restore
    classificationCompletedRef.current = true;
    pendingClassificationBackupRef.current = null;

    // Store this classification for future auto-classify
    setLastClassification({
      type: classification,
      discountPercent,
      bidDurationHours
    });
    console.log('[GotJunk] Stored classification for future auto-classify:', { classification, discountPercent, bidDurationHours });

    // SPECIAL CASE: Classification selection mode (long-press on toggle)
    if (isSelectingClassification) {
      console.log('[GotJunk] Classification selection mode - enabling auto-classify with selected type:', classification);
      setAutoClassifyEnabled(true);
      setIsSelectingClassification(false);
      setPendingClassificationItem(null);
      setIsProcessingClassification(false);
      return; // Don't create an item - just store the classification and enable auto-classify
    }

    setPendingClassificationItem(null);
    setIsProcessingClassification(true);

    console.log('[GotJunk] Classification processing started, pending item cleared');

    try {
      // Calculate price based on classification
      // TODO: Get originalPrice from Google Vision API
      const defaultPrice = 100; // Placeholder until Vision API integration
      let price = 0;

      // Use provided values or defaults
      const finalDiscountPercent = discountPercent || 75;
      const finalBidDurationHours = bidDurationHours || 48;

      if (classification === 'free') {
        price = 0;
      } else if (classification === 'discount') {
        // Use the selected discount percentage
        price = defaultPrice * (1 - finalDiscountPercent / 100);
      } else if (classification === 'bid') {
        price = defaultPrice * 0.5; // Starting bid at 50% OFF
      }

      const newItem: CapturedItem = {
        id: `item-${Date.now()}`,
        blob,
        url,
        status: 'draft', // Photos go to myDrafts (ownership='mine', status='draft')
        ownership: 'mine', // User's own items
        classification,
        price,
        originalPrice: defaultPrice,
        discountPercent: classification === 'discount' ? finalDiscountPercent : undefined,
        bidDurationHours: classification === 'bid' ? finalBidDurationHours : undefined,
        createdAt: Date.now(),
        ...location,
      };

      console.log('[GotJunk] Saving new item:', { id: newItem.id, classification, price });
      await storage.saveItem(newItem);

      setMyDrafts(current => {
        console.log('[GotJunk] Adding to myDrafts, current count:', current.length);
        return [newItem, ...current];
      });

      console.log('[GotJunk] Item successfully created and added to drafts');

      // Liberty Alert: If keyword detected during video recording, create alert
      if (libertyEnabled && keywordDetected && blob.type.startsWith('video/')) {
        console.log('🧊 Liberty Alert - Creating ice cube marker for video');
        const alert: LibertyAlert = {
          id: `alert-${Date.now()}`,
          location: location || { latitude: 0, longitude: 0 },
          message: 'Liberty Alert - Keyword detected',
          video_url: newItem.url,
          timestamp: Date.now(),
        };
        setLibertyAlerts(prev => [alert, ...prev]);
        console.log('🧊 Ice cube marker created on map!');
        setKeywordDetected(false);
      }
    } finally {
      // Always reset processing flag, even if there's an error
      setIsProcessingClassification(false);
      console.log('[GotJunk] Classification processing complete, flag reset');
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

  
  // Re-classify existing item
  const handleReclassify = async (item: CapturedItem, newClassification: ItemClassification, discountPercent?: number, bidDurationHours?: number) => {
    console.log('[GotJunk] handleReclassify called:', { itemId: item.id, newClassification, discountPercent, bidDurationHours });

    const defaultPrice = 100; // Will be from Google Vision API

    // Use provided values or defaults
    const finalDiscountPercent = discountPercent || 75;
    const finalBidDurationHours = bidDurationHours || 48;

    let price = 0;

    if (newClassification === 'free') {
      price = 0;
    } else if (newClassification === 'discount') {
      price = defaultPrice * (1 - finalDiscountPercent / 100);
    } else if (newClassification === 'bid') {
      price = defaultPrice * 0.5; // 50% OFF starting bid
    }

    const updatedItem: CapturedItem = {
      ...item,
      classification: newClassification,
      price,
      discountPercent: newClassification === 'discount' ? finalDiscountPercent : undefined,
      bidDurationHours: newClassification === 'bid' ? finalBidDurationHours : undefined,
    };

    console.log('[GotJunk] Updating item in state:', { id: updatedItem.id, status: item.status });

    // Update in state
    if (item.status === 'draft') {
      setMyDrafts(prev => {
        const updated = prev.map(i => i.id === item.id ? updatedItem : i);
        console.log('[GotJunk] myDrafts updated, count:', updated.length);
        return updated;
      });
    } else {
      setMyListed(prev => {
        const updated = prev.map(i => i.id === item.id ? updatedItem : i);
        console.log('[GotJunk] myListed updated, count:', updated.length);
        return updated;
      });
    }

    // Update in IndexedDB
    console.log('[GotJunk] Saving to IndexedDB...');
    await storage.saveItem(updatedItem);
    console.log('[GotJunk] Saved to IndexedDB successfully');

    setReclassifyingItem(null);
  };

  // Update options for discount/bid
  const handleUpdateOptions = async (item: CapturedItem, discountPercent?: number, bidDurationHours?: number) => {
    const defaultPrice = 100;
    let price = item.price || 0;

    if (item.classification === 'discount' && discountPercent) {
      price = defaultPrice * (1 - discountPercent / 100);
    }

    const updatedItem: CapturedItem = {
      ...item,
      price,
      discountPercent: discountPercent || item.discountPercent,
      bidDurationHours: bidDurationHours || item.bidDurationHours,
    };

    // Update in state
    if (item.status === 'draft') {
      setMyDrafts(prev => prev.map(i => i.id === item.id ? updatedItem : i));
    } else {
      setMyListed(prev => prev.map(i => i.id === item.id ? updatedItem : i));
    }

    // Update in IndexedDB
    await storage.saveItem(updatedItem);

    setEditingOptionsItem(null);
  };

// Filter browse feed by classification type AND location (if map marker clicked)
  let filteredBrowseFeed = classificationFilter === 'all'
    ? browseFeed
    : browseFeed.filter(item => item.classification === classificationFilter);

  // Further filter by location if a map marker was clicked (show only items at that location)
  if (locationFilter) {
    const LOCATION_THRESHOLD = 0.001; // ~100m radius
    filteredBrowseFeed = filteredBrowseFeed.filter(item =>
      item.latitude && item.longitude &&
      Math.abs(item.latitude - locationFilter.latitude) < LOCATION_THRESHOLD &&
      Math.abs(item.longitude - locationFilter.longitude) < LOCATION_THRESHOLD
    );
  }

  const currentReviewItem = myDrafts.length > 0 ? myDrafts[0] : null;
  const showCameraOrb = !isMapOpen && activeTab === 'myitems';

  // Handle instructions modal close
  const handleInstructionsClose = () => {
    setShowInstructions(false);
  };

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
        {/* TAB 1: BROWSE FEED - Tinder for stuff */}
        {activeTab === 'browse' && (
          <>
            {/* Filter Dropdown (top right) */}
            <div className="absolute top-4 right-4 z-10">
              <select
                value={classificationFilter}
                onChange={(e) => setClassificationFilter(e.target.value as 'all' | ItemClassification)}
                className="bg-gray-800/90 text-white px-4 py-2 rounded-xl border-2 border-gray-600 shadow-xl text-sm font-semibold hover:bg-gray-700/90 transition-all"
              >
                <option value="all">All Items</option>
                <option value="free">Free</option>
                <option value="discount">Discounted</option>
                <option value="bid">Auction</option>
              </select>
            </div>

            {/* Swipeable Item */}
            <AnimatePresence>
              {filteredBrowseFeed.length > 0 && (
                <ItemReviewer
                  key={filteredBrowseFeed[0].id}
                  item={filteredBrowseFeed[0]}
                  onDecision={(item, decision) => handleBrowseSwipe(item, decision === 'keep' ? 'right' : 'left')}
                />
              )}
            </AnimatePresence>

            {/* Empty State */}
            {filteredBrowseFeed.length === 0 && !isRecording && (
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center px-8">
                <h2 className="text-3xl font-bold text-white mb-3">No items found</h2>
                <p className="text-lg text-gray-400">
                  {classificationFilter === 'all'
                    ? '50km radius • Try capturing some items!'
                    : `No ${classificationFilter} items nearby`}
                </p>
              </div>
            )}
          </>
        )}

        {/* TAB 2: MAP (shown via overlay, content hidden) */}
        {/* Map is rendered separately as overlay */}

        {/* TAB 3: MY ITEMS - Photo Grid (iPhone-style) */}
        {activeTab === 'myitems' && (
          <div className="w-full h-full overflow-y-auto">
            <PhotoGrid
              items={[...myDrafts, ...myListed]}
              onClick={(item) => {
                // Double-tap detected by PhotoCard - open fullscreen review
                const allMyItems = [...myDrafts, ...myListed];
                const currentIndex = allMyItems.findIndex(i => i.id === item.id);
                const remainingItems = allMyItems.slice(currentIndex + 1);

                setReviewingItem(item);
                setReviewQueue(remainingItems);
              }}
              onDelete={async (item) => {
                // Delete from storage and update state
                URL.revokeObjectURL(item.url);
                await storage.deleteItem(item.id);
                if (item.status === 'draft') {
                  setMyDrafts(prev => prev.filter(i => i.id !== item.id));
                } else {
                  setMyListed(prev => prev.filter(i => i.id !== item.id));
                }
              }}
              onBadgeClick={(item) => {
                // Tap badge to re-classify
                setReclassifyingItem(item);
              }}
              onBadgeLongPress={(item) => {
                // Long-press badge to edit options (discount % or bid duration)
                if (item.classification !== 'free') {
                  setEditingOptionsItem(item);
                }
              }}
            />

            {/* Fullscreen Item Reviewer (triggered by double-tap) */}
            <AnimatePresence>
              {reviewingItem && (
                <ItemReviewer
                  key={reviewingItem.id}
                  item={reviewingItem}
                  onDecision={(item, decision) => {
                    if (decision === 'delete') {
                      // Delete the item
                      if (item.status === 'draft') {
                        setMyDrafts(prev => prev.filter(i => i.id !== item.id));
                      } else {
                        setMyListed(prev => prev.filter(i => i.id !== item.id));
                      }
                    }
                    // Both keep and delete: Show next item in queue
                    if (reviewQueue.length > 0) {
                      const [nextItem, ...rest] = reviewQueue;
                      setReviewingItem(nextItem);
                      setReviewQueue(rest);
                    } else {
                      // No more items - close fullscreen
                      setReviewingItem(null);
                      setReviewQueue([]);
                    }
                  }}
                  onClose={() => {
                    // Double-tap detected - close fullscreen without making a decision
                    setReviewingItem(null);
                    setReviewQueue([]);
                  }}
                />
              )}
            </AnimatePresence>

          </div>
        )}

        {/* TAB 4: CART (items I want from others) */}
        {activeTab === 'cart' && (
          <div className="w-full h-full overflow-y-auto">
            {cart.length === 0 ? (
              <div className="text-center p-8">
                <h2 className="text-3xl font-bold text-white mb-3">Shopping Cart</h2>
                <p className="text-xl text-gray-300 font-semibold mb-2">0 items</p>
                <p className="text-sm text-gray-400 mt-3">Swipe right on browse items to add them here</p>
              </div>
            ) : (
              <PhotoGrid
                items={cart}
                onClick={(item) => {
                  // Double-tap thumbnail → fullscreen with queue
                  console.log('[GotJunk] Cart item clicked:', item.id);
                  const currentIndex = cart.findIndex(i => i.id === item.id);
                  const remainingItems = cart.slice(currentIndex + 1);

                  setReviewingCartItem(item);
                  setCartReviewQueue(remainingItems);
                }}
                onDelete={async (item) => {
                  // Remove from cart
                  setCart(prev => prev.filter(i => i.id !== item.id));
                  // Update status back to browsing so it appears in browse feed again
                  await storage.updateItemStatus(item.id, 'browsing');
                  console.log('[GotJunk] Removed from cart:', item.id);
                }}
                onBadgeClick={(item) => {
                  // Can't re-classify other people's items
                  console.log('[GotJunk] Cannot re-classify cart items (not yours)');
                }}
                onBadgeLongPress={(item) => {
                  // Can't edit options on other people's items
                  console.log('[GotJunk] Cannot edit cart items (not yours)');
                }}
              />
            )}

            {/* Fullscreen Cart Item Reviewer (triggered by double-tap) */}
            <AnimatePresence>
              {reviewingCartItem && (
                <ItemReviewer
                  key={reviewingCartItem.id}
                  item={reviewingCartItem}
                  showForwardButton={true}  // Show > button for purchase
                  onDecision={(item, decision) => {
                    if (decision === 'keep') {
                      // Right swipe in cart → Purchase confirmation
                      console.log('[GotJunk] Opening purchase modal for item:', item.id);
                      setPurchasingItem(item);
                      // Don't advance queue yet - wait for purchase confirmation
                    } else if (decision === 'delete') {
                      // Left swipe in cart → Remove from cart
                      setCart(prev => prev.filter(i => i.id !== item.id));
                      storage.updateItemStatus(item.id, 'browsing');
                      console.log('[GotJunk] Removed from cart:', item.id);

                      // Show next item in queue
                      if (cartReviewQueue.length > 0) {
                        const [nextItem, ...rest] = cartReviewQueue;
                        setReviewingCartItem(nextItem);
                        setCartReviewQueue(rest);
                      } else {
                        // No more items - close fullscreen
                        setReviewingCartItem(null);
                        setCartReviewQueue([]);
                      }
                    }
                  }}
                  onClose={() => {
                    // Swipe up or double-tap → close fullscreen without making a decision
                    setReviewingCartItem(null);
                    setCartReviewQueue([]);
                  }}
                />
              )}
            </AnimatePresence>

          </div>
        )}
      </div>

      {/* Left sidebar navigation - hidden when map is open (map has X button) */}
      {!isMapOpen && (
        <LeftSidebarNav
          activeTab={activeTab}
          onGalleryClick={() => {
            // Always reset SOS detection and clear timeout (same as Map button)
            setTapTimes([]);
            sosDetectionActive.current = false;
            if (tapTimeoutRef.current) clearTimeout(tapTimeoutRef.current);
            // Navigate to Browse
            setActiveTab('browse'); // Tab 1: Browse
            setMapOpen(false); // Close map when switching to Browse
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
            setMapOpen(true); // Open map as overlay
          }}
          onMyItemsClick={() => {
            setActiveTab('myitems'); // Tab 3: My Items
            setMapOpen(false); // Close map when switching to My Items
            console.log('📦 My Items clicked');
          }}
          onCartClick={() => {
            setActiveTab('cart'); // Tab 4: Cart
            setMapOpen(false); // Close map when switching to Cart
            console.log('🛒 Cart clicked');
          }}
          libertyEnabled={libertyEnabled}
        />
      )}

      {/* Bottom navigation bar - visually hidden when map is open (keeps Camera mounted) */}
      <BottomNavBar
        style={{ display: isMapOpen ? 'none' : 'block' }}
          captureMode={captureMode}
          onToggleCaptureMode={() => setCaptureMode(mode => mode === 'photo' ? 'video' : 'photo')}
          onCapture={handleCapture}
          onReviewAction={(action) => {
            if (activeTab === 'browse' && filteredBrowseFeed.length > 0) {
              console.log('[GotJunk] Button action:', action, 'on item:', filteredBrowseFeed[0].id);
              handleBrowseSwipe(filteredBrowseFeed[0], action === 'keep' ? 'right' : 'left');
            } else if (activeTab === 'myitems' && currentReviewItem) {
              handleReviewDecision(currentReviewItem, action);
            }
          }}
          isRecording={isRecording}
          setIsRecording={setIsRecording}
          countdown={countdown}
          setCountdown={setCountdown}
          hasReviewItems={activeTab === 'browse' ? filteredBrowseFeed.length > 0 : myDrafts.length > 0}
          onSearchClick={() => {
            console.log('🔍 Search clicked');
            // TODO: Open search modal
          }}
          showCameraOrb={showCameraOrb}
          autoClassifyEnabled={autoClassifyEnabled}
          onToggleAutoClassify={() => setAutoClassifyEnabled(!autoClassifyEnabled)}
          onLongPressAutoClassify={handleLongPressAutoClassify}
          lastClassification={lastClassification}
        />

      {/* Re-classification Modal (tap badge) */}
      {reclassifyingItem && (
        <ClassificationModal
          isOpen={true}
          imageUrl={reclassifyingItem.url}
          onClassify={(newClassification, discountPercent, bidDurationHours) => handleReclassify(reclassifyingItem, newClassification, discountPercent, bidDurationHours)}
        />
      )}

      {/* Options Modal (long-press badge) */}
      {editingOptionsItem && (
        <OptionsModal
          isOpen={true}
          item={editingOptionsItem}
          onSave={(discountPercent, bidDurationHours) => handleUpdateOptions(editingOptionsItem, discountPercent, bidDurationHours)}
          onClose={() => setEditingOptionsItem(null)}
        />
      )}

      {isGalleryOpen && (
        <FullscreenGallery
          items={myListed}
          onClose={() => setGalleryOpen(false)}
          onDelete={handleDeleteMyItem}
        />
      )}


      {/* Map View */}
      {isMapOpen && (
        <PigeonMapView
          // NEW: Pass raw CapturedItems for clustering with thumbnails
          capturedItems={browseFeed}
          useClustering={true}
          // Legacy: Keep junkItems for backward compatibility (used if clustering disabled)
          junkItems={browseFeed.map(item => ({
            id: item.id,
            location: {
              latitude: item.latitude || userLocation?.latitude || 37.7749,
              longitude: item.longitude || userLocation?.longitude || -122.4194,
            },
            title: item.classification || 'Item',
            imageUrl: item.url || '',
            status: 'available' as const,
            timestamp: item.createdAt || Date.now(),
          }))}
          libertyAlerts={libertyAlerts}
          userLocation={userLocation || null}
          onClose={() => {
            setMapOpen(false); // Close overlay, return to current tab
          }}
          onMarkerClick={(location) => {
            // User clicked cluster marker → filter Browse view to items at that location
            console.log('[GotJunk] Cluster marker clicked:', location);
            setLocationFilter(location);
            setActiveTab('browse'); // Switch to Browse tab showing filtered items
            setMapOpen(false); // Close map
          }}
          showLibertyAlerts={libertyEnabled}
          onLibertyActivate={() => {
            // SOS morse code detected on map → activate Liberty Alerts
            console.log('🗽 Liberty Alert activated via map SOS!');
            setLibertyEnabled(true);
            alert('🗽 Liberty Alert Unlocked via Map SOS!');
          }}
        />
      )}


      {/* Classification Modal */}
      <ClassificationModal
        isOpen={!!pendingClassificationItem}
        imageUrl={pendingClassificationItem?.url || ''}
        onClassify={handleClassify}
      />

      {/* Instructions Modal (shows on Browse tab only - landing page) */}
      <InstructionsModal
        isOpen={showInstructions && activeTab === 'browse'}
        onClose={handleInstructionsClose}
      />

      {/* Purchase Confirmation Modal (Cart items) */}
      <PurchaseModal
        isOpen={!!purchasingItem}
        item={purchasingItem}
        onConfirm={async () => {
          console.log('[GotJunk] Purchase confirmed for item:', purchasingItem?.id);

          // TODO: Integrate with FoundUps wallet (testnet)
          // For now: Remove from cart and delete (purchase complete)
          if (purchasingItem) {
            setCart(prev => prev.filter(i => i.id !== purchasingItem.id));
            await storage.deleteItem(purchasingItem.id);
            console.log('[GotJunk] Item purchased and removed:', purchasingItem.id);
          }

          // Close purchase modal
          setPurchasingItem(null);

          // Advance to next item in queue
          if (cartReviewQueue.length > 0) {
            const [nextItem, ...rest] = cartReviewQueue;
            setReviewingCartItem(nextItem);
            setCartReviewQueue(rest);
          } else {
            // No more items - close fullscreen
            setReviewingCartItem(null);
            setCartReviewQueue([]);
          }
        }}
        onCancel={() => {
          console.log('[GotJunk] Purchase cancelled');
          setPurchasingItem(null);
          // Return to cart thumbnails view (close fullscreen)
          setReviewingCartItem(null);
          setCartReviewQueue([]);
        }}
      />

    </div>
  );
};

export default App;
