"use client";
import { memo, useRef, useEffect } from "react";
import { Room, RoomEvent, Track, RemoteTrack, RemoteTrackPublication, RemoteParticipant } from "livekit-client";

interface Props {
  token: string;
  serverUrl: string;
  isHost: boolean;
}

const LivePlayer = memo(function LivePlayer({ token, serverUrl, isHost }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const roomRef = useRef<Room | null>(null);

  useEffect(() => {
    if (roomRef.current) return; // already connected

    const room = new Room({
      adaptiveStream: true,
      dynacast: true,
    });
    roomRef.current = room;

    function handleTrackSubscribed(track: RemoteTrack, pub: RemoteTrackPublication, participant: RemoteParticipant) {
      if (!containerRef.current) return;
      if (track.kind === Track.Kind.Video) {
        const el = track.attach() as HTMLVideoElement;
        el.style.width = "100%";
        el.style.height = "100%";
        el.style.objectFit = "contain";
        el.autoplay = true;
        (el as HTMLVideoElement).playsInline = true;
        containerRef.current!.innerHTML = "";
        containerRef.current!.appendChild(el);
      } else if (track.kind === Track.Kind.Audio) {
        const el = track.attach();
        document.body.appendChild(el);
      }
    }

    function handleTrackUnsubscribed(track: RemoteTrack) {
      track.detach();
    }

    room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed);
    room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed);

    room.connect(serverUrl, token).then(async () => {
      if (isHost) {
        await room.localParticipant.enableCameraAndMicrophone();
        const videoTrack = room.localParticipant.getTrackPublication(Track.Source.Camera)?.track;
        if (videoTrack && containerRef.current) {
          const el = videoTrack.attach();
          el.style.width = "100%";
          el.style.height = "100%";
          el.style.objectFit = "contain";
          el.autoplay = true;
          (el as HTMLVideoElement).playsInline = true;
          el.muted = true;
          containerRef.current.innerHTML = "";
          containerRef.current.appendChild(el);
        }
      }
    }).catch(console.error);

    // Page Visibility API — notify when host pauses
    function handleVisibility() {
      if (!isHost) return;
      const hidden = document.hidden;
      const msg = hidden
        ? JSON.stringify({ type: "host_paused" })
        : JSON.stringify({ type: "host_resumed" });
      // Send via data channel if connected
      try {
        room.localParticipant.publishData(new TextEncoder().encode(msg), { reliable: true });
      } catch {}
    }
    document.addEventListener("visibilitychange", handleVisibility);

    // Listen for data from host (viewer side)
    room.on(RoomEvent.DataReceived, (payload: Uint8Array) => {
      try {
        const msg = JSON.parse(new TextDecoder().decode(payload));
        const overlay = document.getElementById("host-status-overlay");
        if (overlay) {
          if (msg.type === "host_paused") {
            overlay.style.display = "flex";
          } else if (msg.type === "host_resumed") {
            overlay.style.display = "none";
          }
        }
      } catch {}
    });

    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      room.disconnect();
      roomRef.current = null;
    };
  }, []); // empty deps — only mount once

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <div ref={containerRef} style={{ width: "100%", height: "100%", background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.1em" }}>
          {isHost ? "Starting camera..." : "Waiting for host..."}
        </p>
      </div>
      {/* Host paused overlay */}
      <div id="host-status-overlay" style={{ display: "none", position: "absolute", inset: 0, background: "rgba(0,0,0,0.7)", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: "0.5rem" }}>
        <p style={{ color: "#f0e8d8", fontFamily: "Georgia, serif", fontSize: "1rem" }}>📵 Host has paused their video</p>
        <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem" }}>Stream will resume shortly...</p>
      </div>
    </div>
  );
}, () => true); // never re-render

export default LivePlayer;
