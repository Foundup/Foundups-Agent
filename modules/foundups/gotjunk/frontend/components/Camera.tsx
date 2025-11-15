import React, { useRef, useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { CaptureMode } from '../App';

interface CameraProps {
  onCapture: (blob: Blob) => void;
  captureMode: CaptureMode;
  fullscreen?: boolean; // Fullscreen mode (no circular styling)
}

export interface CameraHandle {
  takePhoto: () => void;
  startRecording: () => void;
  stopRecording: () => void;
}

export const Camera = forwardRef<CameraHandle, CameraProps>(({ onCapture, captureMode, fullscreen = false }, ref) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let activeStream: MediaStream | null = null;

    const getMedia = async () => {
      const constraintsToTry: MediaStreamConstraints[] = [
        // Ideal: back camera with audio
        { video: { facingMode: 'environment' }, audio: true },
        // Fallback 1: any camera with audio
        { video: true, audio: true },
        // Fallback 2: back camera without audio (for devices with no mic)
        { video: { facingMode: 'environment' }, audio: false },
        // Fallback 3: any camera without audio
        { video: true, audio: false },
      ];

      for (const constraints of constraintsToTry) {
        try {
          activeStream = await navigator.mediaDevices.getUserMedia(constraints);
          // If we get a stream, break the loop
          if (activeStream) {
            console.log('Successfully got media stream with constraints:', constraints);
            break;
          }
        } catch (err) {
          console.warn(`Failed to get media with constraints:`, constraints, err);
        }
      }

      if (activeStream) {
        setError(null);
        setStream(activeStream);
        if (videoRef.current) {
          videoRef.current.srcObject = activeStream;

          // Log when video metadata is loaded (stream ready for capture)
          videoRef.current.onloadedmetadata = () => {
            console.log('[Camera] ✅ Video stream ready! Dimensions:', videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight);
          };
        }
      } else {
        console.error("Error accessing any camera or microphone after all fallbacks.");
        setError("No Camera Access");
      }
    };
    
    getMedia();

    return () => {
      // When component unmounts, stop all tracks
      if (activeStream) {
        activeStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  useImperativeHandle(ref, () => ({
    takePhoto: () => {
      console.log('[Camera] takePhoto() called');
      console.log('[Camera] Video dimensions:', videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight);
      console.log('[Camera] Stream ready:', !!stream);

      if (videoRef.current?.videoWidth && videoRef.current?.videoHeight) {
        console.log('[Camera] Creating canvas...');
        const canvas = document.createElement('canvas');
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        const context = canvas.getContext('2d');
        if (context) {
          console.log('[Camera] Drawing image to canvas...');
          context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
          canvas.toBlob(blob => {
            if (blob) {
              console.log('[Camera] ✅ Photo captured! Blob size:', blob.size);
              onCapture(blob);
            } else {
              console.error('[Camera] ❌ Failed to create blob from canvas');
            }
          }, 'image/jpeg', 0.95);
        } else {
          console.error('[Camera] ❌ Failed to get 2D context from canvas');
        }
      } else {
        console.error('[Camera] ❌ Video not ready! Width:', videoRef.current?.videoWidth, 'Height:', videoRef.current?.videoHeight);
        console.error('[Camera] Video element:', videoRef.current);
        console.error('[Camera] Stream:', stream);
      }
    },
    startRecording: () => {
      if (stream && MediaRecorder.isTypeSupported('video/webm')) {
        recordedChunksRef.current = [];
        mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' });
        
        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            recordedChunksRef.current.push(event.data);
          }
        };

        mediaRecorderRef.current.onstop = () => {
          const videoBlob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
          onCapture(videoBlob);
          recordedChunksRef.current = [];
        };
        
        mediaRecorderRef.current.start();
      } else {
        console.error("MediaRecorder not supported or stream not available");
      }
    },
    stopRecording: () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    },
  }));
  
  return (
    <div
      className={fullscreen
        ? "w-full h-full overflow-hidden bg-black flex items-center justify-center"
        : "w-full h-full rounded-full overflow-hidden bg-black flex items-center justify-center border-2 border-white/50"
      }
    >
      {error ? (
        <div className="text-white text-xs text-center p-1">{error}</div>
      ) : (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted // Mute preview to prevent feedback
          className={fullscreen
            ? "w-full h-full object-cover" // Fullscreen: no scaling, cover entire viewport
            : "w-full h-full object-cover scale-[1.9]" // Orb: scaled to fill the circle better
          }
        />
      )}
    </div>
  );
});