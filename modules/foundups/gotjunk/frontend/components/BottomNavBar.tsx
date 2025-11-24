import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LeftArrowIcon } from './icons/LeftArrowIcon';
import { RightArrowIcon } from './icons/RightArrowIcon';
import { CameraIcon } from './icons/CameraIcon';
import { MicIcon } from './icons/MicIcon';
import { ShieldIcon } from './icons/ShieldIcon';
import { useLongPress } from '../hooks/useLongPress';
import { useSOSDetector } from '../hooks/useSOSDetector';
import { Z_LAYERS } from '../constants/zLayers';
import { CaptureMode } from '../App';

interface BottomNavBarProps {
  captureMode: CaptureMode;
  onToggleCaptureMode: () => void;
  onCapture: (blob: Blob) => void;
  onReviewAction: (action: 'keep' | 'delete') => void;
  isRecording: boolean;
  setIsRecording: React.Dispatch<React.SetStateAction<boolean>>;
  countdown: number;
  setCountdown: React.Dispatch<React.SetStateAction<number>>;
  hasReviewItems: boolean;
  onSearchClick?: () => void; // Search functionality
  onCameraClick?: () => void; // Open fullscreen camera
  showCameraOrb?: boolean;
  autoClassifyEnabled?: boolean;
  onToggleAutoClassify?: () => void;
  onLongPressAutoClassify?: () => void; // Long press to select classification
  lastClassification?: { type: string, discountPercent?: number, bidDurationHours?: number } | null;
  libertyUnlocked?: boolean; // Has user triggered SOS easter egg? (only show toggle when true)
  libertyEnabled?: boolean; // Liberty Alert mode (show 🗽 badge on camera)
  onToggleLiberty?: () => void; // Toggle Liberty Alert mode ON/OFF
  onLongPressLibertyBadge?: () => void; // Long press 🗽 badge to select Liberty classification
  lastLibertyClassification?: { type: string, stayLimitNights?: number, alertTimerMinutes?: number, isPermanent?: boolean } | null;
  onVoiceInput?: (transcript: string) => void; // Voice input callback - receives STT result
  onUnlockLiberty?: () => void; // Unlock Liberty Alert (triggered by SOS pattern)
}

const buttonVariants = {
    hover: { scale: 1.05 },
    tap: { scale: 0.95 }
};

export const BottomNavBar: React.FC<BottomNavBarProps> = ({
  captureMode,
  onToggleCaptureMode,
  onCapture,
  onReviewAction,
  isRecording,
  setIsRecording,
  setCountdown,
  hasReviewItems,
  onSearchClick = () => console.log('🔍 Search clicked'),
  onCameraClick = () => console.log('📷 Camera clicked'),
  showCameraOrb = true,
  autoClassifyEnabled = false,
  onToggleAutoClassify = () => console.log('🔄 Auto-classify toggled'),
  onLongPressAutoClassify = () => console.log('🔄 Long-press: Select classification'),
  lastClassification = null,
  libertyUnlocked = false,
  libertyEnabled = false,
  onToggleLiberty = () => console.log('🗽 Liberty toggled'),
  onLongPressLibertyBadge = () => console.log('🗽 Long-press: Select Liberty classification'),
  lastLibertyClassification = null,
  onVoiceInput = (transcript: string) => console.log('🎤 Voice input:', transcript),
  onUnlockLiberty = () => console.log('🗽 Liberty Unlocked!'),
  }) => {
  // Voice input state (Web Speech API - triggers phone's native STT)
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Speech recognition setup
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      console.log('[GotJunk] STT result:', transcript);
      onVoiceInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.log('[GotJunk] STT error:', event.error);
      setIsListening(false);
    };
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    return () => recognitionRef.current?.stop();
  }, [onVoiceInput]);

  const handleMicClick = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.log('[GotJunk] Speech recognition not supported on this device');
      return;
    }
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
        console.log('[GotJunk] STT started - listening...');
      } catch (err) {
        console.log('[GotJunk] Failed to start STT:', err);
      }
    }
  };
  // SOS Pattern Detector (for invisible trigger button)
  const { patternLength: sosPatternLength, handlers: sosHandlers } = useSOSDetector({
    onSOSDetected: onUnlockLiberty,
  });

  // Navigation Bar Layout: [<] [>] ... [📷] [Auto: OFF] [🎤]
  // - Left: Swipe left/right thumb toggles (delete/keep)
  // - Right: Camera icon + Auto toggle + AI MIC (voice interface to DAE system)

  // Long-press handler for auto-classify toggle button (ORIGINAL LOGIC - DO NOT MODIFY)
  const autoClassifyLongPress = useLongPress({
    onLongPress: () => {
      console.log('[GotJunk] Long-press detected on auto-classify toggle');
      onLongPressAutoClassify();
    },
    onTap: () => {
      console.log('[GotJunk] Short tap on auto-classify toggle');
      onToggleAutoClassify();
    },
    threshold: 450, // 450ms to trigger long-press
  });

  // Long-press handler for Liberty toggle button
  const libertyLongPress = useLongPress({
    onLongPress: () => {
      console.log('[GotJunk] Long-press detected on Liberty toggle');
      onLongPressLibertyBadge();
    },
    onTap: () => {
      console.log('[GotJunk] Short tap on Liberty toggle');
      onToggleLiberty();
    },
    threshold: 450, // 450ms to trigger long-press
  });

  return (
    <motion.div
        className="fixed bottom-0 left-0 right-0"
        style={{ zIndex: Z_LAYERS.floatingControls }}
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Main Nav Bar - Layout: [Delete] [Keep] ... [Camera] [Auto] ... [AI MIC] */}
      {/* h-24 on mobile (restored), h-28 on tablets+ */}
      <div
        className="relative flex items-center justify-center w-full h-24 md:h-28 bg-gray-800/80 backdrop-blur-lg border-t border-white/10 max-w-2xl mx-auto rounded-t-2xl shadow-2xl px-4 md:px-6"
        style={{ paddingBottom: 'max(12px, env(safe-area-inset-bottom))' }}
      >

        {/* Left Section: Delete & Keep Arrows - Hidden on phones, visible on tablets+ */}
        <div className="hidden md:flex absolute left-6 items-center gap-6">
            <motion.button
                onClick={() => onReviewAction('delete')}
                aria-label="Delete item"
                className="w-16 h-16 rounded-full flex items-center justify-center transition-colors bg-red-600/50 hover:bg-red-600/70 disabled:opacity-50"
                variants={buttonVariants}
                whileTap="tap"
                disabled={!hasReviewItems || isRecording}
            >
                <LeftArrowIcon className="w-7 h-7 text-white" />
            </motion.button>

            <motion.button
                onClick={() => onReviewAction('keep')}
                aria-label="Keep item"
                className="w-16 h-16 rounded-full flex items-center justify-center transition-colors bg-green-500/50 hover:bg-green-500/70 disabled:opacity-50"
                variants={buttonVariants}
                whileTap="tap"
                disabled={!hasReviewItems || isRecording}
            >
                <RightArrowIcon className="w-7 h-7 text-white" />
            </motion.button>
        </div>

        {/* Center Section: Camera Icon + Auto Toggle - ALWAYS CENTERED */}
        <div className="flex items-center gap-3 md:gap-4">
          {/* SOS Trigger Button - INVISIBLE until pattern entry begins */}
          <motion.button
            {...sosHandlers}
            className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center transition-all ${
              sosPatternLength > 0
                ? 'bg-red-500/20 animate-pulse border border-red-400/30' // Only visible during pattern entry
                : 'bg-transparent border-transparent' // Completely invisible by default
            }`}
            variants={buttonVariants}
            whileTap="tap"
            aria-label="Menu"
          >
            <ShieldIcon className={`w-4 h-4 md:w-5 md:h-5 transition-opacity ${
              sosPatternLength > 0 ? 'text-red-400 opacity-100' : 'opacity-0' // Hidden until active
            }`} />
          </motion.button>

          {/* Camera Icon - Matches sidebar style */}
          <motion.button
            onClick={onCameraClick}
            className="w-14 h-14 md:w-16 md:h-16 rounded-2xl bg-gray-800/90 hover:bg-gray-700/90 border-2 border-gray-600 backdrop-blur-md shadow-xl flex items-center justify-center transition-all"
            variants={buttonVariants}
            whileTap="tap"
            aria-label="Toggle camera"
          >
            <CameraIcon className="w-5 h-5 md:w-6 md:h-6 text-white" />
          </motion.button>

         {/* Auto-Classify Toggle Button - Oval shaped (more horizontal padding) */}
         <motion.button
           {...autoClassifyLongPress}
           className={`px-4 py-1.5 md:px-5 md:py-2 rounded-full shadow-lg font-semibold text-xs md:text-sm transition-all ${
             autoClassifyEnabled
               ? lastClassification?.type === 'free'
                 ? 'bg-blue-600 text-white'      // Free = Blue
                 : lastClassification?.type === 'discount'
                 ? 'bg-green-600 text-white'     // Discount = Green
                 : lastClassification?.type === 'bid'
                 ? 'bg-amber-600 text-white'     // Bid = Amber
                 : 'bg-green-600 text-white'     // Fallback = Green
               : 'bg-red-500/60 text-white'      // OFF = Softer red
           }`}
           variants={buttonVariants}
           whileHover="hover"
           whileTap="tap"
           aria-label={autoClassifyEnabled ? `Auto-classify: ${lastClassification?.type || 'ON'}` : 'Auto-classify: OFF (long-press to select)'}
         >
           <div className="flex items-center gap-2">
             <div className={`w-2 h-2 rounded-full ${autoClassifyEnabled ? 'bg-white' : 'bg-white/70'}`} />
             <span>
               {autoClassifyEnabled ? 'ON' : 'OFF'}
             </span>
           </div>
           {autoClassifyEnabled && lastClassification && (
             <div className="text-[10px] md:text-xs opacity-90 mt-0.5">
               {lastClassification.type === 'discount' && `${lastClassification.discountPercent || 75}%`}
               {lastClassification.type === 'bid' && `${lastClassification.bidDurationHours || 48}h`}
               {lastClassification.type === 'free' && 'FREE'}
             </div>
           )}
         </motion.button>

         {/* Liberty Toggle Button - Only visible after SOS easter egg unlock */}
         {libertyUnlocked && (
           <motion.button
             {...libertyLongPress}
             className={`px-4 py-2 md:px-5 md:py-2.5 rounded-full shadow-lg font-semibold text-sm md:text-base transition-all ${
               libertyEnabled
                 ? lastLibertyClassification?.type === 'ice' || lastLibertyClassification?.type === 'police'
                   ? 'bg-red-600 text-white'       // Alert = Red
                   : lastLibertyClassification?.type === 'couch' || lastLibertyClassification?.type === 'camping'
                   ? 'bg-purple-600 text-white'    // Mutual Aid = Purple
                   : 'bg-blue-600 text-white'      // Default ON = Blue
                 : 'bg-gray-600/60 text-white/70'  // OFF = Gray
             }`}
             variants={buttonVariants}
             whileHover="hover"
             whileTap="tap"
             aria-label={libertyEnabled ? `Liberty: ${lastLibertyClassification?.type || 'ON'}` : 'Liberty: OFF (long-press to select)'}
           >
             <div className="flex items-center gap-1.5">
               <span className="text-lg md:text-xl">🗽</span>
               <span>
                 {libertyEnabled ? 'ON' : 'OFF'}
               </span>
             </div>
             {libertyEnabled && lastLibertyClassification && (
               <div className="text-xs md:text-sm opacity-90 mt-0.5">
                 {lastLibertyClassification.type === 'ice' && '❄️ ICE'}
                 {lastLibertyClassification.type === 'police' && '🚔 POLICE'}
                 {lastLibertyClassification.type === 'couch' && '🛋️ COUCH'}
                 {lastLibertyClassification.type === 'camping' && '⛺ CAMP'}
               </div>
             )}
           </motion.button>
         )}
        </div>

        {/* Right Section: Voice Input MIC - Matches sidebar style */}
        <div className="absolute right-4 md:right-6 flex items-center">
          {/* Voice MIC - Triggers phone's native STT via Web Speech API */}
          <motion.button
            onClick={handleMicClick}
            className={`w-14 h-14 md:w-16 md:h-16 rounded-2xl backdrop-blur-md shadow-xl flex items-center justify-center transition-all ${
              isListening
                ? 'bg-red-500/90 border-2 border-red-400 animate-pulse'
                : 'bg-gray-800/90 hover:bg-gray-700/90 border-2 border-gray-600'
            }`}
            variants={buttonVariants}
            whileTap="tap"
            aria-label={isListening ? 'Stop listening' : 'Voice input'}
          >
            <MicIcon className="w-5 h-5 md:w-6 md:h-6 text-white" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};
